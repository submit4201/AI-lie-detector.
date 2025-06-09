# backend/services/manipulation_service.py
import logging
from typing import Dict, Any, Optional
from backend.models import ManipulationAssessment
from backend.services.gemini_service import GeminiService # Assuming GeminiService will be here or accessible
import json

logger = logging.getLogger(__name__)

class ManipulationService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini_service = gemini_service if gemini_service else GeminiService()

    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> ManipulationAssessment:
        if not transcript:
            return ManipulationAssessment()

        prompt = f"""Analyze the following transcript for signs of manipulation.
Transcript:
"{transcript}"

Consider the following aspects and provide your analysis as a JSON object matching the ManipulationAssessment model:
1.  is_manipulative (bool): Overall assessment of whether manipulation is present.
2.  manipulation_score (float, 0.0 to 1.0): Likelihood of manipulation.
3.  manipulation_techniques (List[str]): Specific techniques identified (e.g., "Gaslighting", "Guilt-tripping", "Love bombing", "Appeal to pity", "Intimidation", "Minimization").
4.  manipulation_confidence (float, 0.0 to 1.0): Confidence in this assessment.
5.  manipulation_explanation (str): Brief explanation of why the assessment was made, citing examples from the text if possible.
6.  manipulation_score_analysis (str): Detailed analysis of the manipulation score.

JSON structure:
{{
  "is_manipulative": bool,
  "manipulation_score": float,
  "manipulation_techniques": ["technique1", "technique2"],
  "manipulation_confidence": float,
  "manipulation_explanation": "...",
  "manipulation_score_analysis": "..."
}}
If a field cannot be determined, use a sensible default (e.g., false, 0.0, empty list, "Analysis not available").
"""

        try:
            raw_analysis = await self.gemini_service.query_gemini_for_raw_json(prompt)
            if raw_analysis:
                data = json.loads(raw_analysis)
                # Ensure all fields from the model are present, with defaults if missing
                return ManipulationAssessment(
                    is_manipulative=data.get("is_manipulative", False),
                    manipulation_score=data.get("manipulation_score", 0.0),
                    manipulation_techniques=data.get("manipulation_techniques", []),
                    manipulation_confidence=data.get("manipulation_confidence", 0.0),
                    manipulation_explanation=data.get("manipulation_explanation", "Analysis not available."),
                    manipulation_score_analysis=data.get("manipulation_score_analysis", "Analysis not available.")
                )
            else:
                return self._fallback_text_analysis(transcript)
        except Exception as e:
            logger.error(f"Error in ManipulationService LLM call: {e}")
            return self._fallback_text_analysis(transcript)

    def _fallback_text_analysis(self, transcript: str) -> ManipulationAssessment:
        logger.info(f"Performing fallback manipulation assessment for transcript snippet: {transcript[:100]}...")
        techniques = []
        explanation = "No significant manipulative tactics detected in this fallback analysis."
        score = 0.0
        is_manipulative = False
        confidence = 0.3 # Low confidence for fallback

        if "you always" in transcript.lower() or "you never" in transcript.lower():
            techniques.append("Overgeneralization/Absolutes")
            score += 0.2
            is_manipulative = True
        if "if you really loved me" in transcript.lower() or "a good person would" in transcript.lower():
            techniques.append("Guilt-tripping/Moralizing")
            score += 0.3
            is_manipulative = True
        
        if techniques:
            explanation = f"Fallback analysis detected potential manipulative tactics: {', '.join(techniques)}."
        
        score = min(score, 1.0)

        return ManipulationAssessment(
            is_manipulative=is_manipulative,
            manipulation_score=score,
            manipulation_techniques=techniques,
            manipulation_confidence=confidence,
            manipulation_explanation=explanation,
            manipulation_score_analysis=f"Fallback score ({score:.2f}) implies low/moderate manipulation likelihood based on keyword matching."
        )

# Remove the global instance if services are to be instantiated by the main pipeline
# manipulation_service = ManipulationService()
