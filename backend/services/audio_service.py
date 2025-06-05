import speech_recognition as sr
from pydub import AudioSegment
from typing import List, Dict, Any
import logging

# Assuming EMOTION_CLASSIFIER is initialized in config.py and imported
from backend.config import EMOTION_CLASSIFIER

logger = logging.getLogger(__name__)

def assess_audio_quality(audio_segment: AudioSegment) -> Dict[str, Any]:
    """Assess the quality of the audio for better analysis"""
    quality_metrics = {
        "duration": len(audio_segment) / 1000.0,  # seconds
        "sample_rate": audio_segment.frame_rate,
        "channels": audio_segment.channels,
        "loudness": audio_segment.dBFS,
        "quality_score": 0
    }

    # Calculate quality score
    if quality_metrics["duration"] >= 1.0:  # At least 1 second
        quality_metrics["quality_score"] += 25
    if quality_metrics["sample_rate"] >= 16000:  # Good sample rate
        quality_metrics["quality_score"] += 25
    if quality_metrics["loudness"] > -30:  # Not too quiet
        quality_metrics["quality_score"] += 25
    if quality_metrics["channels"] >= 1:  # Has audio channels
        quality_metrics["quality_score"] += 25

    return quality_metrics

def transcribe_audio(wav_audio_path: str) -> str:
    """
    Transcribes audio from a WAV file.
    Raises sr.UnknownValueError if audio is unintelligible.
    Raises sr.RequestError for speech recognition service issues.
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            transcript = recognizer.recognize_google(audio_data)
            logger.info(f"Transcript generated: \"{transcript[:100]}...\"")
            return transcript
        except sr.UnknownValueError as e:
            logger.warning(f"Speech recognition: Could not understand audio from file {wav_audio_path}.")
            raise  # Re-raise to be handled by the caller
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error for file {wav_audio_path}: {e}")
            raise  # Re-raise to be handled by the caller

def analyze_emotion(text: str) -> List[Dict[str, Any]]:
    """
    Analyzes emotion from text using the preloaded classifier.
    Returns a list of emotion scores or a default if analysis fails.
    """
    if not EMOTION_CLASSIFIER:
        logger.warning("Emotion classifier not available. Returning default emotion.")
        return [{"label": "neutral", "score": 0.5, "error": "Classifier not available"}]

    try:
        emotions_output = EMOTION_CLASSIFIER(text)
        # The pipeline with return_all_scores=True and top_k typically returns a list containing a list of dicts:
        # [[{'label': 'sadness', 'score': 0.9...}, {'label': 'joy', 'score': 0.0...}, ...]]
        if isinstance(emotions_output, list) and len(emotions_output) > 0 and isinstance(emotions_output[0], list):
            # This is the expected structure when top_k is used (even if top_k covers all labels)
            return emotions_output[0]
        elif isinstance(emotions_output, list) and len(emotions_output) > 0 and isinstance(emotions_output[0], dict):
             # This might happen if top_k=1 or not specified and model returns single list of dicts
            return emotions_output
        else:
            logger.warning(f"Unexpected emotion classifier output structure: {type(emotions_output)}. Using default.")
            return [{"label": "neutral", "score": 0.5, "error": "Unexpected output structure"}]

    except Exception as e:
        logger.warning(f"Emotion analysis failed: {e}")
        return [{"label": "neutral", "score": 0.5, "error": str(e)}]
