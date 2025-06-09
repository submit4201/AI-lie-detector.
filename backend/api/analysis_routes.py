from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import tempfile
import os
import logging
from typing import Optional
from pydub import AudioSegment

from models import AnalyzeResponse, ErrorResponse
from services.audio_service import assess_audio_quality, streaming_audio_analysis_pipeline
from services.gemini_service import query_gemini, query_gemini_with_audio, validate_and_structure_gemini_response
from services.linguistic_service import analyze_linguistic_patterns
from services.session_service import conversation_history_service # Import the instance
from services.session_insights_service import SessionInsightsGenerator
from services.streaming_service import analysis_streamer, stream_analysis_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize session insights generator
session_insights_generator = SessionInsightsGenerator()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time analysis updates"""
    await analysis_streamer.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Could handle client commands here if needed
    except WebSocketDisconnect:
        analysis_streamer.disconnect(session_id)

@router.post(
    "/analyze/stream",
    tags=["Analysis"],
    summary="Stream Audio Analysis",
    description="Uploads an audio file and streams analysis results as they complete. Returns Server-Sent Events with real-time updates.",
)
async def stream_analyze_audio(
    audio: UploadFile = File(..., description="Audio file to be analyzed"),
    session_id_form: Optional[str] = Form(None, alias="session_id")
):
    """Stream analysis results as they complete"""
    try:
        # Resolve session_id
        current_session_id = conversation_history_service.get_or_create_session(session_id_form)
        logger.info(f"Starting streaming analysis for session: {current_session_id}")
        
        # Validate audio file
        valid_audio_types = ['audio/', 'video/']
        valid_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.webm', '.flac']
        
        is_valid_content_type = (audio.content_type and 
                               any(audio.content_type.startswith(t) for t in valid_audio_types))
        is_valid_extension = (audio.filename and 
                            any(audio.filename.lower().endswith(ext) for ext in valid_extensions))
        
        if not (is_valid_content_type or is_valid_extension):
            raise HTTPException(status_code=422, detail="Invalid audio file type")
          # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename or ".wav")[1]) as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_audio_path = temp_file.name
        
        # Return streaming response
        return StreamingResponse(
            stream_analysis_pipeline(temp_audio_path, current_session_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        logger.error(f"Error in streaming analysis: {e}")
        # Clean up temp file on error
        if 'temp_audio_path' in locals():
            try:
                os.unlink(temp_audio_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    tags=["Analysis"],
    summary="Analyze Audio File",
    description="Uploads an audio file and performs a comprehensive analysis for deception, emotion, and other speech patterns. Returns detailed results including a transcript, audio quality assessment, emotion scores, and AI-driven insights.",    responses={
        200: {"description": "Successful analysis"},
        400: {"model": ErrorResponse, "description": "Invalid input (e.g., not an audio file, file too short, unintelligible audio)."},
        413: {"model": ErrorResponse, "description": "File too large."},
        422: {"model": ErrorResponse, "description": "Validation error (e.g., invalid file type by content)."},
        500: {"model": ErrorResponse, "description": "Internal server error during analysis."}
    }
)
async def analyze_audio_route(
    audio: UploadFile = File(..., description="Audio file to be analyzed (WAV, MP3, OGG, WEBM). Max size 15MB."),
    session_id_form: Optional[str] = Form(None, alias="session_id", description="Optional session ID for conversation continuity. If not provided, a new session will be created.")
):
    try:
        # Resolve session_id: Use form value if provided, otherwise create new.
        # This handles the "get or create session" logic streamlined.
        current_session_id = conversation_history_service.get_or_create_session(session_id_form)
        logger.info(f"Starting analysis for session: {current_session_id}")        # More robust audio file validation - check both content type and file extension
        valid_audio_types = ['audio/', 'video/']
        valid_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.webm', '.flac']
        
        is_valid_content_type = (audio.content_type and 
                               any(audio.content_type.startswith(t) for t in valid_audio_types))
        is_valid_extension = (audio.filename and 
                            any(audio.filename.lower().endswith(ext) for ext in valid_extensions))
        
        if not (is_valid_content_type or is_valid_extension):
            raise HTTPException(status_code=400, detail="File must be an audio file (MP3, WAV, M4A, AAC, OGG, WEBM, FLAC).")

        audio_content = await audio.read()
        file_size = len(audio_content) # More reliable size after reading

        logger.info(f"Received audio file: {audio.filename or 'unnamed'}, Content-Type: {audio.content_type}, Size: {file_size} bytes for session {current_session_id}")

        # Max file size check (e.g., 15MB)
        MAX_FILE_SIZE = 15 * 1024 * 1024
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File size {file_size} bytes exceeds {MAX_FILE_SIZE}MB limit.")
            raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB.")

        # Save uploaded file temporarily
        # Ensure the suffix is appropriate for pydub to recognize the format
        suffix = os.path.splitext(audio.filename or "")[1] if audio.filename and os.path.splitext(audio.filename)[1] else ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(audio_content)
            temp_audio_path = temp_audio.name
        del audio_content # Free memory

        wav_path = None # Initialize wav_path
        try:
            audio_segments = []
            audio_segment = AudioSegment.from_file(temp_audio_path)
            if audio_segment.duration_seconds < 1:
                raise HTTPException(status_code=400, detail="Audio file is too short. Please provide audio that is at least 1 second long.")
            if audio_segment.duration_seconds > 120:
                # cut audio to  2 minutes segments
                for i in range(0, len(audio_segment), 120000):
                    audio_segments.append(audio_segment[i:i+120000])
            else:
                audio_segments.append(audio_segment)
            
            #loop through audio segments and analyze each one
            for audio_segment in audio_segments:
                # Assess audio quality
                logger.info(f"Assessing audio quality for segment of {audio_segment.duration_seconds} seconds")
                audio_quality_metrics = assess_audio_quality(audio_segment)
                # Convert to WAV for speech recognition
                # Use a new temporary file for the WAV version
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                    wav_path = temp_wav.name
                audio_segment.export(wav_path, format="wav")
                from services.gemini_service import full_audio_analysis_pipeline # Import here to avoid circular import
                # full audio analysis pipeline
                try:
                    gemini_response = full_audio_analysis_pipeline(wav_path, None, {})
                    logger.info(f"Gemini analysis response: {gemini_response}")
                    transcript_text = gemini_response.get('transcript', 'No transcript available')
                except Exception as e:
                    logger.warning(f"Gemini API unavailable or failed: {e}. Using fallback analysis.")
                    # Create a fallback response when Gemini is unavailable
                    transcript_text = "This is a sample transcript generated when the Gemini API is unavailable. The system is using default analysis values."
                    gemini_response = {
                        'transcript': transcript_text,
                        'audio_query_response': {},
                        'audio_analysis': {},
                        'emotion_analysis': {},
                        'full_analysis_response': '{}'
                    }
                if not transcript_text or len(transcript_text.strip()) < 10:
                    logger.warning(f"Transcript too short or empty for file {audio.filename or 'unnamed'}: '{transcript_text}'")
                    raise HTTPException(status_code=400, detail="Transcript too short or empty. Please provide longer audio with clear speech (min 10 characters after transcription).")

                # Get session context for Gemini analysis (flags here are from session context, not primary analysis)
                session_context_data = conversation_history_service.get_session_context(current_session_id)            # In the original main.py, 'flags' passed to query_gemini was session_context.
                # Let's pass the relevant part of session_context if needed, or adjust query_gemini.
                # The prompt in query_gemini refers to "RED FLAGS FROM PRIMARY ANALYSIS",
                # which seems to be missing from this flow if not explicitly generated before Gemini.
                # For now, passing empty dict for primary_analysis_flags as it was not explicitly defined.            # This might need refinement if primary flags are expected by Gemini prompt.
                
                # Use query_gemini_with_audio for proper audio analysis instead of text-only
                validated_gemini_analysis = validate_and_structure_gemini_response(gemini_response, transcript_text)

                logger.info(f"Analysis completed successfully for session {current_session_id}")
                
                final_result_data = {
                    "session_id": current_session_id,
                    "speaker_name": "Speaker 1",  # Default speaker name
                    "transcript": transcript_text,
                    "audio_quality": audio_quality_metrics,
                    "emotion_analysis": validated_gemini_analysis.get("emotion_analysis", []),
                    "linguistic_analysis": validated_gemini_analysis.get("linguistic_analysis", {}),
                    # Add quantitative metrics as a separate field for UI
                    "quantitative_metrics": validated_gemini_analysis.get("linguistic_analysis", {}),
                    # Check if audio analysis was performed (if Gemini returns audio_analysis)
                    "audio_analysis": validated_gemini_analysis.get("audio_analysis", {}),
                    
                    **validated_gemini_analysis
                }
            
            # Add session insights if context was used and Gemini didn't override it
            if session_context_data.get("previous_analyses", 0) > 0 and 'session_insights' not in validated_gemini_analysis:
                # Get session history for intelligent insights generation
                session_history = conversation_history_service.get_session_history(current_session_id)
                
                # Generate intelligent session insights
                session_insights = session_insights_generator.generate_session_insights(
                    session_context_data, 
                    validated_gemini_analysis, 
                    session_history
                )
                
                if session_insights:
                    final_result_data['session_insights'] = session_insights

            conversation_history_service.add_analysis(current_session_id, transcript_text, final_result_data)

            return AnalyzeResponse(**final_result_data)

        except HTTPException: # Re-raise HTTPExceptions directly
            raise
        except Exception as e: # Catch-all for other unexpected errors during processing
            logger.error(f"Unexpected error processing audio file {audio.filename or 'unnamed'} in session {current_session_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during audio processing: {str(e)}")
        finally:
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
            if wav_path and os.path.exists(wav_path):
                os.unlink(wav_path)

    except HTTPException: # Re-raise HTTPExceptions from initial checks (file size, type)
        raise
    except Exception as e: # Catch-all for truly unexpected errors (e.g., issues before processing starts)
        logger.error(f"Critical unexpected error in /analyze endpoint for session {session_id_form}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"A critical unexpected error occurred: {str(e)}")

@router.post(
    "/analyze_text",
    response_model=AnalyzeResponse,
    tags=["Analysis"],
    summary="Analyze Text Input",
    description="Analyzes text input for deception, manipulation, and other linguistic patterns. Useful for testing UI components."
)
async def analyze_text_input(
    request: dict,
    session_id: Optional[str] = None
):
    """
    Analyze text input for testing the new UI components.
    """
    try:
        text = request.get("text", "")
        speaker_name = request.get("speaker_name", "Speaker")
        
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text must be at least 10 characters long")
          # Get or create session
        if not session_id:
            session_id = conversation_history_service.get_or_create_session()
        
        # Get session context
        session_context_data = conversation_history_service.get_session_context(session_id)
        
        # Perform linguistic analysis
        linguistic_analysis = analyze_linguistic_patterns(text)
        
        # Get Gemini analysis
        gemini_raw_response = query_gemini(text, linguistic_analysis, session_context_data)
        validated_gemini_analysis = validate_and_structure_gemini_response(gemini_raw_response, text, linguistic_analysis)        # Build final result
        final_result_data = {
            "session_id": session_id,
            "speaker_name": speaker_name,
            "transcript": text,"audio_quality": {
                "duration": 0.0,
                "sample_rate": 0,
                "channels": 0,
                "loudness": 0.0,
                "quality_score": 0,
                "overall_quality": "N/A",
                "signal_to_noise_ratio": 0,
                "clarity_score": 0,
                "volume_consistency": 0,
                "background_noise_level": 0
            },  # Default audio quality for text-only
            "emotion_analysis": [],  # Empty emotion analysis for text-only
            "linguistic_analysis": linguistic_analysis,
            "quantitative_metrics": linguistic_analysis,
            "audio_analysis": validated_gemini_analysis.get('audio_analysis'),
            **validated_gemini_analysis
        }
        
        # Add session insights if applicable
        if session_context_data.get("previous_analyses", 0) > 0 and 'session_insights' not in validated_gemini_analysis:
            session_history = conversation_history_service.get_session_history(session_id)
            session_insights = session_insights_generator.generate_session_insights(
                session_context_data, 
                validated_gemini_analysis, 
                session_history
            )
            
            if session_insights:
                final_result_data['session_insights'] = session_insights
        
        # Save to history
        conversation_history_service.add_analysis(session_id, text, final_result_data)
        
        return AnalyzeResponse(**final_result_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in text analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")
