# backend/services/speaker_intent_service.py
import logging
import asyncio
from typing import Dict, Any, Optional
import dspy # Import dspy

from backend.models import SpeakerIntent
from backend.dspy_modules import DSPySpeakerIntentAnalyzer
from backend.services.gemini_service import GeminiService # To ensure LM config

logger = logging.getLogger(__name__)

class SpeakerIntentService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        # Ensure DSPy LM is configured by instantiating GeminiService
        self.gemini_service_instance = gemini_service if gemini_service else GeminiService()

        lm_configured = False
        try:
            if dspy.settings.lm:
                lm_configured = True
        except AttributeError:
            pass # lm is not configured

        if not lm_configured:
            logger.warning("DSPy LM not configured at SpeakerIntentService init. Service calls might fail if not configured elsewhere.")

        self.dspy_analyzer = DSPySpeakerIntentAnalyzer()

    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> SpeakerIntent:
        if not transcript:
            return SpeakerIntent()

        # Ensure LM is configured before calling (safety check, ideally done at app startup)
        lm_configured = False
        try:
            if dspy.settings.lm:
                lm_configured = True
        except AttributeError:
            pass

        if not lm_configured:
            logger.error("DSPy LM not configured in SpeakerIntentService.analyze. Attempting to re-init GeminiService.")
            GeminiService() # Attempt to trigger config

            lm_configured_after_init = False
            try:
                if dspy.settings.lm:
                    lm_configured_after_init = True
            except AttributeError:
                pass

            if not lm_configured_after_init:
                logger.error("DSPy LM failed to configure. Returning default SpeakerIntent.")
                return SpeakerIntent(overall_assessment="Error: DSPy LM not configured.")
            else:
                logger.info("DSPy LM configured after explicit GeminiService initialization in SpeakerIntentService.")

        if session_context is None:
            session_context = {}

        try:
            # DSPy modules are synchronous by default
            intent_assessment = await asyncio.to_thread(
                self.dspy_analyzer.forward, transcript, session_context
            )
            return intent_assessment
        except Exception as e:
            logger.error(f"Error during SpeakerIntentService DSPy call: {e}", exc_info=True)
            return SpeakerIntent(overall_assessment=f"Error during analysis: {str(e)}")
