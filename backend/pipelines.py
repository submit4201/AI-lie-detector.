# backend/pipelines.py
import asyncio
import logging
from typing import Dict, Any, Optional, List

# Import Pydantic models
from backend.models import (
    ManipulationAssessment, ArgumentAnalysis, SpeakerAttitude, EnhancedUnderstanding,
    PsychologicalAnalysis, AudioAnalysis as TextAudioAnalysisModel, # Renamed to avoid confusion with audio files
    QuantitativeMetrics, ConversationFlow, EmotionDetail, AudioQualityMetrics
)

# Import DSPy-powered services
from backend.services.core_dspy_services import dspy_transcribe_audio, dspy_analyze_emotions_audio
from backend.services.manipulation_service import ManipulationService
from backend.services.argument_service import ArgumentService
from backend.services.speaker_attitude_service import SpeakerAttitudeService
from backend.services.enhanced_understanding_service import EnhancedUnderstandingService
from backend.services.psychological_service import PsychologicalService
from backend.services.audio_analysis_service import AudioAnalysisService as TextAudioAnalysisService # For text-inferred audio features
from backend.services.quantitative_metrics_service import QuantitativeMetricsService
from backend.services.conversation_flow_service import ConversationFlowService

# Import other necessary services
from backend.services.audio_service import assess_audio_quality # For actual audio quality
# from backend.services.linguistic_service import analyze_linguistic_patterns # Assuming this is still non-DSPy or to be refactored later
from backend.services.gemini_service import GeminiService # To ensure DSPy LM is configured
import dspy # Required for dspy.settings.lm check

logger = logging.getLogger(__name__)

async def full_audio_analysis_pipeline_dspy(
    audio_path: str,
    session_id: str, # Added for context if needed by services
    session_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Orchestrates the full audio analysis using DSPy-powered services.
    Returns a dictionary ready to be parsed by AnalyzeResponse.
    """
    # Ensure DSPy LM is configured by instantiating GeminiService
    # This should ideally be done once at app startup.
    gs_instance = GeminiService() # Triggers DSPy LM config if not already done

    lm_configured = False
    try:
        if dspy.settings.lm:
            lm_configured = True
    except AttributeError:
        pass # lm is not configured

    if not lm_configured:
        logger.error("DSPy LM not configured in pipeline after GeminiService init. Analysis will be limited.")
        # Services have fallbacks, but this indicates a potential setup issue.

    if session_context is None:
        session_context = {}

    # Add session_id to session_context if not already present
    session_context['session_id'] = session_id

    results: Dict[str, Any] = {"transcript": "Transcription failed."} # Default transcript

    # 1. Transcription
    try:
        transcript_text = await dspy_transcribe_audio(audio_path)
        results["transcript"] = transcript_text
        logger.info(f"Pipeline: Transcription complete for {audio_path}")
    except Exception as e:
        logger.error(f"Pipeline: Transcription failed for {audio_path}: {e}", exc_info=True)
        transcript_text = results["transcript"] # Use default if failed

    # 2. Actual Audio Quality Assessment (non-DSPy, uses audio file)
    try:
        from pydub import AudioSegment as PydubAudioSegment # Local import
        audio_segment_pydub = await asyncio.to_thread(PydubAudioSegment.from_file, audio_path)
        results["audio_quality_metrics"] = assess_audio_quality(audio_segment_pydub) # field name in AnalyzeResponse
        logger.info(f"Pipeline: Audio quality assessment complete for {audio_path}")
    except Exception as e:
        logger.error(f"Pipeline: Audio quality assessment failed for {audio_path}: {e}", exc_info=True)
        results["audio_quality_metrics"] = AudioQualityMetrics() # Default

    # Initialize services (they ensure GeminiService/DSPy LM is configured)
    manip_service = ManipulationService()
    arg_service = ArgumentService()
    att_service = SpeakerAttitudeService()
    enh_service = EnhancedUnderstandingService()
    psy_service = PsychologicalService()
    txt_audio_service = TextAudioAnalysisService() # Text-inferred audio features
    qnt_service = QuantitativeMetricsService()
    flow_service = ConversationFlowService()

    # Prepare tasks for concurrent execution
    analysis_tasks_map: Dict[str, Any] = {} # Use a dict to map keys to tasks for clarity

    # 3. Emotion Analysis (DSPy, uses audio + transcript)
    analysis_tasks_map["emotion_analysis"] = dspy_analyze_emotions_audio(audio_path, transcript_text)

    # Modular services (mostly text-based, using DSPy)
    analysis_tasks_map["manipulation_assessment"] = manip_service.analyze(transcript_text, session_context)
    analysis_tasks_map["argument_analysis"] = arg_service.analyze(transcript_text, session_context)
    analysis_tasks_map["speaker_attitude"] = att_service.analyze(transcript_text, session_context)
    analysis_tasks_map["enhanced_understanding"] = enh_service.analyze(transcript_text, session_context)
    analysis_tasks_map["psychological_analysis"] = psy_service.analyze(transcript_text, session_context)
    # Text-inferred audio features (DSPy)
    # The TextAudioAnalysisService's analyze method expects 'text' and 'session_context'
    analysis_tasks_map["audio_analysis_text_inferred"] = txt_audio_service.analyze(text=transcript_text, session_context=session_context)

    # Quantitative Metrics (DSPy)
    # The service's analyze method expects text, speaker_diarization, sentiment_trend_data_input
    # The DSPy module for it packs speaker_diarization and sentiment_trend into session_context for the predictor
    # We will pass session_context directly, assuming it might contain these keys if available from other sources.
    # Or, if these are specific inputs to this pipeline function, they should be passed here.
    # For now, assuming they might be in the general session_context.
    analysis_tasks_map["quantitative_metrics"] = qnt_service.analyze(
        text=transcript_text,
        speaker_diarization=session_context.get('speaker_diarization'), # Pass if available in context
        sentiment_trend_data_input=session_context.get('sentiment_trend_data') # Pass if available
    )

    # Conversation Flow (DSPy)
    analysis_tasks_map["conversation_flow"] = flow_service.analyze(
        text=transcript_text,
        dialogue_acts=session_context.get('dialogue_acts'), # Pass if available
        speaker_diarization=session_context.get('speaker_diarization') # Pass if available
    )

    # Linguistic Analysis (non-DSPy for now, assuming it's synchronous)
    # from backend.services.linguistic_service import analyze_linguistic_patterns # Local import if used
    # analysis_tasks_map["linguistic_analysis"] = asyncio.to_thread(analyze_linguistic_patterns, transcript_text)

    # Run tasks concurrently
    task_keys = list(analysis_tasks_map.keys())
    task_coroutines = list(analysis_tasks_map.values())

    # Gather results
    gathered_task_results = await asyncio.gather(*task_coroutines, return_exceptions=True)

    # Assign results and handle potential errors
    default_models = {
        "emotion_analysis": [], "manipulation_assessment": ManipulationAssessment(),
        "argument_analysis": ArgumentAnalysis(), "speaker_attitude": SpeakerAttitude(),
        "enhanced_understanding": EnhancedUnderstanding(), "psychological_analysis": PsychologicalAnalysis(),
        "audio_analysis_text_inferred": TextAudioAnalysisModel(), "quantitative_metrics": QuantitativeMetrics(),
        "conversation_flow": ConversationFlow(),
        # "linguistic_analysis": {}
    }

    for i, key in enumerate(task_keys):
        result_item = gathered_task_results[i]
        if isinstance(result_item, Exception):
            logger.error(f"Pipeline: Error in analysis task '{key}': {result_item}", exc_info=result_item)
            results[key] = default_models.get(key) # Assign default on error
        else:
            results[key] = result_item

    # Ensure all expected keys for AnalyzeResponse are present, even if from defaults
    for key, default_val in default_models.items():
        if key not in results:
            results[key] = default_val

    # Mapping to AnalyzeResponse fields (example, adjust as per AnalyzeResponse definition)
    # The 'results' dict should now have keys that mostly match AnalyzeResponse fields.
    # Some keys might need renaming or specific handling before passing to AnalyzeResponse.
    # For example, 'audio_analysis_text_inferred' vs 'audio_analysis' in AnalyzeResponse.
    # And 'audio_quality_metrics' vs 'audio_quality'.

    # This pipeline returns a dictionary. The route handler will create AnalyzeResponse.
    # Ensure keys match what AnalyzeResponse expects, or transform them in the route.
    # 'audio_analysis' in AnalyzeResponse is TextAudioAnalysisModel (text-inferred)
    # 'audio_quality_metrics' in AnalyzeResponse is AudioQualityMetrics (actual audio)

    # Rename for clarity if AnalyzeResponse expects 'audio_analysis' for text-inferred
    if "audio_analysis_text_inferred" in results:
        results["audio_analysis"] = results.pop("audio_analysis_text_inferred")

    logger.info(f"Full DSPy audio analysis pipeline completed for session {session_id}, audio {audio_path}")
    return results
