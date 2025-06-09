from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
import tempfile
import os
import logging
from typing import Optional
from pydub import AudioSegment

from models import AnalyzeResponse, ErrorResponse
from services.audio_service import assess_audio_quality, transcribe_audio, analyze_emotion
from services.gemini_service import query_gemini, validate_and_structure_gemini_response
from services.linguistic_service import analyze_linguistic_patterns
from services.session_service import conversation_history_service # Import the instance
from services.session_insights_service import SessionInsightsGenerator
import speech_recognition as sr # For specific error types

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize session insights generator
session_insights_generator = SessionInsightsGenerator()

@router.post(
    "/analyze",
    response_model=AnalyzeResponse, # Defines the successful response structure.
    tags=["Analysis"], # Groups this endpoint in Swagger UI.
    summary="Analyze Audio File for Deception and Speech Patterns",
    description=(
        "Uploads an audio file (WAV, MP3, OGG, WEBM, M4A, FLAC) and performs a comprehensive analysis. "
        "The analysis includes speech-to-text transcription, audio quality assessment, "
        "emotion detection, quantitative linguistic pattern analysis, and advanced AI-driven insights "
        "for deception, credibility, and communication style. "
        "Supports session continuity via an optional session ID."
    ),
    responses={ # Defines possible responses, including error cases.
        200: {"description": "Successful analysis with detailed results."},
        400: {"model": ErrorResponse, "description": "Invalid input. Reasons include: not an audio file, file too short for meaningful analysis, or unintelligible audio content."},
        413: {"model": ErrorResponse, "description": "Uploaded file is too large. See limits in description."},
        422: {"model": ErrorResponse, "description": "Validation error, often due to incorrect file type determined by content inspection, even if extension is acceptable."},
        500: {"model": ErrorResponse, "description": "Internal server error occurred during the analysis process."},
        503: {"model": ErrorResponse, "description": "A dependent service (e.g., speech recognition) encountered an error."}
    }
)
async def analyze_audio_route(
    audio: UploadFile = File(..., description="Audio file to be analyzed (e.g., WAV, MP3, OGG, WEBM, M4A, FLAC). Maximum size: 15MB."),
    session_id_form: Optional[str] = Form(None, alias="session_id", description="Optional session ID for conversation continuity. If not provided, or if the ID is new, a new session will be created and its ID returned.")
):
    """
    Handles audio file uploads, performs comprehensive analysis, and returns structured results.

    This endpoint orchestrates various services:
    1.  Session Management: Retrieves or creates a session using `conversation_history_service`.
    2.  File Validation: Checks content type and file size.
    3.  Audio Processing: Saves the uploaded file temporarily, converts it to WAV format
        using Pydub for standardization, and assesses basic audio quality.
    4.  Transcription: Converts speech in the WAV file to text using `transcribe_audio`.
    5.  Emotion Analysis: Analyzes emotions from the transcript using `analyze_emotion`.
    6.  Linguistic Analysis: Calculates quantitative linguistic patterns from the transcript.
    7.  AI-Powered Analysis: Queries a Gemini model with the transcript and session context
        for deeper insights, then validates and structures this response.
    8.  Session Insights: If it's not the first analysis in a session, generates insights
        based on the session's history and the current analysis.
    9.  History Update: Adds the current analysis results to the session's history.

    Error handling is implemented for issues like invalid file types, processing errors,
    and failures in external services (e.g., speech recognition).

    Args:
        audio: The uploaded audio file. FastAPI handles the multi-part form data.
        session_id_form: Optional session ID passed as a form field.

    Returns:
        An `AnalyzeResponse` Pydantic model containing all analysis results on success.
        Raises `HTTPException` with an `ErrorResponse` model on failure.
    """
    temp_audio_path: Optional[str] = None # Path for the initially uploaded temp file
    wav_path: Optional[str] = None        # Path for the converted WAV temp file

    try:
        # --- Session Handling ---
        # Resolve session_id: Use form value if provided, otherwise get_or_create_session will make a new one.
        current_session_id = conversation_history_service.get_or_create_session(session_id_form)
        logger.info(f"Initiating analysis for session ID: {current_session_id}. Received file: {audio.filename or 'unnamed file'}")

        # --- File Validation & Initial Processing ---
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            logger.warning(f"Invalid content type '{audio.content_type}' for session {current_session_id}.")
            raise HTTPException(status_code=400, detail="Uploaded file is not an audio file. Please ensure the Content-Type is audio/*.")

        audio_content = await audio.read() # Read file content into memory.
        file_size_bytes = len(audio_content)
        logger.info(f"Audio file '{audio.filename or 'unnamed'}' received. Content-Type: {audio.content_type}, Size: {file_size_bytes} bytes for session {current_session_id}.")

        # Maximum file size check (e.g., 15MB).
        MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024
        if file_size_bytes > MAX_FILE_SIZE_BYTES:
            logger.warning(f"File size {file_size_bytes} bytes exceeds {MAX_FILE_SIZE_BYTES}B limit for session {current_session_id}.")
            raise HTTPException(status_code=413, detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_BYTES // (1024*1024)}MB.")
        if file_size_bytes == 0:
            logger.warning(f"Uploaded file is empty for session {current_session_id}.")
            raise HTTPException(status_code=400, detail="Uploaded file is empty. Please provide a valid audio file.")

        # --- Temporary File Management & Audio Conversion ---
        # Save uploaded audio to a temporary file.
        # The suffix is important for Pydub to correctly identify the original format.
        original_suffix = os.path.splitext(audio.filename or "")[1] if audio.filename and os.path.splitext(audio.filename)[1] else ".tmp"

        with tempfile.NamedTemporaryFile(delete=False, suffix=original_suffix) as temp_audio_file_obj:
            temp_audio_file_obj.write(audio_content)
            temp_audio_path = temp_audio_file_obj.name
        del audio_content # Free memory after writing to disk.

        try:
            # --- Core Audio Processing and Analysis ---
            # Load audio using Pydub (supports various formats like MP3, WEBM, OGG, M4A, FLAC etc.)
            audio_segment = AudioSegment.from_file(temp_audio_path)
            # Assess basic audio quality metrics from the loaded segment.
            audio_quality_metrics = assess_audio_quality(audio_segment)
            logger.info(f"Audio quality metrics for session {current_session_id}: {audio_quality_metrics}")

            # Convert the audio to WAV format for standardization, as required by some speech recognition services.
            # A new temporary file is created for the WAV version.
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file_obj:
                wav_path = temp_wav_file_obj.name
            audio_segment.export(wav_path, format="wav") # Export to WAV
            logger.info(f"Audio for session {current_session_id} converted to WAV format at {wav_path}")

            # Transcribe the WAV audio to text.
            transcript_text = transcribe_audio(wav_path)
            logger.info(f"Transcription completed for session {current_session_id}. Transcript length: {len(transcript_text)} chars.")

            # Validate transcript length.
            if not transcript_text or len(transcript_text.strip()) < 10: # Arbitrary minimum length
                logger.warning(f"Transcript too short or empty for session {current_session_id}. File: {audio.filename or 'unnamed'}, Transcript: '{transcript_text}'")
                raise HTTPException(status_code=400, detail="Transcript is too short or empty. Please provide audio with at least 10 characters of clear speech after transcription.")

            # Analyze emotions from the transcript.
            emotion_scores = analyze_emotion(transcript_text)
            logger.info(f"Emotion analysis completed for session {current_session_id}.")

            # Perform quantitative linguistic analysis on the transcript.
            # Duration from audio_quality_metrics is used for rate calculations (e.g., WPM).
            linguistic_analysis = analyze_linguistic_patterns(
                transcript_text, 
                audio_quality_metrics.get('duration') # Pass duration in seconds
            )
            logger.info(f"Linguistic analysis completed for session {current_session_id}.")

            # --- AI-Powered Analysis & Session Context ---
            # Retrieve session context (history, patterns) for more informed AI analysis.
            session_context_data = conversation_history_service.get_session_context(current_session_id)
            logger.info(f"Session context retrieved for session {current_session_id}. Previous analyses: {session_context_data.get('previous_analyses',0)}")

            # Define primary_analysis_flags. Currently, this is a placeholder.
            # In a more complex system, this might come from a preliminary rule-based check on the current transcript
            # or other immediate cues before the main Gemini call.
            # For now, it's an empty dict, meaning Gemini will rely on transcript and session context primarily.
            primary_analysis_flags = {}
            
            # Query the Gemini model with the transcript, (empty) primary flags, and session context.
            gemini_raw_response = query_gemini(transcript_text, primary_analysis_flags, session_context_data)
            logger.info(f"Gemini query completed for session {current_session_id}.")

            # Validate and structure Gemini's response, ensuring it conforms to the expected schema.
            # Pass current linguistic_analysis so it can be part of the validated structure if Gemini doesn't provide its own.
            validated_gemini_analysis = validate_and_structure_gemini_response(
                gemini_raw_response, transcript_text, linguistic_analysis
            )
            logger.info(f"Gemini response validated and structured for session {current_session_id}.")

            # --- Assemble Final Response ---
            # Combine all analysis results into the final response structure.
            final_result_data = {
                "session_id": current_session_id,
                "transcript": transcript_text,
                "audio_quality": audio_quality_metrics,
                "emotion_analysis": emotion_scores,
                # linguistic_analysis is now part of validated_gemini_analysis if not overridden by Gemini
                **validated_gemini_analysis # Spread the validated Gemini analysis results
            }

            # Generate and add session insights if this is not the first analysis in the session
            # and if Gemini's response doesn't already include 'session_insights'.
            if session_context_data.get("previous_analyses", 0) > 0 and 'session_insights' not in validated_gemini_analysis:
                session_history_for_insights = conversation_history_service.get_session_history(current_session_id)
                logger.info(f"Generating session insights for session {current_session_id} with {len(session_history_for_insights)} history entries.")
                
                session_insights = session_insights_generator.generate_session_insights(
                    session_context_data, 
                    final_result_data, # Pass the current, assembled analysis data
                    session_history_for_insights
                )
                
                if session_insights: # Add insights if they were generated
                    final_result_data['session_insights'] = session_insights
                    logger.info(f"Session insights generated and added for session {current_session_id}.")

            # Add the complete current analysis (including insights if generated) to the session history.
            conversation_history_service.add_analysis(current_session_id, transcript_text, final_result_data)
            logger.info(f"Current analysis added to history for session {current_session_id}.")

            return AnalyzeResponse(**final_result_data) # Return the Pydantic model response.

        # --- Error Handling for Core Processing ---
        except sr.UnknownValueError: # Specific error from speech_recognition if audio is unintelligible.
            logger.warning(f"Speech recognition error: Could not understand audio. File: {audio.filename or 'unnamed'}, Session: {current_session_id}.")
            raise HTTPException(status_code=400, detail="Could not understand the audio. Please ensure the speech is clear and the audio quality is good.")
        except sr.RequestError as e: # Error from speech_recognition if the service is down or unreachable.
            logger.error(f"Speech recognition service error. File: {audio.filename or 'unnamed'}, Session: {current_session_id}. Error: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail=f"Speech recognition service error: {e}. Please try again later.")
        except HTTPException: # Re-raise HTTPExceptions that were raised explicitly (e.g., for file size).
            raise
        except Exception as e: # Catch-all for other unexpected errors during the try-block of processing.
            logger.error(f"Unexpected error processing audio file '{audio.filename or 'unnamed'}' in session {current_session_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during audio processing: {str(e)}. Please check server logs.")
        finally:
            # --- Temporary File Cleanup ---
            # Ensure temporary files are deleted regardless of success or failure.
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
                logger.info(f"Deleted temporary original audio file: {temp_audio_path} for session {current_session_id}")
            if wav_path and os.path.exists(wav_path):
                os.unlink(wav_path)
                logger.info(f"Deleted temporary WAV file: {wav_path} for session {current_session_id}")

    # --- Outer Error Handling (for issues before core processing begins) ---
    except HTTPException: # Re-raise HTTPExceptions from initial checks (e.g. problem with Form data).
        raise
    except Exception as e: # Catch-all for truly unexpected errors at the endpoint level.
        logger.critical(f"Critical unexpected error in /analyze endpoint. Session ID (from form, if any): {session_id_form}. Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"A critical unexpected server error occurred: {str(e)}. Please contact support.")
