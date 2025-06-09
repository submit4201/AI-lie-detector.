import logging
from typing import Dict, Any, Optional, List # Ensure List is imported
import json
import asyncio # For asyncio.to_thread

from backend.models import QuantitativeMetrics
from backend.services.gemini_service import GeminiService # To ensure it's initialized for DSPy config
from backend.dspy_modules import DSPyQuantitativeMetricsAnalyzer # Import the new DSPy module

logger = logging.getLogger(__name__)

class QuantitativeMetricsService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        # Ensure GeminiService is initialized, which should configure DSPy LM.
        self.gemini_service_instance = gemini_service if gemini_service else GeminiService()
        self.dspy_analyzer = DSPyQuantitativeMetricsAnalyzer()
        
        import dspy # For checking dspy.settings.lm
        if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
            logger.warning("DSPy LM may not have been configured by GeminiService init as expected in QuantitativeMetricsService. Analysis might rely on fallbacks.")
        else:
            logger.info("QuantitativeMetricsService initialized; DSPy LM should be configured by GeminiService.")

    async def analyze(self, text: str,
                      speaker_diarization: Optional[List[Dict[str, Any]]] = None,
                      sentiment_trend_data_input: Optional[List[Dict[str, float]]] = None) -> QuantitativeMetrics:
        if not text:
            # Fallback to default if no text, ensuring word_count is 0
            return QuantitativeMetrics(word_count=0)
        
        try:
            # Check DSPy LM configuration
            import dspy
            if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                logger.error("DSPy LM not configured globally. QuantitativeMetricsService cannot proceed with DSPy analysis.")
                GeminiService() # Attempt to trigger config
                if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                     logger.error("DSPy LM still not configured after attempting GeminiService init. Falling back.")
                     return self._fallback_text_analysis(text, speaker_diarization, sentiment_trend_data_input, "DSPy LM not configured.")
                else:
                    logger.info("DSPy LM was configured after GeminiService explicit initialization in QuantitativeMetricsService.analyze.")

            # Use the DSPy module for analysis.
            # The DSPyQuantitativeMetricsAnalyzer's forward method is designed to take these extra params.
            assessment = await asyncio.to_thread(
                self.dspy_analyzer.forward,
                transcript=text,
                session_context={}, # Pass an empty dict for now, specific data is handled by other params
                speaker_diarization=speaker_diarization,
                sentiment_trend_data_input=sentiment_trend_data_input
            )
            return assessment
            
        except Exception as e:
            logger.error(f"Error in QuantitativeMetricsService DSPy call: {e}", exc_info=True)
            return self._fallback_text_analysis(text, speaker_diarization, sentiment_trend_data_input, f"DSPy module error: {e}")

    def _fallback_text_analysis(self, text: str,
                                speaker_diarization: Optional[List[Dict[str, Any]]] = None,
                                sentiment_trend_data_input: Optional[List[Dict[str, float]]] = None,
                                error_message: Optional[str] = None) -> QuantitativeMetrics:
        logger.info(f"Performing fallback quantitative metrics analysis for transcript snippet: {text[:100]}...")

        word_count = len(text.split())
        vocab_richness = 0.0
        if word_count > 0:
            actual_words = [word for word in text.lower().split() if word.isalpha()]
            unique_words_count = len(set(actual_words))
            actual_word_count = len(actual_words)
            vocab_richness = unique_words_count / actual_word_count if actual_word_count > 0 else 0.0

        # Use provided sentiment trend or simulate if not
        simulated_sentiment_trend = sentiment_trend_data_input if sentiment_trend_data_input is not None else []
        if not simulated_sentiment_trend and word_count > 0:
            estimated_total_seconds = (word_count / 150.0) * 60 # Avg 150 WPM
            simulated_sentiment_trend = [
                {'time': round(0.2 * estimated_total_seconds, 1), 'sentiment': 0.0}, # Neutral start
                {'time': round(0.8 * estimated_total_seconds, 1), 'sentiment': 0.0}  # Neutral end
            ] if estimated_total_seconds > 0 else [{'time': 0.0, 'sentiment': 0.0}]

        # Rudimentary speaker diarization fallback (if data provided)
        talk_ratio = 0.0
        avg_turn_duration = 0.0
        interruptions = 0
        if speaker_diarization:
            num_turns = len(speaker_diarization)
            if num_turns > 0:
                total_speech_time = sum(turn.get('duration', 0) for turn in speaker_diarization if isinstance(turn, dict))
                avg_turn_duration = total_speech_time / num_turns if num_turns > 0 else 0.0
            # Basic interruption inference (very naive)
            if num_turns > 1: interruptions = max(0, num_turns -1 - int(avg_turn_duration/10)) # Guess based on turns and avg duration
            # Talk ratio is complex; simplified: if more than one speaker, assume 0.5, else 1.0 or 0.0
            unique_speakers = set(turn.get('speaker_label') for turn in speaker_diarization if isinstance(turn, dict))
            if len(unique_speakers) > 1 : talk_ratio = 0.5
            elif len(unique_speakers) == 1: talk_ratio = 1.0


        logger.info(f"Fallback analysis performed. Error context if any: {error_message}")

        return QuantitativeMetrics(
            talk_to_listen_ratio=talk_ratio,
            speaker_turn_duration_avg=round(avg_turn_duration, 2),
            interruptions_count=interruptions,
            sentiment_trend=simulated_sentiment_trend,
            word_count=word_count,
            vocabulary_richness_score=round(vocab_richness, 3)
        )
