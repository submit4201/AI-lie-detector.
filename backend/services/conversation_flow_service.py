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

    async def analyze_conversation_flow(self, transcript: str, session_context: str = None) -> ConversationFlow:
        prompt = f"""
Analyze the conversation flow based on the following transcript.
Consider turn-taking, topic shifts, conversation depth, engagement, balance, clarity, and coherence.
Identify any disruptions or enhancers to the flow.
Provide a summary of the conversation flow.

Transcript:
{transcript}

Session Context (if any):
{session_context if session_context else "No specific session context provided."}

Please return your analysis in a JSON format with the following fields:
- turn_taking_frequency (e.g., "High", "Medium", "Low", or specific metrics if inferable)
- topic_shifts (e.g., "Frequent and abrupt", "Smooth and logical", "Few")
- conversation_depth (e.g., "Superficial", "Moderate", "Deep")
- engagement_levels (e.g., "High for all participants", "Mixed", "Low")
- conversation_balance (e.g., "Balanced", "Dominated by one speaker")
- clarity_and_coherence (e.g., "Clear and coherent", "Sometimes unclear", "Fragmented")
- summary_of_flow (A brief narrative summary)
- flow_disruptions (List of observed disruptions, e.g., ["Frequent interruptions", "Long silences"])
- flow_enhancers (List of observed enhancers, e.g., ["Active listening cues", "Clear topic transitions"])
- turn_taking_frequency_analysis (Your reasoning for the turn_taking_frequency assessment)
- topic_shifts_analysis (Your reasoning for the topic_shifts assessment)
- conversation_depth_analysis (Your reasoning for the conversation_depth assessment)
- engagement_levels_analysis (Your reasoning for the engagement_levels assessment)
- conversation_balance_analysis (Your reasoning for the conversation_balance assessment)
- clarity_and_coherence_analysis (Your reasoning for the clarity_and_coherence assessment)
- summary_of_flow_analysis (Your reasoning for the summary_of_flow)
- flow_disruptions_analysis (Your reasoning for identifying these flow_disruptions)
- flow_enhancers_analysis (Your reasoning for identifying these flow_enhancers)

If specific data is unavailable or analysis is not possible for a field, use appropriate default values like "N/A", "Could not determine", empty lists for list types, or a neutral assessment.
Ensure all fields are present in your JSON response.
IMPORTANT: Your entire response must be only the JSON object, with no surrounding text, explanations, or markdown formatting.
"""
        try:
            response_json_str = await self.gemini_service.query_gemini_for_raw_json(prompt)
            response_data = json.loads(response_json_str)
            
            # Ensure all expected fields are present in the response
            expected_fields = [
                "turn_taking_frequency", "topic_shifts", "conversation_depth",
                "engagement_levels", "conversation_balance", "clarity_and_coherence",
                "summary_of_flow", "flow_disruptions", "flow_enhancers",
                "turn_taking_frequency_analysis", "topic_shifts_analysis",
                "conversation_depth_analysis", "engagement_levels_analysis",
                "conversation_balance_analysis", "clarity_and_coherence_analysis",
                "summary_of_flow_analysis", "flow_disruptions_analysis", "flow_enhancers_analysis"
            ]
            
            # Fill missing fields with default values
            for field in expected_fields:
                if field not in response_data:
                    if "analysis" in field or field in ["summary_of_flow", "turn_taking_frequency", "topic_shifts", "conversation_depth", "engagement_levels", "conversation_balance", "clarity_and_coherence"]:
                        response_data[field] = "N/A"  # Default for analysis and summary fields
                    elif field in ["flow_disruptions", "flow_enhancers"]:
                        response_data[field] = []  # Default to empty list
                    else:
                        response_data[field] = "Could not determine"  # Generic default

            return ConversationFlow(
                engagement_level=response_data.get("engagement_levels", "Analysis not available"),
                topic_coherence_score=response_data.get("topic_coherence_score", 0.0),
                conversation_dominance=response_data.get("conversation_dominance", {}),
                turn_taking_efficiency=response_data.get("turn_taking_frequency", "Analysis not available"),
                conversation_phase=response_data.get("conversation_phase", "Analysis not available"),
                flow_disruptions=response_data.get("flow_disruptions", [])
            )
        except Exception as e:
            print(f"Error during enhanced conversation flow analysis: {e}")
            return self._fallback_text_analysis(transcript, None, None)
