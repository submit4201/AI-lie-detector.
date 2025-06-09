from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import tempfile
import os
import logging
import asyncio
from typing import Optional, Dict, Any, List # Added List

from backend.models import (
    AnalyzeResponse, ErrorResponse, AudioQualityMetrics,
    ManipulationAssessment, ArgumentAnalysis, SpeakerAttitude, EnhancedUnderstanding,
    PsychologicalAnalysis, TextAudioAnalysisModel, QuantitativeMetrics,
    ConversationFlow, EmotionDetail, LinguisticAnalysisModel, SessionInsights # Added SessionInsights
)
from backend.services.audio_service import assess_audio_quality
from backend.pipelines import full_audio_analysis_pipeline_dspy # New DSPy pipeline
from backend.services.session_service import conversation_history_service
from backend.services.session_insights_service import SessionInsightsGenerator
from backend.services.streaming_service import analysis_streamer, stream_analysis_pipeline # Keep for streaming route

# Import DSPy-powered services for /analyze_text route
from backend.services.manipulation_service import ManipulationService
from backend.services.argument_service import ArgumentService
from backend.services.speaker_attitude_service import SpeakerAttitudeService
from backend.services.enhanced_understanding_service import EnhancedUnderstandingService
from backend.services.psychological_service import PsychologicalService
from backend.services.audio_analysis_service import AudioAnalysisService as TextAudioAnalysisService
from backend.services.quantitative_metrics_service import QuantitativeMetricsService
from backend.services.conversation_flow_service import ConversationFlowService
# from backend.services.linguistic_service import analyze_linguistic_patterns # Linguistic analysis is part of pipeline_output now if used
from backend.services.gemini_service import GeminiService # To ensure DSPy LM is configured
import dspy # For DSPy settings check

logger = logging.getLogger(__name__)
router = APIRouter()

session_insights_generator = SessionInsightsGenerator()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time analysis updates"""
    await analysis_streamer.connect(websocket, session_id)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        analysis_streamer.disconnect(session_id)

@router.post(
    "/analyze/stream",
    tags=["Analysis"],
    summary="Stream Audio Analysis",
)
async def stream_analyze_audio(
    audio: UploadFile = File(..., description="Audio file to be analyzed"),
    session_id_form: Optional[str] = Form(None, alias="session_id")
):
    temp_audio_path: Optional[str] = None # Define to ensure it's available in finally
    try:
        current_session_id = conversation_history_service.get_or_create_session(session_id_form)
        logger.info(f"Starting streaming analysis for session: {current_session_id}")
        
        valid_audio_types = ['audio/', 'video/']
        valid_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.webm', '.flac']
        
        is_valid_content_type = (audio.content_type and 
                               any(audio.content_type.startswith(t) for t in valid_audio_types))
        is_valid_extension = (audio.filename and 
                            any(audio.filename.lower().endswith(ext) for ext in valid_extensions))
        
        if not (is_valid_content_type or is_valid_extension):
            raise HTTPException(status_code=422, detail="Invalid audio file type")

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename or ".wav")[1]) as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_audio_path = temp_file.name
        
        return StreamingResponse(
            stream_analysis_pipeline(temp_audio_path, current_session_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache", "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        logger.error(f"Error in streaming analysis: {e}", exc_info=True)
        if temp_audio_path and os.path.exists(temp_audio_path):
            try: os.unlink(temp_audio_path)
            except Exception as unlink_e: logger.error(f"Error unlinking temp file: {unlink_e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    tags=["Analysis"],
    summary="Analyze Audio File (DSPy Pipeline)",
    description="Uploads an audio file and performs a comprehensive analysis using DSPy-powered services.",
    responses={
        200: {"description": "Successful analysis"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
        413: {"model": ErrorResponse, "description": "File too large."},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def analyze_audio_route_dspy(
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, etc.). Max 15MB."),
    session_id_form: Optional[str] = Form(None, alias="session_id")
):
    temp_audio_path: Optional[str] = None
    try:
        current_session_id = conversation_history_service.get_or_create_session(session_id_form)
        logger.info(f"Starting DSPy analysis for session: {current_session_id}, file: {audio.filename}")

        valid_audio_types = ['audio/', 'video/']
        valid_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.webm', '.flac']
        
        is_valid_content_type = (audio.content_type and 
                               any(audio.content_type.startswith(t) for t in valid_audio_types))
        is_valid_extension = (audio.filename and 
                            any(audio.filename.lower().endswith(ext) for ext in valid_extensions))
        
        if not (is_valid_content_type or is_valid_extension):
            logger.warning(f"Invalid file type for {audio.filename}: {audio.content_type}")
            raise HTTPException(status_code=400, detail="File must be a valid audio format.")

        audio_content = await audio.read()
        file_size = len(audio_content)
        MAX_FILE_SIZE = 15 * 1024 * 1024
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File size {file_size} exceeds limit for {audio.filename}.")
            raise HTTPException(status_code=413, detail=f"File too large. Max size {MAX_FILE_SIZE // (1024*1024)}MB.")

        suffix = os.path.splitext(audio.filename or "")[1] if audio.filename and os.path.splitext(audio.filename)[1] else ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio_file:
            temp_audio_file.write(audio_content)
            temp_audio_path = temp_audio_file.name
        del audio_content

        session_context_data = conversation_history_service.get_session_context(current_session_id)

        logger.info(f"Calling full_audio_analysis_pipeline_dspy for: {temp_audio_path}")
        pipeline_output = await full_audio_analysis_pipeline_dspy(
            audio_path=temp_audio_path,
            session_id=current_session_id,
            session_context=session_context_data
        )
        logger.info(f"DSPy pipeline analysis completed for {temp_audio_path}.")

        final_result_data: Dict[str, Any] = {
            "session_id": current_session_id,
            "speaker_name": "Speaker 1",
            **pipeline_output
        }

        if session_context_data.get("previous_analyses", 0) > 0:
            session_history = conversation_history_service.get_session_history(current_session_id)
            session_insights = session_insights_generator.generate_session_insights(
                session_context_data,
                pipeline_output,
                session_history
            )
            if session_insights:
                final_result_data['session_insights'] = session_insights

        if 'session_insights' not in final_result_data:
            final_result_data['session_insights'] = SessionInsights()

        if 'linguistic_analysis' not in final_result_data:
             final_result_data['linguistic_analysis'] = LinguisticAnalysisModel()


        conversation_history_service.add_analysis(current_session_id, final_result_data.get("transcript",""), final_result_data)
        logger.info(f"Analysis for session {current_session_id} (DSPy) completed. Returning AnalyzeResponse.")
        # Ensure all fields for AnalyzeResponse are present before creation
        # This is a simplified check; ideally, ensure each field from AnalyzeResponse.__fields__ exists
        for key in AnalyzeResponse.__annotations__.keys():
            if key not in final_result_data:
                logger.warning(f"Field '{key}' missing in final_result_data for AnalyzeResponse. Setting default based on type.")
                # Set a sensible default based on type hint if possible, or use a generic default
                # This part might need more robust default handling if pipeline_output can be sparse
                if AnalyzeResponse.__annotations__[key] == Optional[str] or AnalyzeResponse.__annotations__[key] == str :
                     final_result_data[key] = ""
                elif AnalyzeResponse.__annotations__[key] == List[EmotionDetail]:
                     final_result_data[key] = []
                elif hasattr(AnalyzeResponse.__annotations__[key], '__call__') and not isinstance(AnalyzeResponse.__annotations__[key], type(Optional)): # Check if it's a class we can call
                    try:
                        final_result_data[key] = AnalyzeResponse.__annotations__[key]() # Call Pydantic model for default
                    except:
                        final_result_data[key] = None # Fallback for complex types
                else:
                    final_result_data[key] = None


        return AnalyzeResponse(**final_result_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /analyze (DSPy) for {audio.filename if audio else 'N/A'}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            try: os.unlink(temp_audio_path)
            except Exception as e_unlink: logger.error(f"Error deleting temp file {temp_audio_path}: {e_unlink}")


@router.post(
    "/analyze_text",
    response_model=AnalyzeResponse,
    tags=["Analysis"],
    summary="Analyze Text Input (DSPy Services)",
    description="Analyzes text input using DSPy-powered services for manipulation, arguments, etc."
)
async def analyze_text_input_dspy(
    request_data: Dict[str, Any],
    session_id_form: Optional[str] = Form(None, alias="session_id")
):
    try:
        text = request_data.get("text", "")
        speaker_name = request_data.get("speaker_name", "Speaker")
        
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text must be at least 10 characters long.")
        
        current_session_id = conversation_history_service.get_or_create_session(session_id_form)
        session_context_data = conversation_history_service.get_session_context(current_session_id)
        session_context_data['session_id'] = current_session_id

        gs_instance = GeminiService()
        lm_configured = False
        try:
            if dspy.settings.lm: lm_configured = True
        except AttributeError: pass
        if not lm_configured:
            logger.error("DSPy LM not configured in /analyze_text. Analysis will use fallbacks.")

        manip_service = ManipulationService()
        arg_service = ArgumentService()
        att_service = SpeakerAttitudeService()
        enh_service = EnhancedUnderstandingService()
        psy_service = PsychologicalService()
        txt_audio_service = TextAudioAnalysisService()
        qnt_service = QuantitativeMetricsService()
        flow_service = ConversationFlowService()

        analysis_tasks_map: Dict[str, Any] = {}
        analysis_tasks_map["manipulation_assessment"] = manip_service.analyze(text, session_context_data)
        analysis_tasks_map["argument_analysis"] = arg_service.analyze(text, session_context_data)
        analysis_tasks_map["speaker_attitude"] = att_service.analyze(text, session_context_data)
        analysis_tasks_map["enhanced_understanding"] = enh_service.analyze(text, session_context_data)
        analysis_tasks_map["psychological_analysis"] = psy_service.analyze(text, session_context_data)
        analysis_tasks_map["audio_analysis"] = txt_audio_service.analyze(text=text, session_context=session_context_data)
        analysis_tasks_map["quantitative_metrics"] = qnt_service.analyze(text=text, session_context=session_context_data)
        analysis_tasks_map["conversation_flow"] = flow_service.analyze(text=text, session_context=session_context_data)
        
        from backend.services.linguistic_service import analyze_linguistic_patterns # Local import
        analysis_tasks_map["linguistic_analysis"] = asyncio.to_thread(analyze_linguistic_patterns, text)


        task_keys = list(analysis_tasks_map.keys())
        task_coroutines = list(analysis_tasks_map.values())
        gathered_task_results = await asyncio.gather(*task_coroutines, return_exceptions=True)

        pipeline_output: Dict[str, Any] = {}
        default_models = {
            "manipulation_assessment": ManipulationAssessment(), "argument_analysis": ArgumentAnalysis(),
            "speaker_attitude": SpeakerAttitude(), "enhanced_understanding": EnhancedUnderstanding(),
            "psychological_analysis": PsychologicalAnalysis(), "audio_analysis": TextAudioAnalysisModel(),
            "quantitative_metrics": QuantitativeMetrics(word_count=len(text.split())),
            "conversation_flow": ConversationFlow(), "linguistic_analysis": LinguisticAnalysisModel()
        }
        for i, key in enumerate(task_keys):
            result_item = gathered_task_results[i]
            if isinstance(result_item, Exception):
                logger.error(f"Text Analysis Pipeline: Error in task '{key}': {result_item}", exc_info=result_item)
                pipeline_output[key] = default_models.get(key)
            else:
                pipeline_output[key] = result_item

        for key, default_val in default_models.items():
            if key not in pipeline_output: pipeline_output[key] = default_val

        final_result_data: Dict[str, Any] = {
            "session_id": current_session_id,
            "speaker_name": speaker_name,
            "transcript": text,
            "audio_quality_metrics": AudioQualityMetrics(),
            "emotion_analysis": [],
            **pipeline_output
        }
        
        if session_context_data.get("previous_analyses", 0) > 0:
            session_history = conversation_history_service.get_session_history(current_session_id)
            session_insights = session_insights_generator.generate_session_insights(
                session_context_data, pipeline_output, session_history
            )
            if session_insights: final_result_data['session_insights'] = session_insights
        
        if 'session_insights' not in final_result_data:
            final_result_data['session_insights'] = SessionInsights()

        # Ensure all fields for AnalyzeResponse are present before creation
        for key in AnalyzeResponse.__annotations__.keys():
            if key not in final_result_data:
                 logger.warning(f"Field '{key}' missing in final_result_data for /analyze_text. Setting default.")
                 if AnalyzeResponse.__annotations__[key] == Optional[str] or AnalyzeResponse.__annotations__[key] == str :
                     final_result_data[key] = ""
                 elif AnalyzeResponse.__annotations__[key] == List[EmotionDetail]:
                     final_result_data[key] = []
                 elif hasattr(AnalyzeResponse.__annotations__[key], '__call__') and not isinstance(AnalyzeResponse.__annotations__[key], type(Optional)):
                    try: final_result_data[key] = AnalyzeResponse.__annotations__[key]()
                    except: final_result_data[key] = None
                 else: final_result_data[key] = None

        conversation_history_service.add_analysis(current_session_id, text, final_result_data)
        logger.info(f"Text analysis (DSPy) for session {current_session_id} completed.")
        return AnalyzeResponse(**final_result_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in text analysis (DSPy): {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

```
