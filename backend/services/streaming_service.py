import json
import asyncio
import logging
from typing import Dict, Any, Optional, AsyncGenerator, List # Added List
from fastapi import WebSocket
import os

# Import services and models needed for the new pipeline
from backend.services.gemini_service import GeminiService # For DSPy LM config trigger
from backend.services.core_dspy_services import dspy_transcribe_audio, dspy_analyze_emotions_audio # New DSPy services
from backend.services.audio_service import assess_audio_quality
# from backend.services.linguistic_service import analyze_linguistic_patterns # Assuming it's called if needed

from backend.services.manipulation_service import ManipulationService
from backend.services.argument_service import ArgumentService
from backend.services.speaker_attitude_service import SpeakerAttitudeService
from backend.services.enhanced_understanding_service import EnhancedUnderstandingService
from backend.services.psychological_service import PsychologicalService
from backend.services.audio_analysis_service import AudioAnalysisService as ModularAudioAnalysisService
from backend.services.quantitative_metrics_service import QuantitativeMetricsService
from backend.services.conversation_flow_service import ConversationFlowService
# Import Pydantic models for type hints if returning them directly (though SSE sends dicts)
from backend.models import AudioQualityMetrics, EmotionDetail

logger = logging.getLogger(__name__)

class AnalysisStreamer:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected for session {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected for session {session_id}")
    
    async def send_analysis_update(self, session_id: str, analysis_type: str, data: Any):
        if session_id in self.active_connections:
            try:
                if hasattr(data, 'model_dump') and callable(data.model_dump): # Pydantic v2
                    payload_data = data.model_dump()
                elif hasattr(data, 'dict') and callable(data.dict): # Pydantic v1
                    payload_data = data.dict()
                else:
                    payload_data = data

                message = {"type": "analysis_update", "analysis_type": analysis_type, "data": payload_data}
                await self.active_connections[session_id].send_text(json.dumps(message))
                logger.debug(f"Sent {analysis_type} update to session {session_id}")
            except Exception as e:
                logger.error(f"Failed to send update to session {session_id}: {e}")
                self.disconnect(session_id)
    
    async def send_progress_update(self, session_id: str, step: str, progress: int, total_steps: int):
        if session_id in self.active_connections:
            try:
                message = {"type": "progress_update", "step": step, "progress": progress, "total_steps": total_steps, "percentage": int((progress / total_steps) * 100)}
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e: logger.error(f"Failed to send progress to session {session_id}: {e}")
    
    async def send_error(self, session_id: str, error_message: str):
        if session_id in self.active_connections:
            try:
                message = {"type": "error", "message": error_message}
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e: logger.error(f"Failed to send error to session {session_id}: {e}")

analysis_streamer = AnalysisStreamer()

async def stream_analysis_pipeline(audio_path: str, session_id: str, session_context: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
    # Initial steps that must complete before text-based analysis can begin
    initial_steps_count = 3 # AudioQuality, Transcription, EmotionAnalysis

    if session_context is None: session_context = {}

    def sse_format(data: Dict[str, Any]) -> str:
        return f"data: {json.dumps(data)}\n\n"

    try:
        GeminiService()
        logger.info("Streaming pipeline: GeminiService instantiated to ensure DSPy LM config.")

        current_step = 0 # For progress updates

        # Define text-based analysis services
        manipulation_service = ManipulationService()
        argument_service = ArgumentService()
        speaker_attitude_service = SpeakerAttitudeService()
        enhanced_understanding_service = EnhancedUnderstandingService()
        psychological_service = PsychologicalService()
        modular_audio_analysis_service = ModularAudioAnalysisService() # Text-inferred audio features
        quantitative_metrics_service = QuantitativeMetricsService()
        conversation_flow_service = ConversationFlowService()
        # linguistic_service = ... # if async

        # Map of text-dependent services
        text_analysis_map: Dict[str, Any] = {
            "manipulation_assessment": (manipulation_service.analyze, []), # Args to be filled after transcription
            "argument_analysis": (argument_service.analyze, []),
            "speaker_attitude": (speaker_attitude_service.analyze, []),
            "enhanced_understanding": (enhanced_understanding_service.analyze, []),
            "psychological_analysis": (psychological_service.analyze, []),
            "audio_analysis": (modular_audio_analysis_service.analyze, []), # text-inferred
            "quantitative_metrics": (quantitative_metrics_service.analyze, []),
            "conversation_flow": (conversation_flow_service.analyze, []),
            # "linguistic_analysis": (asyncio.to_thread(analyze_linguistic_patterns, transcript_text), []), # If sync
        }
        total_steps = initial_steps_count + len(text_analysis_map)


        current_step += 1
        yield sse_format({'type': 'progress', 'step': 'Audio Quality Assessment', 'progress': current_step, 'total': total_steps})
        try:
            from pydub import AudioSegment as PydubAudioSegment
            audio_segment_pydub = await asyncio.to_thread(PydubAudioSegment.from_file, audio_path)
            audio_quality_data = assess_audio_quality(audio_segment_pydub)
            yield sse_format({'type': 'result', 'analysis_type': 'audio_quality_metrics', 'data': audio_quality_data.model_dump() if hasattr(audio_quality_data, 'model_dump') else audio_quality_data})
        except Exception as e:
            logger.error(f"Streaming: Audio quality assessment failed: {e}", exc_info=True)
            yield sse_format({'type': 'error', 'message': f'Audio quality assessment error: {str(e)}'})
            # audio_quality_data = AudioQualityMetrics() # Default if needed by other parts

        current_step += 1
        yield sse_format({'type': 'progress', 'step': 'Transcription', 'progress': current_step, 'total': total_steps})
        transcript_text = "Transcription failed."
        try:
            transcript_text = await dspy_transcribe_audio(audio_path) # Uses DSPy
            yield sse_format({'type': 'result', 'analysis_type': 'transcript', 'data': {'transcript': transcript_text}})
        except Exception as e:
            logger.error(f"Streaming: Transcription error: {e}", exc_info=True)
            yield sse_format({'type': 'error', 'message': f'Transcription error: {str(e)}'})
        
        current_step += 1
        yield sse_format({'type': 'progress', 'step': 'Emotion Analysis', 'progress': current_step, 'total': total_steps})
        try:
            emotion_details = await dspy_analyze_emotions_audio(audio_path, transcript_text) # Uses DSPy
            yield sse_format({'type': 'result', 'analysis_type': 'emotion_analysis',
                              'data': [ed.model_dump() if hasattr(ed, 'model_dump') else ed for ed in emotion_details]})
        except Exception as e:
            logger.error(f"Streaming: Emotion analysis error: {e}", exc_info=True)
            yield sse_format({'type': 'error', 'message': f'Emotion analysis error: {str(e)}'})

        # Update args for text-dependent services now that transcript is available
        text_analysis_map["manipulation_assessment"] = (manipulation_service.analyze, [transcript_text, session_context])
        text_analysis_map["argument_analysis"] = (argument_service.analyze, [transcript_text, session_context])
        text_analysis_map["speaker_attitude"] = (speaker_attitude_service.analyze, [transcript_text, session_context])
        text_analysis_map["enhanced_understanding"] = (enhanced_understanding_service.analyze, [transcript_text, session_context])
        text_analysis_map["psychological_analysis"] = (psychological_service.analyze, [transcript_text, session_context])
        text_analysis_map["audio_analysis"] = (modular_audio_analysis_service.analyze, [transcript_text, session_context]) # text-inferred
        text_analysis_map["quantitative_metrics"] = (quantitative_metrics_service.analyze, [transcript_text,
                                                                                            session_context.get('speaker_diarization'),
                                                                                            session_context.get('sentiment_trend_data')])
        text_analysis_map["conversation_flow"] = (conversation_flow_service.analyze, [transcript_text,
                                                                                      session_context.get('dialogue_acts'),
                                                                                      session_context.get('speaker_diarization')])
        # if "linguistic_analysis" in text_analysis_map: # If it were added
        #    text_analysis_map["linguistic_analysis"] = (asyncio.to_thread(analyze_linguistic_patterns, transcript_text), [])


        for analysis_name, (service_method, args) in text_analysis_map.items():
            current_step += 1
            yield sse_format({'type': 'progress', 'step': analysis_name.replace("_", " ").title(), 'progress': current_step, 'total': total_steps})
            try:
                result_data = await service_method(*args) # All services in map are async now
                payload = result_data.model_dump() if hasattr(result_data, 'model_dump') else result_data
                yield sse_format({'type': 'result', 'analysis_type': analysis_name, 'data': payload})
            except Exception as e:
                logger.error(f"Streaming: Error in {analysis_name}: {e}", exc_info=True)
                yield sse_format({'type': 'error', 'message': f'Error in {analysis_name}: {str(e)}'})

        yield sse_format({'type': 'complete', 'message': 'Analysis pipeline completed'})

    except Exception as e:
        logger.error(f"Critical error in streaming_analysis_pipeline: {e}", exc_info=True)
        yield sse_format({'type': 'error', 'message': f'Critical pipeline error: {str(e)}'})
    finally:
        try:
            if audio_path and os.path.exists(audio_path):
                await asyncio.to_thread(os.unlink, audio_path)
                logger.info(f"Cleaned up temporary file from streaming pipeline: {audio_path}")
        except Exception as e:
            logger.warning(f"Streaming: Failed to clean up temporary file {audio_path}: {e}")

```
