import logging
from typing import Dict, Any, Optional
import json
import asyncio # For asyncio.to_thread

from backend.models import ArgumentAnalysis
from backend.services.gemini_service import GeminiService # To ensure it's initialized for DSPy config
from backend.dspy_modules import DSPyArgumentAnalyzer # Import the new DSPy module

logger = logging.getLogger(__name__)

class ArgumentService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        # Ensure GeminiService is initialized, which should configure DSPy LM.
        self.gemini_service_instance = gemini_service if gemini_service else GeminiService()
        self.dspy_analyzer = DSPyArgumentAnalyzer()

        import dspy # For checking dspy.settings.lm
        if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
            logger.warning("DSPy LM may not have been configured by GeminiService init as expected in ArgumentService. Analysis might rely on fallbacks.")
        else:
            logger.info("ArgumentService initialized; DSPy LM should be configured by GeminiService.")


    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> ArgumentAnalysis:
        if not transcript:
            return ArgumentAnalysis()

        try:
            # Check DSPy LM configuration
            import dspy
            if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                logger.error("DSPy LM not configured globally. ArgumentService cannot proceed with DSPy analysis.")
                # Attempt to initialize GeminiService here to trigger config if not already done.
                # This is a safety net; ideally, app startup ensures GeminiService is initialized.
                GeminiService() # Initialize to trigger DSPy setup if not already done.
                if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                     logger.error("DSPy LM still not configured after attempting GeminiService init. Falling back.")
                     return self._fallback_analysis(transcript, "DSPy LM not configured.")
                else:
                    logger.info("DSPy LM was configured after GeminiService explicit initialization in ArgumentService.analyze.")

            # Use the DSPy module for analysis
            assessment = await asyncio.to_thread(self.dspy_analyzer.forward, transcript, session_context)
            return assessment

        except Exception as e:
            logger.error(f"Error in ArgumentService DSPy call: {e}", exc_info=True)
            return self._fallback_analysis(transcript, f"DSPy module error: {e}")

    def _fallback_analysis(self, transcript: str, error_message: Optional[str] = None) -> ArgumentAnalysis:
        logger.info(f"Performing fallback argument analysis for transcript snippet: {transcript[:100]}...")
        explanation = "Fallback analysis due to error or unconfigured DSPy LM."
        if error_message:
            explanation += f" Error: {error_message}"
        
        arguments_present = "because" in transcript.lower() or "therefore" in transcript.lower()
        key_arguments = []
        if arguments_present:
            key_arguments.append({"claim": "A claim might be present.", "evidence": "Inferred from keywords."})

        return ArgumentAnalysis(
            arguments_present=arguments_present,
            key_arguments=key_arguments,
            argument_strength=0.2 if arguments_present else 0.0,
            fallacies_detected=[],
            argument_summary="Summary not available due to fallback.",
            argument_structure_rating=0.1,
            argument_structure_analysis=explanation
        )
