import logging
from typing import Dict, Any, Optional, List # Ensure List is imported
import json
import asyncio # For asyncio.to_thread

from backend.models import ConversationFlow
from backend.services.gemini_service import GeminiService # To ensure it's initialized for DSPy config
from backend.dspy_modules import DSPyConversationFlowAnalyzer # Import the new DSPy module

logger = logging.getLogger(__name__)

class ConversationFlowService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        # Ensure GeminiService is initialized, which should configure DSPy LM.
        self.gemini_service_instance = gemini_service if gemini_service else GeminiService()
        self.dspy_analyzer = DSPyConversationFlowAnalyzer()

        import dspy # For checking dspy.settings.lm
        if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
            logger.warning("DSPy LM may not have been configured by GeminiService init as expected in ConversationFlowService. Analysis might rely on fallbacks.")
        else:
            logger.info("ConversationFlowService initialized; DSPy LM should be configured by GeminiService.")

    async def analyze(self, text: str,
                      dialogue_acts: Optional[List[Dict[str, Any]]] = None,
                      speaker_diarization: Optional[List[Dict[str, Any]]] = None) -> ConversationFlow:
        if not text:
            return ConversationFlow()

        try:
            # Check DSPy LM configuration
            import dspy
            if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                logger.error("DSPy LM not configured globally. ConversationFlowService cannot proceed with DSPy analysis.")
                GeminiService() # Attempt to trigger config
                if not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                     logger.error("DSPy LM still not configured after attempting GeminiService init. Falling back.")
                     return self._fallback_text_analysis(text, dialogue_acts, speaker_diarization, "DSPy LM not configured.")
                else:
                    logger.info("DSPy LM was configured after GeminiService explicit initialization in ConversationFlowService.analyze.")

            # Use the DSPy module for analysis.
            assessment = await asyncio.to_thread(
                self.dspy_analyzer.forward,
                transcript=text,
                session_context={}, # Pass an empty dict for now, specific data is handled by other params
                dialogue_acts=dialogue_acts,
                speaker_diarization=speaker_diarization
            )
            return assessment
            
        except Exception as e:
            logger.error(f"Error in ConversationFlowService DSPy call: {e}", exc_info=True)
            return self._fallback_text_analysis(text, dialogue_acts, speaker_diarization, f"DSPy module error: {e}")

    def _fallback_text_analysis(self, text: str,
                                dialogue_acts: Optional[List[Dict[str, Any]]] = None,
                                speaker_diarization: Optional[List[Dict[str, Any]]] = None,
                                error_message: Optional[str] = None) -> ConversationFlow:
        logger.info(f"Performing fallback conversation flow analysis for transcript snippet: {text[:100]}...")

        engagement = "Medium"
        coherence = 0.0
        dominance: Dict[str, float] = {}
        turn_taking = "Analysis not available (fallback)."
        phase = "Analysis not available (fallback)."
        disruptions = []

        if error_message:
            disruptions.append(f"Error during analysis: {error_message}")

        if text:
            word_count = len(text.split())
            if word_count > 200: engagement = "High"; coherence = 0.75; phase = "Development"
            elif word_count > 50: engagement = "Medium"; coherence = 0.5; phase = "Opening"
            else: engagement = "Low"; coherence = 0.25; phase = "Initial"

        if speaker_diarization and len(speaker_diarization) > 0:
            speaker_times: Dict[str, float] = {}
            total_speech_time = 0.0
            for segment in speaker_diarization:
                duration = (segment.get('end_time', 0.0) - segment.get('start_time', 0.0))
                speaker = segment.get('speaker_label', 'Unknown')
                speaker_times[speaker] = speaker_times.get(speaker, 0.0) + duration
                total_speech_time += duration
            
            if total_speech_time > 0:
                for speaker_label, time_val in speaker_times.items(): # Renamed time to time_val
                    dominance[speaker_label] = round(time_val / total_speech_time, 2)
            
            if len(speaker_diarization) > 10: turn_taking = "Seemingly fluid (fallback)"
            elif len(speaker_diarization) > 1: turn_taking = "Potentially stilted (fallback)"
            else: turn_taking = "Single speaker or minimal turns (fallback)"

        if dialogue_acts and len(dialogue_acts) > 1:
            act_types = {act.get('act_type') for act in dialogue_acts if isinstance(act, dict) and act.get('act_type')}
            if len(act_types) > 3: coherence = min(1.0, coherence + 0.1)
            disagreement_count = sum(1 for act in dialogue_acts if isinstance(act, dict) and act.get('act_type') == "Disagreement")
            if disagreement_count > len(dialogue_acts) * 0.3 and len(dialogue_acts) > 3:
                disruptions.append("Frequent disagreements noted.")
                coherence = max(0.0, coherence - 0.2)
        elif not dialogue_acts and not speaker_diarization and len(text.split()) < 20:
             turn_taking = "Very short input, likely single turn (fallback)."
             phase = "Brief Utterance (fallback)"

        return ConversationFlow(
            engagement_level=engagement,
            topic_coherence_score=round(coherence,2),
            conversation_dominance=dominance,
            turn_taking_efficiency=turn_taking,
            conversation_phase=phase,
            flow_disruptions=disruptions
        )
