from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
import tempfile
import os
import logging
from typing import Optional

from backend.models import AnalyzeResponse, ErrorResponse
from backend.services.audio_service import assess_audio_quality, transcribe_audio, analyze_emotion
from backend.services.gemini_service import query_gemini, validate_and_structure_gemini_response
from backend.services.session_service import conversation_history_service # Import the instance
import speech_recognition as sr # For specific error types

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    tags=["Analysis"],
    summary="Analyze Audio File",
    description="Uploads an audio file and performs a comprehensive analysis for deception, emotion, and other speech patterns. Returns detailed results including a transcript, audio quality assessment, emotion scores, and AI-driven insights.",
    responses={
        200: {"description": "Successful analysis"},
        400: {"model": ErrorResponse, "description": "Invalid input (e.g., not an audio file, file too short, unintelligible audio)."},
        413: {"model": ErrorResponse, "description": "File too large."},
        422: {"model": ErrorResponse, "description": "Validation error (e.g., invalid file type by content)."},
        500: {"model": ErrorResponse, "description": "Internal server error during analysis."},
        503: {"model": ErrorResponse, "description": "Speech recognition service error."}
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
        logger.info(f"Starting analysis for session: {current_session_id}")

        if not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file.")

        audio_content = await audio.read()
        file_size = len(audio_content) # More reliable size after reading

        logger.info(f"Received audio file: {audio.filename}, Content-Type: {audio.content_type}, Size: {file_size} bytes for session {current_session_id}")

        # Max file size check (e.g., 15MB)
        MAX_FILE_SIZE = 15 * 1024 * 1024
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File size {file_size} bytes exceeds {MAX_FILE_SIZE}MB limit.")
            raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB.")

        # Save uploaded file temporarily
        # Ensure the suffix is appropriate for pydub to recognize the format
        suffix = os.path.splitext(audio.filename)[1] if os.path.splitext(audio.filename)[1] else ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(audio_content)
            temp_audio_path = temp_audio.name
        del audio_content # Free memory

        wav_path = None # Initialize wav_path
        try:
            audio_segment = AudioSegment.from_file(temp_audio_path)
            audio_quality_metrics = assess_audio_quality(audio_segment)
            logger.info(f"Audio quality metrics: {audio_quality_metrics}")

            # Convert to WAV for speech recognition
            # Use a new temporary file for the WAV version
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                wav_path = temp_wav.name
            audio_segment.export(wav_path, format="wav")

            transcript_text = transcribe_audio(wav_path)

            if not transcript_text or len(transcript_text.strip()) < 10:
                logger.warning(f"Transcript too short or empty for file {audio.filename}: '{transcript_text}'")
                raise HTTPException(status_code=400, detail="Transcript too short or empty. Please provide longer audio with clear speech (min 10 characters after transcription).")

            emotion_scores = analyze_emotion(transcript_text)

            # Get session context for Gemini analysis (flags here are from session context, not primary analysis)
            session_context_data = conversation_history_service.get_session_context(current_session_id)

            # In the original main.py, 'flags' passed to query_gemini was session_context.
            # Let's pass the relevant part of session_context if needed, or adjust query_gemini.
            # The prompt in query_gemini refers to "RED FLAGS FROM PRIMARY ANALYSIS",
            # which seems to be missing from this flow if not explicitly generated before Gemini.
            # For now, passing empty dict for primary_analysis_flags as it was not explicitly defined.
            # This might need refinement if primary flags are expected by Gemini prompt.
            primary_analysis_flags = {} # Placeholder - to be defined if there's a pre-Gemini flag generation step

            gemini_raw_response = query_gemini(transcript_text, primary_analysis_flags, session_context_data)
            validated_gemini_analysis = validate_and_structure_gemini_response(gemini_raw_response, transcript_text)

            logger.info(f"Analysis completed successfully for session {current_session_id}")

            final_result_data = {
                "session_id": current_session_id,
                "transcript": transcript_text,
                "audio_quality": audio_quality_metrics,
                "emotion_analysis": emotion_scores,
                **validated_gemini_analysis
            }

            # Add session insights if context was used and Gemini didn't override it
            if session_context_data.get("previous_analyses", 0) > 0 and 'session_insights' not in validated_gemini_analysis:
                 final_result_data['session_insights'] = { # Default insights if Gemini doesn't provide specific ones
                    "consistency_analysis": "Contextual analysis performed.",
                    "behavioral_evolution": "User behavior patterns considered.",
                    "risk_trajectory": "Risk assessment over time considered.",
                    "conversation_dynamics": "Overall conversation dynamics analyzed."
                }


            conversation_history_service.add_analysis(current_session_id, transcript_text, final_result_data)

            return AnalyzeResponse(**final_result_data)

        except sr.UnknownValueError:
            logger.warning(f"Speech recognition: Could not understand audio from file {audio.filename} in session {current_session_id}.")
            raise HTTPException(status_code=400, detail="Could not understand the audio. Please ensure clear speech and good audio quality.")
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error for file {audio.filename} in session {current_session_id}: {e}")
            raise HTTPException(status_code=503, detail=f"Speech recognition service error: {e}")
        except HTTPException: # Re-raise HTTPExceptions directly
            raise
        except Exception as e: # Catch-all for other unexpected errors during processing
            logger.error(f"Unexpected error processing audio file {audio.filename} in session {current_session_id}: {str(e)}", exc_info=True)
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
