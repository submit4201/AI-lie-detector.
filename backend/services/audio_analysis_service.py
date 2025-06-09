import logging
from typing import Dict, Any, Optional
import json
import asyncio # For asyncio.to_thread

from backend.models import AudioAnalysis
from backend.services.gemini_service import GeminiService # To ensure it's initialized for DSPy config
from backend.dspy_modules import DSPyAudioAnalysisAnalyzer # Import the new DSPy module

logger = logging.getLogger(__name__)

class AudioAnalysisService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        # Ensure GeminiService is initialized, which should configure DSPy LM.
        self.gemini_service_instance = gemini_service if gemini_service else GeminiService()
        self.dspy_analyzer = DSPyAudioAnalysisAnalyzer()

        import dspy # For checking dspy.settings.lm
        if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
            logger.warning("DSPy LM may not have been configured by GeminiService init as expected in AudioAnalysisService. Analysis might rely on fallbacks.")
        else:
            logger.info("AudioAnalysisService initialized; DSPy LM should be configured by GeminiService.")

    async def analyze(self, text: str, audio_file_path: Optional[str] = None) -> AudioAnalysis:
        # audio_file_path is not used by this DSPy module as it infers from text.
        # Kept for signature consistency if other methods use it.
        if not text:
            return AudioAnalysis() # Return default if no text
        
        try:
            # Check DSPy LM configuration
            import dspy
            if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                logger.error("DSPy LM not configured globally. AudioAnalysisService cannot proceed with DSPy analysis.")
                GeminiService() # Attempt to trigger config
                if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                     logger.error("DSPy LM still not configured after attempting GeminiService init. Falling back.")
                     return self._fallback_text_analysis(text, "DSPy LM not configured.")
                else:
                    logger.info("DSPy LM was configured after GeminiService explicit initialization in AudioAnalysisService.analyze.")

            # Use the DSPy module for analysis. Session context is empty as it's not used here.
            assessment = await asyncio.to_thread(self.dspy_analyzer.forward, text, session_context={})
            return assessment
            
        except Exception as e:
            logger.error(f"Error in AudioAnalysisService DSPy call: {e}", exc_info=True)
            return self._fallback_text_analysis(text, f"DSPy module error: {e}")

    def _fallback_text_analysis(self, text: str, error_message: Optional[str] = None) -> AudioAnalysis:
        logger.info(f"Performing fallback audio (text-based) analysis for transcript snippet: {text[:100]}...")
        explanation = "Fallback analysis due to error or unconfigured DSPy LM."
        if error_message:
            explanation += f" Error: {error_message}"

        # Basic fallback, returning an empty or minimally populated AudioAnalysis object
        # This part can be enhanced with simple text heuristics if needed, similar to original _fallback_text_analysis
        import re
        clarity = 0.0
        noise = "Low"
        wpm = 0
        pauses_data = {}
        intonation = "Analysis not available (fallback)."
        quality = explanation # Put the error/fallback reason in quality assessment

        if text:
            words = text.split()
            word_count = len(words)
            if word_count > 0:
                estimated_duration_minutes = word_count / 150.0 
                wpm = int(word_count / estimated_duration_minutes) if estimated_duration_minutes > 0 else 0

            fillers = len(re.findall(r'\\b(um|uh|er|ah|like|you know)\\b', text, re.IGNORECASE))
            text_pauses = text.count("...") + text.count("---")
            pauses_data = {"fillers": fillers, "textual_pauses": text_pauses}
            
            if word_count > 100: clarity = 0.65
            elif word_count > 20: clarity = 0.5
            else: clarity = 0.3
        
        return AudioAnalysis(
            speech_clarity_score=clarity_score,
            speech_clarity_analysis="Fallback: Inferred from text presence.",
            background_noise_assessment="Low (fallback assumption)",
            background_noise_analysis="Fallback: No specific background noise analysis from text.",
            average_speech_rate_wpm=wpm,
            speech_rate_variability_analysis="Fallback: Not analyzed from text.",
            intonation_patterns_analysis="Fallback: Not analyzed from text.",
            overall_audio_quality_assessment=quality_assessment,
            audio_duration_seconds=audio_duration_seconds,
            # Most other fields will use their defaults (None, "Analysis not available", [])
            # as they are hard to infer meaningfully from just text in a simple fallback.
            loudness_analysis="Fallback: Analysis not available.",
            signal_to_noise_ratio_analysis="Fallback: Analysis not available.",
            pitch_profile_analysis="Fallback: Analysis not available.",
            voice_timbre_description="Fallback: Analysis not available.",
            vocal_effort_assessment="Fallback: Analysis not available.",
            acoustic_event_analysis="Fallback: Analysis not available.",
            pause_characteristics_analysis="Fallback: Inferred from text if possible, otherwise not available.",
            vocal_stress_indicators_acoustic_analysis="Fallback: Analysis not available."
        )
