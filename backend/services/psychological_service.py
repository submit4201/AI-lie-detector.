import logging
from typing import Dict, Any, Optional
import json
import asyncio # For asyncio.to_thread

from backend.models import PsychologicalAnalysis
from backend.services.gemini_service import GeminiService # To ensure it's initialized for DSPy config
from backend.dspy_modules import DSPyPsychologicalAnalyzer # Import the new DSPy module

logger = logging.getLogger(__name__)

class PsychologicalService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        # Ensure GeminiService is initialized, which should configure DSPy LM.
        self.gemini_service_instance = gemini_service if gemini_service else GeminiService()
        self.dspy_analyzer = DSPyPsychologicalAnalyzer()

        import dspy # For checking dspy.settings.lm
        if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
            logger.warning("DSPy LM may not have been configured by GeminiService init as expected in PsychologicalService. Analysis might rely on fallbacks.")
        else:
            logger.info("PsychologicalService initialized; DSPy LM should be configured by GeminiService.")

    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> PsychologicalAnalysis:
        if not transcript:
            return PsychologicalAnalysis()

        try:
            # Check DSPy LM configuration
            import dspy
            if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                logger.error("DSPy LM not configured globally. PsychologicalService cannot proceed with DSPy analysis.")
                GeminiService() # Attempt to trigger config
                if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                     logger.error("DSPy LM still not configured after attempting GeminiService init. Falling back.")
                     return self._fallback_analysis(transcript, "DSPy LM not configured.")
                else:
                    logger.info("DSPy LM was configured after GeminiService explicit initialization in PsychologicalService.analyze.")

            # Use the DSPy module for analysis
            assessment = await asyncio.to_thread(self.dspy_analyzer.forward, transcript, session_context)
            return assessment

        except Exception as e:
            logger.error(f"Error in PsychologicalService DSPy call: {e}", exc_info=True)
            return self._fallback_analysis(transcript, f"DSPy module error: {e}")

    def _fallback_analysis(self, transcript: str, error_message: Optional[str] = None) -> PsychologicalAnalysis:
        logger.info(f"Performing fallback psychological analysis for transcript snippet: {transcript[:100]}...")
        explanation = "Fallback analysis due to error or unconfigured DSPy LM."
        if error_message:
            explanation += f" Error: {error_message}"

        return PsychologicalAnalysis(
            psychological_summary=explanation
            # Other fields will use their defaults from Pydantic model
        )
