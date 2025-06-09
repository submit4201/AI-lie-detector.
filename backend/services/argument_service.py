# backend/services/argument_service.py
import logging
from typing import Dict, Any, Optional, List
from backend.models import ArgumentAnalysis
from backend.services.gemini_service import GeminiService # Assuming GeminiService will be here or accessible
import json

logger = logging.getLogger(__name__)

class ArgumentService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini_service = gemini_service if gemini_service else GeminiService()

    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> ArgumentAnalysis:
        if not transcript:
            return ArgumentAnalysis()

        prompt = f"""Analyze the following transcript for its argument structure.
Transcript:
"{transcript}"

Identify and evaluate the arguments present. Provide your analysis as a JSON object matching the ArgumentAnalysis model:
1.  arguments_present (bool): Are there identifiable arguments (claims supported by reasons/evidence)?
2.  key_arguments (List[Dict[str, str]]): List of key arguments, each as a dict with "claim" and "evidence" keys (e.g., [{{"claim": "...", "evidence": "..."}}]).
3.  argument_strength (float, 0.0 to 1.0): Overall strength of the arguments.
4.  fallacies_detected (List[str]): Any logical fallacies identified (e.g., "Ad hominem", "Straw man").
5.  argument_summary (str): A brief summary of the main arguments.
6.  argument_structure_rating (float, 0.0 to 1.0): Rating of how well-structured the arguments are.
7.  argument_structure_analysis (str): Detailed analysis of the argument structure.

JSON structure:
{{
  "arguments_present": bool,
  "key_arguments": [{{"claim": "text", "evidence": "text"}}],
  "argument_strength": float,
  "fallacies_detected": ["fallacy1"],
  "argument_summary": "...",
  "argument_structure_rating": float,
  "argument_structure_analysis": "..."
}}
If a field cannot be determined, use a sensible default.
"""

        try:
            raw_analysis = await self.gemini_service.query_gemini_for_raw_json(prompt)
            if raw_analysis:
                data = json.loads(raw_analysis)
                return ArgumentAnalysis(
                    arguments_present=data.get("arguments_present", False),
                    key_arguments=data.get("key_arguments", []),
                    argument_strength=data.get("argument_strength", 0.0),
                    fallacies_detected=data.get("fallacies_detected", []),
                    argument_summary=data.get("argument_summary", "Analysis not available."),
                    argument_structure_rating=data.get("argument_structure_rating", 0.0),
                    argument_structure_analysis=data.get("argument_structure_analysis", "Analysis not available.")
                )
            else:
                return self._fallback_text_analysis(transcript)
        except Exception as e:
            logger.error(f"Error in ArgumentService LLM call: {e}")
            return self._fallback_text_analysis(transcript)

    def _fallback_text_analysis(self, transcript: str) -> ArgumentAnalysis:
        logger.info(f"Performing fallback argument analysis for transcript snippet: {transcript[:100]}...")
        key_args: List[Dict[str, str]] = []
        fallacies: List[str] = []
        summary = "No clear arguments identified by fallback analysis."
        strength = 0.0
        structure_rating = 0.0
        present = False

        if "because" in transcript.lower() and len(transcript.split('.')) > 1:
            present = True
            # Simplistic claim/evidence split for fallback
            parts = transcript.lower().split("because", 1)
            if len(parts) == 2:
                 key_args.append({"claim": parts[0].strip(), "evidence": parts[1].strip()})
            strength += 0.3
            structure_rating += 0.2
            summary = "Fallback: Basic argument structure (claim with 'because') detected."
        
        if "therefore" in transcript.lower() or "so it follows" in transcript.lower():
            present = True
            strength += 0.2
            structure_rating += 0.2
            if not key_args: # Add a general argument if none from 'because'
                key_args.append({"claim": "A conclusion was likely drawn.", "evidence": "Presence of concluding phrases."}) 

        if len(transcript) < 50 and present: # Very short argument
            strength = max(0.1, strength - 0.2)
            structure_rating = max(0.1, structure_rating - 0.2)
            summary += " Argument is very brief."
        elif not present and len(transcript) > 100:
            summary = "Fallback: Transcript is substantial but lacks clear argumentative keywords."

        return ArgumentAnalysis(
            arguments_present=present,
            key_arguments=key_args,
            argument_strength=min(strength, 1.0),
            fallacies_detected=fallacies,
            argument_summary=summary,
            argument_structure_rating=min(structure_rating, 1.0),
            argument_structure_analysis="Fallback analysis based on keyword matching for argument structure."
        )

# argument_service = ArgumentService()
