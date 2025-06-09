import dspy
import asyncio
import base64
import os
import json
import logging
from typing import List, Optional # Ensure List and Optional are imported
from backend.models import EmotionDetail
from backend.dspy_modules import DSPyTranscriptionModule, DSPyEmotionAnalysisModule
from backend.services.gemini_service import GeminiService # To ensure LM is configured

logger = logging.getLogger(__name__)

# Ensure DSPy LM is configured when this module is loaded or service is initialized.
# This assumes GeminiService() call in functions will init the LM if not already.
# A more robust way is a dedicated app startup configuration.

async def dspy_transcribe_audio(audio_path: str) -> str:
    """Transcribes audio using a DSPy module."""
    # Ensure LM is configured
    lm_configured = False
    try:
        if dspy.settings.lm:
            lm_configured = True
    except AttributeError:
        pass

    if not lm_configured:
        logger.warning("DSPy LM not configured in dspy_transcribe_audio. Attempting init.")
        GeminiService() # Attempt to configure if not already

        lm_configured_after_init = False
        try:
            if dspy.settings.lm:
                lm_configured_after_init = True
        except AttributeError:
            pass

        if not lm_configured_after_init:
            logger.error("DSPy LM failed to configure. Transcription cannot proceed.")
            raise RuntimeError("DSPy LM not configured for transcription.")
        else:
            logger.info("DSPy LM configured after explicit GeminiService initialization.")


    try:
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        file_ext = os.path.splitext(audio_path)[1].lower()
        mime_type_map = {
            '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.m4a': 'audio/mp4',
            '.ogg': 'audio/ogg', '.webm': 'audio/webm', '.flac': 'audio/flac'
        }
        mime_type = mime_type_map.get(file_ext, 'audio/wav') # Default to wav

        transcription_module = DSPyTranscriptionModule()
        # DSPy modules are synchronous by default in their forward pass
        transcript = await asyncio.to_thread(
            transcription_module.forward,
            audio_base64_string=audio_base64,
            audio_mime_type=mime_type
        )
        logger.info(f"DSPy transcription successful for {audio_path}")
        return transcript
    except FileNotFoundError:
        logger.error(f"Audio file not found: {audio_path}")
        raise
    except Exception as e:
        logger.error(f"Error during DSPy transcription for {audio_path}: {e}", exc_info=True)
        # Fallback or re-raise
        return "Transcription failed due to an error."


async def dspy_analyze_emotions_audio(audio_path: str, transcript: str) -> List[EmotionDetail]:
    """Analyzes emotions from audio and transcript using a DSPy module."""
    lm_configured = False
    try:
        if dspy.settings.lm:
            lm_configured = True
    except AttributeError:
        pass

    if not lm_configured:
        logger.warning("DSPy LM not configured in dspy_analyze_emotions_audio. Attempting init.")
        GeminiService()

        lm_configured_after_init = False
        try:
            if dspy.settings.lm:
                lm_configured_after_init = True
        except AttributeError:
            pass

        if not lm_configured_after_init:
            logger.error("DSPy LM failed to configure. Emotion analysis cannot proceed.")
            return [EmotionDetail(emotion="error_lm_not_configured", score=0.0, timestamp_start=None, timestamp_end=None)]
        else:
            logger.info("DSPy LM configured after explicit GeminiService initialization for emotion analysis.")


    try:
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        file_ext = os.path.splitext(audio_path)[1].lower()
        mime_type_map = {
            '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.m4a': 'audio/mp4',
            '.ogg': 'audio/ogg', '.webm': 'audio/webm', '.flac': 'audio/flac'
        }
        mime_type = mime_type_map.get(file_ext, 'audio/wav')

        emotion_module = DSPyEmotionAnalysisModule()
        emotions = await asyncio.to_thread(
            emotion_module.forward,
            audio_base64_string=audio_base64,
            audio_mime_type=mime_type,
            transcript=transcript
        )
        logger.info(f"DSPy emotion analysis successful for {audio_path}")
        return emotions
    except FileNotFoundError:
        logger.error(f"Audio file not found for emotion analysis: {audio_path}")
        raise # Or return default error emotion list
    except Exception as e:
        logger.error(f"Error during DSPy emotion analysis for {audio_path}: {e}", exc_info=True)
        # Fallback to default structure
        return [EmotionDetail(emotion="error_processing", score=0.0, timestamp_start=None, timestamp_end=None)]
