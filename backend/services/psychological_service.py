# backend/services/psychological_service.py
import logging
import json
from typing import Dict, Any
from backend.models import PsychologicalAnalysis # Ensure this import is correct
from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class PsychologicalService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    def _fallback_analysis(self, transcript_snippet: str) -> PsychologicalAnalysis:
        logger.warning(f"PsychologicalService: LLM call failed or returned malformed data for transcript snippet: {transcript_snippet}. Falling back to default.")
        return PsychologicalAnalysis()

    async def analyze(self, transcript: str, session_context: Dict[str, Any] = None) -> PsychologicalAnalysis:
        """
        Performs psychological analysis on the given transcript using an LLM.
        """
        transcript_snippet = transcript[:500]
        logger.info(f"Performing psychological analysis for transcript snippet: {transcript_snippet}...")

        prompt = f"""
Analyze the speaker's psychological state based on the following transcript.
Transcript:
"{transcript}"

Based on the transcript, provide a JSON object with the following fields:
- "cognitive_load": A string assessing the speaker's cognitive load (e.g., "low", "moderate", "high", "overwhelmed"). Provide a brief justification.
- "emotional_regulation": A string assessing the speaker's emotional regulation capabilities (e.g., "well-regulated", "shows signs of dysregulation", "struggling with emotional control"). Provide a brief justification.
- "personality_traits_inferred": A list of strings, where each string describes an inferred personality trait (e.g., "appears introverted", "shows extroverted tendencies", "seems anxious", "displays confidence").
- "psychological_summary": A brief textual summary of the overall psychological assessment.
- "stress_indicators": A list of strings identifying specific phrases or cues in the transcript that indicate stress or pressure.
- "coping_mechanisms_observed": A list of strings describing any observed coping mechanisms (e.g., "uses humor to deflect", "rationalizes extensively", "seeks reassurance").
- "speech_coherence_level": A string describing the coherence of speech (e.g., "highly coherent", "mostly coherent with minor digressions", "shows signs of incoherence").

Return ONLY the JSON object.
Example:
{{
  "cognitive_load": "moderate - speaker pauses frequently, suggesting careful thought or difficulty processing.",
  "emotional_regulation": "well-regulated - maintains a calm tone despite discussing sensitive topics.",
  "personality_traits_inferred": ["appears reflective", "cautious in responses"],
  "psychological_summary": "The speaker seems to be under moderate cognitive load but is managing emotions effectively. They present as a reflective and cautious individual.",
  "stress_indicators": ["repeated use of 'um' and 'uh'", "mentions feeling 'a bit overwhelmed'"],
  "coping_mechanisms_observed": ["uses self-deprecating humor"],
  "speech_coherence_level": "mostly coherent with minor digressions"
}}
"""
        try:
            raw_response = await self.gemini_service.query_gemini_for_raw_json(prompt)
            if raw_response:
                return PsychologicalAnalysis(**raw_response)
            else:
                logger.warning(f"PsychologicalService: Received no response from LLM for transcript snippet: {transcript_snippet}.")
                return self._fallback_analysis(transcript_snippet)
        except (json.JSONDecodeError, TypeError, Exception) as e:
            logger.error(f"PsychologicalService: Error processing LLM response for transcript snippet: {transcript_snippet}. Error: {e}")
            return self._fallback_analysis(transcript_snippet)

# psychological_service = PsychologicalService() # Commented out global instantiation
