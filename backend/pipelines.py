# backend/pipelines.py
import asyncio
import logging
from typing import Dict, Any, Optional, List

# Import Pydantic models
from backend.models import (
    ManipulationAssessment, ArgumentAnalysis, SpeakerAttitude, EnhancedUnderstanding,
    PsychologicalAnalysis, AudioAnalysis as TextAudioAnalysisModel,
    QuantitativeMetrics, ConversationFlow, EmotionDetail, AudioQualityMetrics, SpeakerIntent # Added SpeakerIntent
)

# Import DSPy-powered services
from backend.services.core_dspy_services import dspy_transcribe_audio, dspy_analyze_emotions_audio
from backend.services.manipulation_service import ManipulationService
from backend.services.argument_service import ArgumentService
from backend.services.speaker_attitude_service import SpeakerAttitudeService
from backend.services.enhanced_understanding_service import EnhancedUnderstandingService
from backend.services.psychological_service import PsychologicalService
from backend.services.audio_analysis_service import AudioAnalysisService as TextAudioAnalysisService
from backend.services.quantitative_metrics_service import QuantitativeMetricsService
from backend.services.conversation_flow_service import ConversationFlowService
from backend.services.speaker_intent_service import SpeakerIntentService # Added for Speaker Intent


# Import other necessary services
from backend.services.audio_service import assess_audio_quality
# from backend.services.linguistic_service import analyze_linguistic_patterns
from backend.services.gemini_service import GeminiService
import dspy

logger = logging.getLogger(__name__)

async def full_audio_analysis_pipeline_dspy(
    audio_path: str,
    session_id: str,
    session_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    gs_instance = GeminiService()

    lm_configured = False
    try:
        if dspy.settings.lm:
            lm_configured = True
    except AttributeError:
        pass

    if not lm_configured:
        logger.error("DSPy LM not configured in pipeline after GeminiService init. Analysis will be limited.")

    if session_context is None:
        session_context = {}

    session_context['session_id'] = session_id

    results: Dict[str, Any] = {"transcript": "Transcription failed."}

    try:
        transcript_text = await dspy_transcribe_audio(audio_path)
        results["transcript"] = transcript_text
        logger.info(f"Pipeline: Transcription complete for {audio_path}")
    except Exception as e:
        logger.error(f"Pipeline: Transcription failed for {audio_path}: {e}", exc_info=True)
        transcript_text = results["transcript"]

    try:
        from pydub import AudioSegment as PydubAudioSegment
        audio_segment_pydub = await asyncio.to_thread(PydubAudioSegment.from_file, audio_path)
        results["audio_quality_metrics"] = assess_audio_quality(audio_segment_pydub)
        logger.info(f"Pipeline: Audio quality assessment complete for {audio_path}")
    except Exception as e:
        logger.error(f"Pipeline: Audio quality assessment failed for {audio_path}: {e}", exc_info=True)
        results["audio_quality_metrics"] = AudioQualityMetrics()

    manip_service = ManipulationService()
    arg_service = ArgumentService()
    att_service = SpeakerAttitudeService()
    enh_service = EnhancedUnderstandingService()
    psy_service = PsychologicalService()
    txt_audio_service = TextAudioAnalysisService()
    qnt_service = QuantitativeMetricsService()
    flow_service = ConversationFlowService()
    intent_service = SpeakerIntentService() # Instantiate new service

    analysis_tasks_map: Dict[str, Any] = {}

    analysis_tasks_map["emotion_analysis"] = dspy_analyze_emotions_audio(audio_path, transcript_text)
    analysis_tasks_map["manipulation_assessment"] = manip_service.analyze(transcript_text, session_context)
    analysis_tasks_map["argument_analysis"] = arg_service.analyze(transcript_text, session_context)
    analysis_tasks_map["speaker_attitude"] = att_service.analyze(transcript_text, session_context)
    analysis_tasks_map["enhanced_understanding"] = enh_service.analyze(transcript_text, session_context)
    analysis_tasks_map["psychological_analysis"] = psy_service.analyze(transcript_text, session_context)
    analysis_tasks_map["speaker_intent"] = intent_service.analyze(transcript_text, session_context) # Add new task
    analysis_tasks_map["audio_analysis_text_inferred"] = txt_audio_service.analyze(text=transcript_text, session_context=session_context)
    analysis_tasks_map["quantitative_metrics"] = qnt_service.analyze(
        text=transcript_text,
        speaker_diarization=session_context.get('speaker_diarization'),
        sentiment_trend_data_input=session_context.get('sentiment_trend_data')
    )
    analysis_tasks_map["conversation_flow"] = flow_service.analyze(
        text=transcript_text,
        dialogue_acts=session_context.get('dialogue_acts'),
        speaker_diarization=session_context.get('speaker_diarization')
    )

    task_keys = list(analysis_tasks_map.keys())
    task_coroutines = list(analysis_tasks_map.values())
    gathered_task_results = await asyncio.gather(*task_coroutines, return_exceptions=True)

    default_models = {
        "emotion_analysis": [], "manipulation_assessment": ManipulationAssessment(),
        "argument_analysis": ArgumentAnalysis(), "speaker_attitude": SpeakerAttitude(),
        "enhanced_understanding": EnhancedUnderstanding(), "psychological_analysis": PsychologicalAnalysis(),
        "speaker_intent": SpeakerIntent(), # Add default for new model
        "audio_analysis_text_inferred": TextAudioAnalysisModel(), "quantitative_metrics": QuantitativeMetrics(),
        "conversation_flow": ConversationFlow(),
    }

    for i, key in enumerate(task_keys):
        result_item = gathered_task_results[i]
        if isinstance(result_item, Exception):
            logger.error(f"Pipeline: Error in analysis task '{key}': {result_item}", exc_info=result_item)
            results[key] = default_models.get(key)
        else:
            results[key] = result_item

    for key, default_val in default_models.items():
        if key not in results:
            results[key] = default_val

    if "audio_analysis_text_inferred" in results:
        results["audio_analysis"] = results.pop("audio_analysis_text_inferred")

    logger.info(f"Full DSPy audio analysis pipeline completed for session {session_id}, audio {audio_path}")
    return results
