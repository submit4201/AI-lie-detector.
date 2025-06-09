# backend/services/manipulation_service.py
import logging
from typing import Dict, Any, Optional
import json # Added for DSPy module
from backend.models import ManipulationAssessment
# from backend.services.gemini_service import GeminiService # No longer needed for direct calls
from backend.dspy_modules import DSPyManipulationAnalyzer # Import the new DSPy module
from backend.services.gemini_service import GeminiService # Import to ensure it's initialized

logger = logging.getLogger(__name__)

class ManipulationService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        # Ensure GeminiService is initialized, which should configure DSPy LM.
        # If gemini_service is passed, assume it's already initialized.
        # If not passed, instantiate it to trigger __init__ (and thus DSPy setup).
        self.gemini_service_instance = gemini_service if gemini_service else GeminiService()
        self.dspy_analyzer = DSPyManipulationAnalyzer()

        # Verify DSPy LM configuration after GeminiService initialization
        import dspy
        if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
            logger.warning("DSPy LM may not have been configured by GeminiService init as expected. Analysis might rely on fallbacks or fail if no API key.")
        else:
            logger.info("ManipulationService initialized; DSPy LM should be configured by GeminiService.")


    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> ManipulationAssessment:
        if not transcript:
            return ManipulationAssessment()

        # The prompt is now managed by DSPySignature in dspy_modules.py

        try:
            # Use the DSPy module for analysis
            # The DSPy module's forward method is synchronous.
            # If DSPy's LM calls are inherently async or need to be run in an executor:
            # This might require an async wrapper around the dspy_analyzer.forward call
            # or making dspy_analyzer.forward async if dspy.Predict supports it.
            # For now, assuming dspy.Predict's call within forward is blocking and compatible
            # with being called from an async method directly if the underlying HTTP calls are managed by dspy's LM.
            # Let's assume for now it's okay to call directly. If it blocks, it needs `await asyncio.to_thread(...)`

            # DSPy LM is now expected to be configured globally by GeminiService.
            # We still need to ensure it *is* configured before proceeding.
            import dspy
            if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                logger.error("DSPy LM not configured globally. ManipulationService cannot proceed with DSPy analysis.")
                # Attempting to initialize GeminiService here to trigger config if not already done.
                # This is a bit of a workaround; ideally, app startup ensures GeminiService is initialized.
                from backend.services.gemini_service import GeminiService
                GeminiService() # Initialize to trigger DSPy setup if not already done.
                if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                     logger.error("DSPy LM still not configured after attempting GeminiService init. Falling back.")
                     return self._fallback_text_analysis(transcript)
                else:
                    logger.info("DSPy LM was configured after GeminiService explicit initialization.")

            # Assuming dspy_analyzer.forward is synchronous
            # To run synchronous code in an async function, use asyncio.to_thread
            import asyncio
            assessment = await asyncio.to_thread(self.dspy_analyzer.forward, transcript, session_context)
            return assessment

        except Exception as e:
            logger.error(f"Error in ManipulationService DSPy call: {e}", exc_info=True)
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
