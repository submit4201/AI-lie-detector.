# backend/services/enhanced_understanding_service.py
import logging
import json
from typing import Dict, Any
from backend.models import EnhancedUnderstanding # Ensure this import is correct
from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class EnhancedUnderstandingService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    def _fallback_analysis(self, transcript_snippet: str) -> EnhancedUnderstanding:
        logger.warning(f"EnhancedUnderstandingService: LLM call failed or returned malformed data for transcript snippet: {transcript_snippet}. Falling back to default.")
        return EnhancedUnderstanding()

    async def analyze(self, transcript: str, session_context: Dict[str, Any] = None) -> EnhancedUnderstanding:
        """
        Performs enhanced understanding analysis on the given transcript using an LLM.
        """
        transcript_snippet = transcript[:500]
        logger.info(f"Performing enhanced understanding analysis for transcript snippet: {transcript_snippet}...")

        prompt = f"""
Analyze the following transcript for enhanced understanding, focusing on inconsistencies, evasiveness, and contextual flags.
Transcript:
"{transcript}"

Session Context (if any relevant data was provided, otherwise this might be empty or generic):
"{session_context}"

Based on the transcript and session context, provide a JSON object with the following fields:
- "key_inconsistencies": A list of strings, where each string describes a key inconsistency found in the speaker's statements. Include specific examples from the transcript.
- "areas_of_evasiveness": A list of strings, where each string describes an area where the speaker appears to be evasive or avoidant. Include specific examples.
- "contextual_flags": A list of strings, where each string highlights a contextual flag (e.g., contradictions with known facts if provided in context, unusual statements given the context).
- "understanding_summary": A brief textual summary of the enhanced understanding insights.
- "depth_of_detail": A string assessing the level of detail provided by the speaker (e.g., "superficial", "moderate detail", "highly detailed").
- "speaker_certainty_on_claims": A string assessing the speaker's certainty when making claims (e.g., "assertive and certain", "appears uncertain", "mixed certainty").
- "use_of_loaded_language": A boolean indicating if loaded or emotionally charged language is used.
- "loaded_language_examples": A list of strings, providing examples of loaded language if detected.

Return ONLY the JSON object.
Example:
{{
  "key_inconsistencies": ["Speaker initially said they were at home, later mentioned being at a cafe."],
  "areas_of_evasiveness": ["When asked about their whereabouts, speaker changed the subject."],
  "contextual_flags": ["Speaker's claim of ignorance contradicts their previously stated expertise."],
  "understanding_summary": "The speaker showed some inconsistencies and evasiveness, particularly around their location and activities. Loaded language was minimal.",
  "depth_of_detail": "moderate detail",
  "speaker_certainty_on_claims": "mixed certainty",
  "use_of_loaded_language": false,
  "loaded_language_examples": []
}}
"""
        try:
            raw_response = await self.gemini_service.query_gemini_for_raw_json(prompt)
            if raw_response:
                return EnhancedUnderstanding(**raw_response)
            else:
                logger.warning(f"EnhancedUnderstandingService: Received no response from LLM for transcript snippet: {transcript_snippet}.")
                return self._fallback_analysis(transcript_snippet)
        except (json.JSONDecodeError, TypeError, Exception) as e:
            logger.error(f"EnhancedUnderstandingService: Error processing LLM response for transcript snippet: {transcript_snippet}. Error: {e}")
            return self._fallback_analysis(transcript_snippet)

# enhanced_understanding_service = EnhancedUnderstandingService() # Commented out global instantiation
