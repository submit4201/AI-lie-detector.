"""
Streaming service for sending analysis results to frontend as they complete
"""
import json
import asyncio
import logging
from typing import Dict, Any, Optional, AsyncGenerator
from fastapi import WebSocket
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

class AnalysisStreamer:
    """
    Handles streaming of analysis results to frontend as they complete
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a websocket for a session"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected for session {session_id}")
    
    def disconnect(self, session_id: str):
        """Disconnect websocket for a session"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected for session {session_id}")
    
    async def send_analysis_update(self, session_id: str, analysis_type: str, data: Dict[str, Any]):
        """Send an analysis update to the frontend"""
        if session_id in self.active_connections:
            try:
                message = {
                    "type": "analysis_update",
                    "analysis_type": analysis_type,
                    "data": data,
                    "timestamp": str(asyncio.get_event_loop().time())
                }
                await self.active_connections[session_id].send_text(json.dumps(message))
                logger.info(f"Sent {analysis_type} update to session {session_id}")
            except Exception as e:
                logger.error(f"Failed to send update to session {session_id}: {e}")
                self.disconnect(session_id)
    
    async def send_progress_update(self, session_id: str, step: str, progress: int, total_steps: int):
        """Send a progress update to the frontend"""
        if session_id in self.active_connections:
            try:
                message = {
                    "type": "progress_update",
                    "step": step,
                    "progress": progress,
                    "total_steps": total_steps,
                    "percentage": int((progress / total_steps) * 100)
                }
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send progress to session {session_id}: {e}")
    
    async def send_error(self, session_id: str, error_message: str):
        """Send an error message to the frontend"""
        if session_id in self.active_connections:
            try:
                message = {
                    "type": "error",
                    "message": error_message,
                    "timestamp": str(asyncio.get_event_loop().time())
                }
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send error to session {session_id}: {e}")

# Global streamer instance
analysis_streamer = AnalysisStreamer()

async def stream_analysis_pipeline(audio_path: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Stream the analysis pipeline results as they complete
    """
    try:
        from .gemini_service import transcribe_with_gemini, query_gemini_with_audio, analyze_emotions_with_gemini
        from .audio_service import assess_audio_quality
        from .linguistic_service import linguistic_analysis_pipeline
        import os
        
        # Step 1: Audio Quality Assessment
        yield f"data: {json.dumps({'type': 'progress', 'step': 'audio_quality', 'progress': 1, 'total': 5})}\n\n"
        
        # Mock audio quality for now - you can implement actual assessment
        audio_quality = {"duration": 30.0, "sample_rate": 48000, "quality_score": 80}
        yield f"data: {json.dumps({'type': 'result', 'analysis_type': 'audio_quality', 'data': audio_quality})}\n\n"
        
        # Step 2: Transcription
        yield f"data: {json.dumps({'type': 'progress', 'step': 'transcription', 'progress': 2, 'total': 5})}\n\n"
        
        try:
            transcript = transcribe_with_gemini(audio_path)
            yield f"data: {json.dumps({'type': 'result', 'analysis_type': 'transcript', 'data': {'transcript': transcript}})}\n\n"
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Transcription error: {str(e)}'})}\n\n"
            transcript = "Unable to transcribe audio"
        
        # Step 3: Gemini Audio Analysis
        yield f"data: {json.dumps({'type': 'progress', 'step': 'gemini_analysis', 'progress': 3, 'total': 5})}\n\n"
        
        try:
            gemini_result = query_gemini_with_audio(audio_path, transcript, {}, None)
            yield f"data: {json.dumps({'type': 'result', 'analysis_type': 'gemini_analysis', 'data': gemini_result})}\n\n"
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Gemini analysis error: {str(e)}'})}\n\n"
        
        # Step 4: Emotion Analysis
        yield f"data: {json.dumps({'type': 'progress', 'step': 'emotion_analysis', 'progress': 4, 'total': 5})}\n\n"
        
        try:
            emotions = analyze_emotions_with_gemini(audio_path, transcript)
            yield f"data: {json.dumps({'type': 'result', 'analysis_type': 'emotion_analysis', 'data': emotions})}\n\n"
        except Exception as e:
            logger.error(f"Emotion analysis error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Emotion analysis error: {str(e)}'})}\n\n"
        
        # Step 5: Linguistic Analysis
        yield f"data: {json.dumps({'type': 'progress', 'step': 'linguistic_analysis', 'progress': 5, 'total': 5})}\n\n"
        
        try:
            linguistic_result = linguistic_analysis_pipeline(transcript, audio_quality.get('duration', 30.0))
            yield f"data: {json.dumps({'type': 'result', 'analysis_type': 'linguistic_analysis', 'data': linguistic_result})}\n\n"
        except Exception as e:
            logger.error(f"Linguistic analysis error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Linguistic analysis error: {str(e)}'})}\n\n"
          # Final completion
        yield f"data: {json.dumps({'type': 'complete', 'message': 'Analysis pipeline completed'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in streaming pipeline: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    finally:
        # Clean up temporary audio file
        try:
            if os.path.exists(audio_path):
                os.unlink(audio_path)
                logger.info(f"Cleaned up temporary file: {audio_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {audio_path}: {e}")
