# backend/services/speaker_attitude_service.py
import logging
import json
from typing import Dict, Any, Optional
from backend.models import SpeakerAttitude # Ensure this import is correct and SpeakerAttitude is defined in models.py
from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class SpeakerAttitudeService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    def _fallback_analysis(self, transcript_snippet: str) -> SpeakerAttitude:
        logger.warning(f"SpeakerAttitudeService: LLM call failed or returned malformed data for transcript snippet: {transcript_snippet}. Falling back to default.")
        return SpeakerAttitude() # Relies on default_factory or default values in Pydantic model

    async def analyze(self, transcript: str, session_context: Dict[str, Any] = None) -> SpeakerAttitude:
        """
        Performs speaker attitude analysis on the given transcript using an LLM.
        """
        transcript_snippet = transcript[:500] # Use a snippet for brevity in logs if needed
        logger.info(f"Performing speaker attitude analysis for transcript snippet: {transcript_snippet}...")

        prompt = f"""
Analyze the speaker's attitude in the following transcript.
Transcript:
"{transcript}"

Based on the transcript, provide a JSON object with the following fields:
- "respect_level_score": An integer score from 0 to 100 indicating the level of respect shown by the speaker.
- "sarcasm_detected": A boolean indicating if sarcasm is detected.
- "sarcasm_confidence_score": A float score from 0.0 to 1.0 indicating the confidence in sarcasm detection.
- "tone_indicators_respect_sarcasm": A list of strings, where each string is a textual cue or indicator from the transcript supporting the respect and sarcasm assessment.
- "attitude_summary": A brief textual summary of the overall speaker attitude.
- "emotional_tone": A string describing the primary emotional tone (e.g., "neutral", "angry", "joyful", "anxious", "frustrated").
- "confidence_level_speech": A string describing the speaker's confidence level (e.g., "confident", "hesitant", "assertive", "timid").
- "engagement_level": A string describing the speaker's engagement level (e.g., "engaged", "disinterested", "bored", "attentive").

Return ONLY the JSON object.
Example:
{{
  "respect_level_score": 75,
  "sarcasm_detected": false,
  "sarcasm_confidence_score": 0.1,
  "tone_indicators_respect_sarcasm": ["Used polite phrases like 'please'", "Maintained a calm tone"],
  "attitude_summary": "The speaker was generally respectful and engaged, with no clear signs of sarcasm.",
  "emotional_tone": "neutral",
  "confidence_level_speech": "confident",
  "engagement_level": "engaged"
}}
"""
        try:
            raw_response = await self.gemini_service.query_gemini_for_raw_json(prompt)
            if raw_response:
                return SpeakerAttitude(**raw_response)
            else:
                logger.warning(f"SpeakerAttitudeService: Received no response from LLM for transcript snippet: {transcript_snippet}.")
                return self._fallback_analysis(transcript_snippet)
        except (json.JSONDecodeError, TypeError, Exception) as e:
            logger.error(f"SpeakerAttitudeService: Error processing LLM response for transcript snippet: {transcript_snippet}. Error: {e}")
            return self._fallback_analysis(transcript_snippet)

# speaker_attitude_service = SpeakerAttitudeService() # Commented out global instantiation
