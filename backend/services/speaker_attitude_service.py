import logging
from typing import Dict, Any, Optional
import json
import asyncio # For asyncio.to_thread

from backend.models import SpeakerAttitude
from backend.services.gemini_service import GeminiService # To ensure it's initialized for DSPy config
from backend.dspy_modules import DSPySpeakerAttitudeAnalyzer # Import the new DSPy module

logger = logging.getLogger(__name__)

class SpeakerAttitudeService:
    def __init__(self, gemini_service: Optional[GeminiService] = None): # Allow None for flexibility, will be initialized if None
        # Ensure GeminiService is initialized, which should configure DSPy LM.
        self.gemini_service_instance = gemini_service if gemini_service else GeminiService()
        self.dspy_analyzer = DSPySpeakerAttitudeAnalyzer()

        import dspy # For checking dspy.settings.lm
        if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
            logger.warning("DSPy LM may not have been configured by GeminiService init as expected in SpeakerAttitudeService. Analysis might rely on fallbacks.")
        else:
            logger.info("SpeakerAttitudeService initialized; DSPy LM should be configured by GeminiService.")


    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> SpeakerAttitude:
        if not transcript:
            return SpeakerAttitude()

        try:
            # Check DSPy LM configuration
            import dspy
            if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                logger.error("DSPy LM not configured globally. SpeakerAttitudeService cannot proceed with DSPy analysis.")
                # Attempt to initialize GeminiService here to trigger config if not already done.
                GeminiService() # Initialize to trigger DSPy setup if not already done.
                if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                     logger.error("DSPy LM still not configured after attempting GeminiService init. Falling back.")
                     return self._fallback_analysis(transcript, "DSPy LM not configured.")
                else:
                    logger.info("DSPy LM was configured after GeminiService explicit initialization in SpeakerAttitudeService.analyze.")

            # Use the DSPy module for analysis
            assessment = await asyncio.to_thread(self.dspy_analyzer.forward, transcript, session_context)
            return assessment

        except Exception as e:
            logger.error(f"Error in SpeakerAttitudeService DSPy call: {e}", exc_info=True)
            return self._fallback_analysis(transcript, f"DSPy module error: {e}")

    def _fallback_analysis(self, transcript: str, error_message: Optional[str] = None) -> SpeakerAttitude:
        logger.info(f"Performing fallback speaker attitude analysis for transcript: {transcript[:100]}...")
        explanation = "Fallback analysis due to error or unconfigured DSPy LM."
        if error_message:
            explanation += f" Error: {error_message}"

        return SpeakerAttitude(
            dominant_attitude="Neutral",
            attitude_scores={"neutral": 1.0}, # Ensure this matches Pydantic model if it expects Dict[str, float]
            respect_level="Medium",
            respect_level_score=0.5,
            respect_level_score_analysis=explanation,
            formality_score=0.5,
            formality_assessment="Mixed",
            politeness_score=0.5,
            politeness_assessment="Neutral"
        )
