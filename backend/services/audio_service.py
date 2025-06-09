import speech_recognition as sr
from pydub import AudioSegment
from typing import List, Dict, Any
import logging

# Assuming EMOTION_CLASSIFIER is initialized in config.py and imported
# This classifier is expected to be a Hugging Face pipeline object.
from config import EMOTION_CLASSIFIER

logger = logging.getLogger(__name__) # Logger for this module

def assess_audio_quality(audio_segment: AudioSegment) -> Dict[str, Any]:
    """
    Assess the quality of an audio segment to determine its suitability for analysis.

    The quality is judged based on duration, sample rate, loudness, and number of channels.
    A simple scoring system is used to provide a quantitative measure of quality.

    Args:
        audio_segment: An AudioSegment object from Pydub representing the audio.

    Returns:
        A dictionary containing various quality metrics:
        - "duration": Duration of the audio in seconds.
        - "sample_rate": Sample rate in Hz.
        - "channels": Number of audio channels (e.g., 1 for mono, 2 for stereo).
        - "loudness": Average loudness in dBFS (decibels relative to full scale).
        - "quality_score": An overall score from 0 to 100, where higher is better.
    """
    quality_metrics = {
        "duration": len(audio_segment) / 1000.0,  # Convert milliseconds to seconds
        "sample_rate": audio_segment.frame_rate,
        "channels": audio_segment.channels,
        "loudness": audio_segment.dBFS, # Average loudness
        "quality_score": 0 # Initialize quality score
    }

    # Calculate quality score based on predefined criteria.
    # Each criterion met adds 25 points to the score.
    if quality_metrics["duration"] >= 1.0:  # Audio should be at least 1 second long
        quality_metrics["quality_score"] += 25
    if quality_metrics["sample_rate"] >= 16000:  # 16kHz is generally considered good for speech
        quality_metrics["quality_score"] += 25
    if quality_metrics["loudness"] > -30:  # Audio should not be too quiet (e.g. > -30 dBFS)
        quality_metrics["quality_score"] += 25
    if quality_metrics["channels"] >= 1:  # Audio must have at least one channel
        quality_metrics["quality_score"] += 25

    logger.info(f"Audio quality assessed: {quality_metrics}")
    return quality_metrics

def transcribe_audio(wav_audio_path: str) -> str:
    """
    Transcribes audio from a given WAV file using Google's Speech Recognition API.

    Args:
        wav_audio_path: The file path to the WAV audio file.

    Returns:
        The transcribed text string.

    Raises:
        sr.UnknownValueError: If the speech recognition service could not understand the audio.
        sr.RequestError: If there was an issue with the speech recognition service request
                         (e.g., network issues, API key problems).
    """
    recognizer = sr.Recognizer() # Initialize the speech recognizer
    with sr.AudioFile(wav_audio_path) as source: # Open the WAV file
        audio_data = recognizer.record(source)  # Read the entire audio file
        try:
            # Recognize speech using Google Speech Recognition
            transcript = recognizer.recognize_google(audio_data)
            # Log a snippet of the transcript for monitoring
            logger.info(f"Transcript generated (first 100 chars): \"{transcript[:100]}...\"")
            return transcript
        except sr.UnknownValueError as e:
            # This error is raised when Google Speech Recognition cannot understand the audio
            logger.warning(f"Speech recognition: Could not understand audio from file {wav_audio_path}. Error: {e}")
            raise  # Re-raise the exception to be handled by the calling function
        except sr.RequestError as e:
            # This error is raised for issues with the Google Speech Recognition service itself
            # (e.g., network connectivity, API limits)
            logger.error(f"Speech recognition service error for file {wav_audio_path}: {e}")
            raise  # Re-raise the exception

def analyze_emotion(text: str) -> List[Dict[str, Any]]:
    """
    Analyzes emotions from the input text using a pre-loaded Hugging Face text classification pipeline.

    The function expects `EMOTION_CLASSIFIER` to be a pipeline object capable of
    returning a list of dictionaries, where each dictionary contains 'label' and 'score'
    for an emotion.

    Args:
        text: The input string (e.g., a transcript) to analyze for emotions.

    Returns:
        A list of dictionaries, where each dictionary represents an emotion and its score.
        Example: `[{'label': 'sadness', 'score': 0.9...}, {'label': 'joy', 'score': 0.0...}, ...]`.
        Returns a default "neutral" emotion with an error message if the classifier is not available
        or if an unexpected output structure is received, or if an analysis error occurs.
    """
    if not EMOTION_CLASSIFIER:
        logger.warning("Emotion classifier (EMOTION_CLASSIFIER) not available. Returning default emotion.")
        return [{"label": "neutral", "score": 0.5, "error": "Emotion classifier not available"}]

    try:
        # Perform emotion analysis using the configured Hugging Face pipeline
        emotions_output = EMOTION_CLASSIFIER(text)

        # The Hugging Face pipeline, when `return_all_scores=True` or `top_k` is set,
        # typically returns a list containing another list of dictionaries:
        # Example: [[{'label': 'sadness', 'score': 0.9...}, {'label': 'joy', 'score': 0.0...}, ...]]
        if isinstance(emotions_output, list) and len(emotions_output) > 0 and isinstance(emotions_output[0], list):
            # This is the expected structure when the pipeline is configured for multiple scores.
            logger.debug(f"Emotions analyzed for text (first 50 chars): \"{text[:50]}...\" Result: {emotions_output[0]}")
            return emotions_output[0]
        elif isinstance(emotions_output, list) and len(emotions_output) > 0 and isinstance(emotions_output[0], dict):
             # This structure might occur if top_k=1 or if the model returns a single list of dicts by default.
            logger.debug(f"Emotions analyzed (single list) for text (first 50 chars): \"{text[:50]}...\" Result: {emotions_output}")
            return emotions_output
        else:
            # Log a warning if the output structure is not what's expected.
            logger.warning(f"Unexpected emotion classifier output structure: {type(emotions_output)}. Input text (first 50 chars): \"{text[:50]}...\". Using default.")
            return [{"label": "neutral", "score": 0.5, "error": "Unexpected output structure from emotion classifier"}]

    except Exception as e:
        # Catch any other exceptions during emotion analysis.
        logger.warning(f"Emotion analysis failed for text (first 50 chars): \"{text[:50]}...\". Error: {e}", exc_info=True)
        return [{"label": "neutral", "score": 0.5, "error": f"Emotion analysis failed: {str(e)}"}]
