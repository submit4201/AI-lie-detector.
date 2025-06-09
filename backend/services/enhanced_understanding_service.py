import logging
from typing import Dict, Any, Optional
import json
import asyncio # For asyncio.to_thread

from backend.models import EnhancedUnderstanding
from backend.services.gemini_service import GeminiService # To ensure it's initialized for DSPy config
from backend.dspy_modules import DSPyEnhancedUnderstandingAnalyzer # Import the new DSPy module

logger = logging.getLogger(__name__)

class EnhancedUnderstandingService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        # Ensure GeminiService is initialized, which should configure DSPy LM.
        self.gemini_service_instance = gemini_service if gemini_service else GeminiService()
        self.dspy_analyzer = DSPyEnhancedUnderstandingAnalyzer()

        import dspy # For checking dspy.settings.lm
        if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
            logger.warning("DSPy LM may not have been configured by GeminiService init as expected in EnhancedUnderstandingService. Analysis might rely on fallbacks.")
        else:
            logger.info("EnhancedUnderstandingService initialized; DSPy LM should be configured by GeminiService.")

    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> EnhancedUnderstanding:
        if not transcript:
            return EnhancedUnderstanding()

        try:
            # Check DSPy LM configuration
            import dspy
            if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                logger.error("DSPy LM not configured globally. EnhancedUnderstandingService cannot proceed with DSPy analysis.")
                GeminiService() # Attempt to trigger config
                if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                     logger.error("DSPy LM still not configured after attempting GeminiService init. Falling back.")
                     return self._fallback_analysis(transcript, "DSPy LM not configured.")
                else:
                    logger.info("DSPy LM was configured after GeminiService explicit initialization in EnhancedUnderstandingService.analyze.")

            # Use the DSPy module for analysis
            assessment = await asyncio.to_thread(self.dspy_analyzer.forward, transcript, session_context)
            return assessment

        except Exception as e:
            logger.error(f"Error in EnhancedUnderstandingService DSPy call: {e}", exc_info=True)
            return self._fallback_analysis(transcript, f"DSPy module error: {e}")

    def _fallback_analysis(self, transcript: str, error_message: Optional[str] = None) -> EnhancedUnderstanding:
        logger.info(f"Performing fallback enhanced understanding analysis for transcript snippet: {transcript[:100]}...")
        explanation = "Fallback analysis due to error or unconfigured DSPy LM."
        if error_message:
            explanation += f" Error: {error_message}"

        # Basic fallback, returning an empty or minimally populated EnhancedUnderstanding object
        return EnhancedUnderstanding(
            summary_of_understanding="Fallback: Analysis could not be performed.",
            key_inconsistencies_analysis=explanation,
            areas_of_evasiveness_analysis=explanation,
            suggested_follow_up_questions_analysis=explanation,
            fact_checking_analysis=explanation,
            deep_dive_analysis=explanation
            # Other fields will use their defaults from Pydantic model
        )
