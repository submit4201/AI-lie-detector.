import dspy
import json # Ensure json is imported for session_context_str and parsing techniques
from typing import Any # Import Any for type hinting
from backend.models import ManipulationAssessment # Assuming this path is correct

# DSPy LM configuration is now handled centrally by GeminiService.

class ManipulationSignature(dspy.Signature):
    """Analyze the transcript for signs of manipulation and provide a structured assessment.

    The analysis should consider techniques like Gaslighting, Guilt-tripping, Love bombing,
    Appeal to pity, Intimidation, and Minimization.
    """
    transcript: str = dspy.InputField(desc="The conversation transcript to analyze.")
    session_context: str = dspy.InputField(desc="Optional JSON string providing context about the session, e.g., previous interactions or speaker profiles. Can be empty if no context.")

    is_manipulative: bool = dspy.OutputField(desc="Overall assessment of whether manipulation is present.")
    manipulation_score: float = dspy.OutputField(desc="Likelihood of manipulation (0.0 to 1.0).")
    manipulation_techniques: list[str] = dspy.OutputField(desc="Specific manipulation techniques identified.")
    manipulation_confidence: float = dspy.OutputField(desc="Confidence in this assessment (0.0 to 1.0).")
    manipulation_explanation: str = dspy.OutputField(desc="Brief explanation for the assessment, citing examples.")
    manipulation_score_analysis: str = dspy.OutputField(desc="Detailed analysis supporting the manipulation score.")

class DSPyManipulationAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        # Using ChainOfThought to encourage more detailed reasoning from the LLM
        # before it produces the structured output.
        self.predictor = dspy.ChainOfThought(ManipulationSignature)

    def forward(self, transcript: str, session_context: dict | None) -> ManipulationAssessment:
        # Convert session_context dict to JSON string for the signature
        session_context_str = json.dumps(session_context) if session_context else "{}"

        prediction = self.predictor(transcript=transcript, session_context=session_context_str)

        # Convert prediction fields to ManipulationAssessment Pydantic model
        # Ensuring types are correctly handled, especially for bool and float.
        try:
            # Handle boolean conversion robustly
            raw_is_manipulative = str(getattr(prediction, 'is_manipulative', 'false')).lower()
            is_manipulative = raw_is_manipulative == 'true' or raw_is_manipulative == 'yes'

            manipulation_score_raw = getattr(prediction, 'manipulation_score', "0.0")
            manipulation_score = float(manipulation_score_raw) if manipulation_score_raw else 0.0

            manipulation_confidence_raw = getattr(prediction, 'manipulation_confidence', "0.0")
            manipulation_confidence = float(manipulation_confidence_raw) if manipulation_confidence_raw else 0.0

            # Ensure techniques is a list of strings
            techniques_raw = getattr(prediction, 'manipulation_techniques', [])
            techniques = []
            if isinstance(techniques_raw, str):
                # Attempt to parse if it's a JSON string list, or split if comma-separated
                try:
                    parsed_techniques = json.loads(techniques_raw)
                    if isinstance(parsed_techniques, list):
                        techniques = [str(t).strip() for t in parsed_techniques if str(t).strip()]
                    elif isinstance(parsed_techniques, str) and parsed_techniques.strip(): # Handles case where JSON is just a single string
                        techniques = [parsed_techniques.strip()]
                    # else: techniques remains [] if parsed_techniques is not a list or string (e.g. dict)
                except json.JSONDecodeError:
                    # Fallback for non-JSON strings (e.g. comma-separated)
                    techniques = [t.strip() for t in techniques_raw.split(',') if t.strip()] if techniques_raw.strip() else []
            elif isinstance(techniques_raw, list):
                techniques = [str(t).strip() for t in techniques_raw if str(t).strip()]
            # If techniques_raw is not a string or list, techniques remains []

        except (ValueError, TypeError) as e:
            print(f"Error converting prediction fields: {e}. Prediction: {prediction}")
            # Fallback to default values for the Pydantic model on conversion error
            return ManipulationAssessment(
                is_manipulative=False,
                manipulation_score=0.0,
                manipulation_techniques=[],
                manipulation_confidence=0.0,
                manipulation_explanation="Error processing LLM output.",
                manipulation_score_analysis="Could not reliably parse LLM output for detailed analysis."
            )

        return ManipulationAssessment(
            is_manipulative=is_manipulative,
            manipulation_score=manipulation_score,
            manipulation_techniques=techniques,
            manipulation_confidence=manipulation_confidence,
            manipulation_explanation=str(getattr(prediction, 'manipulation_explanation', "")),
            manipulation_score_analysis=str(getattr(prediction, 'manipulation_score_analysis', ""))
        )

from backend.models import ArgumentAnalysis # Add this
# json is already imported at the top

class ArgumentSignature(dspy.Signature):
    """Analyze the transcript for its argument structure.
    Identify claims, supporting evidence, assess strength, and detect fallacies.
    """
    transcript: str = dspy.InputField(desc="The conversation transcript to analyze.")
    session_context: str = dspy.InputField(desc="Optional JSON string providing context. Can be empty.")

    arguments_present: bool = dspy.OutputField(desc="Are there identifiable arguments (claims supported by reasons/evidence)?")
    key_arguments: str = dspy.OutputField(desc="JSON string of a list of key arguments, each as a dict with 'claim' and 'evidence' keys (e.g., '[{\"claim\": \"...\", \"evidence\": \"...\"}]').")
    argument_strength: float = dspy.OutputField(desc="Overall strength of the arguments (0.0 to 1.0).")
    fallacies_detected: str = dspy.OutputField(desc="JSON string of a list of any logical fallacies identified (e.g., '[\"Ad hominem\", \"Straw man\"]'). Empty list if none.")
    argument_summary: str = dspy.OutputField(desc="A brief summary of the main arguments.")
    argument_structure_rating: float = dspy.OutputField(desc="Rating of how well-structured the arguments are (0.0 to 1.0).")
    argument_structure_analysis: str = dspy.OutputField(desc="Detailed analysis of the argument structure.")

class DSPyArgumentAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(ArgumentSignature)

    def forward(self, transcript: str, session_context: dict | None) -> ArgumentAnalysis:
        session_context_str = json.dumps(session_context) if session_context else "{}"
        prediction = self.predictor(transcript=transcript, session_context=session_context_str)

        try:
            raw_args_present = str(getattr(prediction, 'arguments_present', 'false')).lower()
            args_present = raw_args_present == 'true' or raw_args_present == 'yes'

            strength_raw = getattr(prediction, 'argument_strength', "0.0")
            strength = float(strength_raw) if strength_raw else 0.0

            structure_rating_raw = getattr(prediction, 'argument_structure_rating', "0.0")
            structure_rating = float(structure_rating_raw) if structure_rating_raw else 0.0

            key_args_str = getattr(prediction, 'key_arguments', '[]')
            key_args = json.loads(key_args_str) if key_args_str and key_args_str.strip() else []
            if not isinstance(key_args, list): key_args = [] # Ensure it's a list

            fallacies_str = getattr(prediction, 'fallacies_detected', '[]')
            fallacies = json.loads(fallacies_str) if fallacies_str and fallacies_str.strip() else []
            if not isinstance(fallacies, list): fallacies = [] # Ensure it's a list


        except (ValueError, TypeError, json.JSONDecodeError) as e:
            print(f"Error converting ArgumentAnalysis prediction fields: {e}. Prediction: {prediction}")
            return ArgumentAnalysis() # Fallback to default

        return ArgumentAnalysis(
            arguments_present=args_present,
            key_arguments=key_args,
            argument_strength=strength,
            fallacies_detected=fallacies,
            argument_summary=str(getattr(prediction, 'argument_summary', "Analysis not available.")),
            argument_structure_rating=structure_rating,
            argument_structure_analysis=str(getattr(prediction, 'argument_structure_analysis', "Analysis not available."))
        )

from backend.models import SpeakerAttitude # Add this

class SpeakerAttitudeSignature(dspy.Signature):
    """Analyze the speaker's attitude in the transcript.
    Focus on dominant attitude, respect level, formality, and politeness.
    """
    transcript: str = dspy.InputField(desc="The conversation transcript to analyze.")
    session_context: str = dspy.InputField(desc="Optional JSON string providing context. Can be empty.")

    dominant_attitude: str = dspy.OutputField(desc="Dominant attitude of the speaker (e.g., Neutral, Positive, Negative, Mixed).")
    attitude_scores: str = dspy.OutputField(desc="JSON string of a dictionary with scores for various attitudes, e.g., '{\"respectful\": 0.8, \"friendly\": 0.7}'.")
    respect_level: str = dspy.OutputField(desc="Assessed level of respect (e.g., High, Medium, Low, Disrespectful).")
    respect_level_score: float = dspy.OutputField(desc="Numerical score for respect level (0.0 to 1.0).")
    respect_level_score_analysis: str = dspy.OutputField(desc="Analysis of the respect level score.")
    formality_score: float = dspy.OutputField(desc="Formality score (0.0 informal to 1.0 formal).")
    formality_assessment: str = dspy.OutputField(desc="Qualitative assessment of formality.")
    politeness_score: float = dspy.OutputField(desc="Politeness score (0.0 to 1.0).")
    politeness_assessment: str = dspy.OutputField(desc="Qualitative assessment of politeness.")

class DSPySpeakerAttitudeAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(SpeakerAttitudeSignature)

    def forward(self, transcript: str, session_context: dict | None) -> SpeakerAttitude:
        session_context_str = json.dumps(session_context) if session_context else "{}"
        prediction = self.predictor(transcript=transcript, session_context=session_context_str)

        try:
            respect_score_raw = getattr(prediction, 'respect_level_score', "0.0")
            respect_score = float(respect_score_raw) if respect_score_raw else 0.0

            form_score_raw = getattr(prediction, 'formality_score', "0.0")
            form_score = float(form_score_raw) if form_score_raw else 0.0

            polite_score_raw = getattr(prediction, 'politeness_score', "0.0")
            polite_score = float(polite_score_raw) if polite_score_raw else 0.0

            attitude_scores_str = getattr(prediction, 'attitude_scores', '{}')
            attitude_scores = json.loads(attitude_scores_str) if attitude_scores_str and attitude_scores_str.strip() else {}
            if not isinstance(attitude_scores, dict): attitude_scores = {}


        except (ValueError, TypeError, json.JSONDecodeError) as e:
            print(f"Error converting SpeakerAttitude prediction fields: {e}. Prediction: {prediction}")
            return SpeakerAttitude() # Fallback to default

        return SpeakerAttitude(
            dominant_attitude=str(getattr(prediction, 'dominant_attitude', "Neutral")),
            attitude_scores=attitude_scores,
            respect_level=str(getattr(prediction, 'respect_level', "Neutral")),
            respect_level_score=respect_score,
            respect_level_score_analysis=str(getattr(prediction, 'respect_level_score_analysis', "Analysis not available.")),
            formality_score=form_score,
            formality_assessment=str(getattr(prediction, 'formality_assessment', "Analysis not available.")),
            politeness_score=polite_score,
            politeness_assessment=str(getattr(prediction, 'politeness_assessment', "Analysis not available."))
        )

from backend.models import EnhancedUnderstanding # Add this
# json is already imported

class EnhancedUnderstandingSignature(dspy.Signature):
    """Analyze the transcript for deeper understanding, including key topics, action items, inconsistencies, and areas of evasiveness."""
    transcript: str = dspy.InputField(desc="The conversation transcript to analyze.")
    session_context: str = dspy.InputField(desc="Optional JSON string providing context. Can be empty.")

    key_topics: str = dspy.OutputField(desc="JSON string of a list of key topics discussed.")
    action_items: str = dspy.OutputField(desc="JSON string of a list of identified action items.")
    unresolved_questions: str = dspy.OutputField(desc="JSON string of a list of unresolved questions from the conversation.")
    summary_of_understanding: str = dspy.OutputField(desc="Summary of the core understanding derived.")
    contextual_insights: str = dspy.OutputField(desc="JSON string of a list of insights based on context.")
    nuances_detected: str = dspy.OutputField(desc="JSON string of a list of subtle nuances detected in communication.")
    key_inconsistencies: str = dspy.OutputField(desc="JSON string of a list of key contradictions or inconsistencies in statements.")
    areas_of_evasiveness: str = dspy.OutputField(desc="JSON string of a list of topics or questions the speaker seemed to avoid.")
    suggested_follow_up_questions: str = dspy.OutputField(desc="JSON string of a list of suggested questions to ask for clarity or further probing.")
    unverified_claims: str = dspy.OutputField(desc="JSON string of a list of claims made by the speaker that may require fact-checking.")
    key_inconsistencies_analysis: str = dspy.OutputField(desc="Analysis of each key inconsistency and its implications.")
    areas_of_evasiveness_analysis: str = dspy.OutputField(desc="Analysis of each area of evasiveness and its implications.")
    suggested_follow_up_questions_analysis: str = dspy.OutputField(desc="Analysis of each suggested follow-up question and its potential impact.")
    fact_checking_analysis: str = dspy.OutputField(desc="Analysis of each unverified claim and its implications.")
    deep_dive_analysis: str = dspy.OutputField(desc="Deep dive analysis of the enhanced understanding.")

class DSPyEnhancedUnderstandingAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(EnhancedUnderstandingSignature)

    def _parse_list_str_field(self, prediction_field_value: Any) -> list[str]:
        if isinstance(prediction_field_value, list):
            return [str(item).strip() for item in prediction_field_value if str(item).strip()]
        if isinstance(prediction_field_value, str) and prediction_field_value.strip():
            try:
                # Try parsing as JSON list
                parsed_list = json.loads(prediction_field_value)
                if isinstance(parsed_list, list):
                    return [str(item).strip() for item in parsed_list if str(item).strip()]
                # If it's a valid JSON but not a list (e.g. a single string from JSON), wrap it
                return [str(parsed_list).strip()] if str(parsed_list).strip() else []
            except json.JSONDecodeError:
                # Fallback for non-JSON strings (e.g., comma-separated, newline-separated)
                # Split by comma first, then by newline if no commas
                if ',' in prediction_field_value:
                    return [s.strip() for s in prediction_field_value.split(',') if s.strip()]
                else:
                    return [s.strip() for s in prediction_field_value.splitlines() if s.strip()]
        return []

    def forward(self, transcript: str, session_context: dict | None) -> EnhancedUnderstanding:
        session_context_str = json.dumps(session_context) if session_context else "{}"
        prediction = self.predictor(transcript=transcript, session_context=session_context_str)

        try:
            return EnhancedUnderstanding(
                key_topics=self._parse_list_str_field(getattr(prediction, 'key_topics', [])),
                action_items=self._parse_list_str_field(getattr(prediction, 'action_items', [])),
                unresolved_questions=self._parse_list_str_field(getattr(prediction, 'unresolved_questions', [])),
                summary_of_understanding=str(getattr(prediction, 'summary_of_understanding', "Analysis not available.")),
                contextual_insights=self._parse_list_str_field(getattr(prediction, 'contextual_insights', [])),
                nuances_detected=self._parse_list_str_field(getattr(prediction, 'nuances_detected', [])),
                key_inconsistencies=self._parse_list_str_field(getattr(prediction, 'key_inconsistencies', [])),
                areas_of_evasiveness=self._parse_list_str_field(getattr(prediction, 'areas_of_evasiveness', [])),
                suggested_follow_up_questions=self._parse_list_str_field(getattr(prediction, 'suggested_follow_up_questions', [])),
                unverified_claims=self._parse_list_str_field(getattr(prediction, 'unverified_claims', [])),
                key_inconsistencies_analysis=str(getattr(prediction, 'key_inconsistencies_analysis', "Analysis not available.")),
                areas_of_evasiveness_analysis=str(getattr(prediction, 'areas_of_evasiveness_analysis', "Analysis not available.")),
                suggested_follow_up_questions_analysis=str(getattr(prediction, 'suggested_follow_up_questions_analysis', "Analysis not available.")),
                fact_checking_analysis=str(getattr(prediction, 'fact_checking_analysis', "Analysis not available.")),
                deep_dive_analysis=str(getattr(prediction, 'deep_dive_analysis', "Analysis not available."))
            )
        except Exception as e:
            print(f"Error converting EnhancedUnderstanding prediction fields: {e}. Prediction: {prediction}")
            return EnhancedUnderstanding()

from backend.models import PsychologicalAnalysis # Add this

class PsychologicalAnalysisSignature(dspy.Signature):
    """Analyze the speaker's psychological state based on the transcript.
    Focus on emotional state, cognitive load, stress, confidence, and potential biases.
    """
    transcript: str = dspy.InputField(desc="The conversation transcript to analyze.")
    session_context: str = dspy.InputField(desc="Optional JSON string providing context. Can be empty.")

    emotional_state: str = dspy.OutputField(desc="Overall emotional state inferred (e.g., Neutral, Anxious, Calm).")
    cognitive_load: str = dspy.OutputField(desc="Inferred cognitive load (e.g., Low, Normal, High), with brief justification.")
    stress_level: float = dspy.OutputField(desc="Inferred stress level (0.0 to 1.0).")
    confidence_level: float = dspy.OutputField(desc="Inferred confidence level (0.0 to 1.0).")
    psychological_summary: str = dspy.OutputField(desc="Summary of the psychological state analysis.")
    potential_biases: str = dspy.OutputField(desc="JSON string of a list of identified potential cognitive biases (e.g., '[\"Confirmation bias\"] LIKELY because...').")

class DSPyPsychologicalAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(PsychologicalAnalysisSignature)

    def _parse_list_str_field(self, prediction_field_value: Any) -> list[str]: # Helper from above
        if isinstance(prediction_field_value, list):
            return [str(item).strip() for item in prediction_field_value if str(item).strip()]
        if isinstance(prediction_field_value, str) and prediction_field_value.strip():
            try:
                parsed_list = json.loads(prediction_field_value)
                if isinstance(parsed_list, list):
                    return [str(item).strip() for item in parsed_list if str(item).strip()]
                return [str(parsed_list).strip()] if str(parsed_list).strip() else []
            except json.JSONDecodeError:
                if ',' in prediction_field_value:
                    return [s.strip() for s in prediction_field_value.split(',') if s.strip()]
                else:
                    return [s.strip() for s in prediction_field_value.splitlines() if s.strip()]
        return []

    def forward(self, transcript: str, session_context: dict | None) -> PsychologicalAnalysis:
        session_context_str = json.dumps(session_context) if session_context else "{}"
        prediction = self.predictor(transcript=transcript, session_context=session_context_str)

        try:
            stress_raw = getattr(prediction, 'stress_level', "0.0")
            stress = float(stress_raw) if stress_raw else 0.0

            confidence_raw = getattr(prediction, 'confidence_level', "0.0")
            confidence = float(confidence_raw) if confidence_raw else 0.0

            biases = self._parse_list_str_field(getattr(prediction, 'potential_biases', []))

        except (ValueError, TypeError, json.JSONDecodeError) as e:
            print(f"Error converting PsychologicalAnalysis prediction fields: {e}. Prediction: {prediction}")
            return PsychologicalAnalysis()

        return PsychologicalAnalysis(
            emotional_state=str(getattr(prediction, 'emotional_state', "Neutral")),
            cognitive_load=str(getattr(prediction, 'cognitive_load', "Normal")),
            stress_level=stress,
            confidence_level=confidence,
            psychological_summary=str(getattr(prediction, 'psychological_summary', "Analysis not available.")),
            potential_biases=biases
        )

from backend.models import AudioAnalysis # Add this
# json is already imported

class AudioAnalysisSignature(dspy.Signature):
    """Analyze the transcript to infer audio characteristics based *only* on textual content.
    Assess speech clarity, background noise, speech rate, pauses/fillers, intonation, and overall audio quality.
    """
    transcript: str = dspy.InputField(desc="The conversation transcript to analyze.")
    session_context: str = dspy.InputField(desc="Optional JSON string providing context. Can be empty. Not typically used for this text-only audio characteristic inference.")

    speech_clarity_score: float = dspy.OutputField(desc="Clarity of speech (0.0 to 1.0).")
    background_noise_level: str = dspy.OutputField(desc="Inferred level of background noise (e.g., Low, Medium, High).")
    speech_rate_wpm: int = dspy.OutputField(desc="Estimated average speech rate in words per minute.")
    pauses_and_fillers: str = dspy.OutputField(desc="JSON string of a dictionary with counts of pauses and fillers, e.g., '{\"textual_pauses\": 5, \"um\": 2}'.")
    intonation_patterns: str = dspy.OutputField(desc="Description of inferred intonation patterns observed from text.")
    audio_quality_assessment: str = dspy.OutputField(desc="Overall assessment of likely audio quality based on text.")

class DSPyAudioAnalysisAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(AudioAnalysisSignature)

    def forward(self, transcript: str, session_context: dict | None) -> AudioAnalysis:
        # session_context is not strictly used by this text-based audio inference but included for consistency
        session_context_str = json.dumps(session_context) if session_context else "{}"
        prediction = self.predictor(transcript=transcript, session_context=session_context_str)

        try:
            clarity_score_raw = getattr(prediction, 'speech_clarity_score', "0.0")
            clarity_score = float(clarity_score_raw) if clarity_score_raw else 0.0

            rate_wpm_raw = getattr(prediction, 'speech_rate_wpm', "0")
            rate_wpm = int(rate_wpm_raw) if rate_wpm_raw else 0

            pauses_fillers_str = getattr(prediction, 'pauses_and_fillers', '{}')
            pauses_fillers = json.loads(pauses_fillers_str) if pauses_fillers_str and pauses_fillers_str.strip() else {}
            if not isinstance(pauses_fillers, dict): pauses_fillers = {}


        except (ValueError, TypeError, json.JSONDecodeError) as e:
            print(f"Error converting AudioAnalysis prediction fields: {e}. Prediction: {prediction}")
            return AudioAnalysis() # Fallback to default

        return AudioAnalysis(
            speech_clarity_score=clarity_score,
            background_noise_level=str(getattr(prediction, 'background_noise_level', "Low")),
            speech_rate_wpm=rate_wpm,
            pauses_and_fillers=pauses_fillers,
            intonation_patterns=str(getattr(prediction, 'intonation_patterns', "Analysis not available.")),
            audio_quality_assessment=str(getattr(prediction, 'audio_quality_assessment', "Analysis not available."))
        )

from backend.models import QuantitativeMetrics # Add this

class QuantitativeMetricsSignature(dspy.Signature):
    """Analyze the transcript and session context (which may include speaker diarization and sentiment trend data as JSON strings)
    to determine quantitative communication metrics.
    """
    transcript: str = dspy.InputField(desc="The conversation transcript to analyze.")
    # Session context might contain 'speaker_diarization_json' and 'sentiment_trend_json'
    session_context: str = dspy.InputField(desc="JSON string providing context. May include 'speaker_diarization_json' and 'sentiment_trend_json'. Can be empty.")

    talk_to_listen_ratio: float = dspy.OutputField(desc="Ratio of talking time to listening time. Infer if possible, else default.")
    speaker_turn_duration_avg: float = dspy.OutputField(desc="Average duration of speaker turns in seconds. Infer if possible, else default.")
    interruptions_count: int = dspy.OutputField(desc="Number of interruptions detected. Infer if possible, else default.")
    sentiment_trend: str = dspy.OutputField(desc="JSON string of a list of dictionaries representing sentiment trend, e.g., '[{\"time\": 10.5, \"sentiment\": 0.7}]'. Use context if provided, else infer or default to empty list.")
    word_count: int = dspy.OutputField(desc="Total number of words in the transcript.")
    vocabulary_richness_score: float = dspy.OutputField(desc="Vocabulary richness score (e.g., Type-Token Ratio - TTR).")

class DSPyQuantitativeMetricsAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(QuantitativeMetricsSignature)

    def forward(self, transcript: str, session_context: dict | None,
                    # Keep original optional params for now, will be packed into session_context for DSPy
                    speaker_diarization: list | None = None,
                    sentiment_trend_data_input: list | None = None) -> QuantitativeMetrics:

        # Prepare session_context for DSPy module, embedding additional data if provided
        dspy_session_context = session_context.copy() if session_context else {}
        if speaker_diarization:
            dspy_session_context['speaker_diarization_json'] = json.dumps(speaker_diarization)
        if sentiment_trend_data_input:
            dspy_session_context['sentiment_trend_json'] = json.dumps(sentiment_trend_data_input)

        session_context_str = json.dumps(dspy_session_context) if dspy_session_context else "{}"

        prediction = self.predictor(transcript=transcript, session_context=session_context_str)

        try:
            ratio_raw = getattr(prediction, 'talk_to_listen_ratio', "0.0")
            ratio = float(ratio_raw) if ratio_raw else 0.0

            avg_turn_raw = getattr(prediction, 'speaker_turn_duration_avg', "0.0")
            avg_turn = float(avg_turn_raw) if avg_turn_raw else 0.0

            interruptions_raw = getattr(prediction, 'interruptions_count', "0")
            interruptions = int(interruptions_raw) if interruptions_raw else 0

            wc_raw = getattr(prediction, 'word_count', str(len(transcript.split()))) # Fallback for word_count
            wc = int(wc_raw) if wc_raw else len(transcript.split())

            vocab_score_raw = getattr(prediction, 'vocabulary_richness_score', "0.0")
            vocab_score = float(vocab_score_raw) if vocab_score_raw else 0.0

            sentiment_str = getattr(prediction, 'sentiment_trend', '[]')
            sentiment = json.loads(sentiment_str) if sentiment_str and sentiment_str.strip() else []
            if not isinstance(sentiment, list): sentiment = []

        except (ValueError, TypeError, json.JSONDecodeError) as e:
            print(f"Error converting QuantitativeMetrics prediction fields: {e}. Prediction: {prediction}")
            return QuantitativeMetrics(word_count=len(transcript.split())) # Fallback

        return QuantitativeMetrics(
            talk_to_listen_ratio=ratio,
            speaker_turn_duration_avg=avg_turn,
            interruptions_count=interruptions,
            sentiment_trend=sentiment,
            word_count=wc,
            vocabulary_richness_score=vocab_score
        )

from backend.models import SpeakerIntent # Add this
# json and Any are already imported

class SpeakerIntentSignature(dspy.Signature):
    """Analyze the transcript to infer the primary and secondary intents of the speaker.
    Consider the language used, questions asked, statements made, and overall conversational context.
    Possible intents include: To persuade, To inform, To inquire/seek information, To build rapport,
    To express emotion, To problem-solve/resolve conflict, To direct/instruct, To entertain.
    """
    transcript: str = dspy.InputField(desc="The conversation transcript to analyze.")
    session_context: str = dspy.InputField(desc="Optional JSON string providing context. Can be empty.")

    inferred_intent: str = dspy.OutputField(desc="The primary inferred intent of the speaker.")
    confidence_score: float = dspy.OutputField(desc="Confidence in the primary inferred intent (0.0 to 1.0).")
    key_phrases_supporting_intent: str = dspy.OutputField(desc="JSON string list of key phrases supporting the primary intent.")
    overall_assessment: str = dspy.OutputField(desc="Brief justification for the inferred primary intent.")
    secondary_intents: str = dspy.OutputField(desc="JSON string list of any secondary intents detected (e.g., '[\"To build rapport\"]'), or an empty list string '[]'.")

class DSPySpeakerIntentAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(SpeakerIntentSignature)

    def _parse_list_str_field(self, prediction_field_value: Any) -> list[str]: # Re-use or define helper
        if isinstance(prediction_field_value, list):
            return [str(item).strip() for item in prediction_field_value if str(item).strip()]
        if isinstance(prediction_field_value, str) and prediction_field_value.strip():
            try:
                parsed_list = json.loads(prediction_field_value)
                if isinstance(parsed_list, list):
                    return [str(item).strip() for item in parsed_list if str(item).strip()]
                return [str(parsed_list).strip()] if str(parsed_list).strip() else []
            except json.JSONDecodeError:
                if ',' in prediction_field_value:
                    return [s.strip() for s in prediction_field_value.split(',') if s.strip()]
                else: # Treat as lines if no commas
                    return [s.strip() for s in prediction_field_value.splitlines() if s.strip()]
        return []

    def forward(self, transcript: str, session_context: dict | None) -> SpeakerIntent:
        session_context_str = json.dumps(session_context) if session_context else "{}"
        prediction = self.predictor(transcript=transcript, session_context=session_context_str)

        try:
            score_raw = getattr(prediction, 'confidence_score', "0.0")
            score = float(score_raw) if score_raw else 0.0

            key_phrases = self._parse_list_str_field(getattr(prediction, 'key_phrases_supporting_intent', []))
            secondary_intents_list = self._parse_list_str_field(getattr(prediction, 'secondary_intents', []))

        except (ValueError, TypeError, json.JSONDecodeError) as e:
            print(f"Error converting SpeakerIntent prediction fields: {e}. Prediction: {prediction}")
            return SpeakerIntent()

        return SpeakerIntent(
            inferred_intent=str(getattr(prediction, 'inferred_intent', "Unknown")),
            confidence_score=score,
            key_phrases_supporting_intent=key_phrases,
            overall_assessment=str(getattr(prediction, 'overall_assessment', "Analysis not available.")),
            secondary_intents=secondary_intents_list
        )

from backend.models import ConversationFlow # Add this
# json is already imported

class ConversationFlowSignature(dspy.Signature):
    """Analyze the transcript and session context (which may include dialogue acts and speaker diarization as JSON strings)
    to assess conversation flow.
    """
    transcript: str = dspy.InputField(desc="The conversation transcript to analyze.")
    # Session context might contain 'dialogue_acts_json' and 'speaker_diarization_json'
    session_context: str = dspy.InputField(desc="JSON string providing context. May include 'dialogue_acts_json' and 'speaker_diarization_json'. Can be empty.")

    engagement_level: str = dspy.OutputField(desc="Overall engagement level (e.g., Low, Medium, High).")
    topic_coherence_score: float = dspy.OutputField(desc="Coherence of topics discussed (0.0 to 1.0).")
    conversation_dominance: str = dspy.OutputField(desc="JSON string of a dictionary estimating speaker dominance, e.g., '{\"speaker_A\": 0.6, \"speaker_B\": 0.4}'.")
    turn_taking_efficiency: str = dspy.OutputField(desc="Assessment of turn-taking efficiency (e.g., Smooth, Frequent Overlaps).")
    conversation_phase: str = dspy.OutputField(desc="Current phase of conversation (e.g., Opening, Development, Closing).")
    flow_disruptions: str = dspy.OutputField(desc="JSON string of a list of identified disruptions to conversation flow (e.g., '[\"Frequent interruptions\"]'.")

class DSPyConversationFlowAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(ConversationFlowSignature)

    def _parse_list_str_field(self, prediction_field_value: Any) -> list[str]: # Helper from previous modules
        if isinstance(prediction_field_value, list):
            return [str(item).strip() for item in prediction_field_value if str(item).strip()]
        if isinstance(prediction_field_value, str) and prediction_field_value.strip():
            try:
                parsed_list = json.loads(prediction_field_value)
                if isinstance(parsed_list, list):
                    return [str(item).strip() for item in parsed_list if str(item).strip()]
                return [str(parsed_list).strip()] if str(parsed_list).strip() else []
            except json.JSONDecodeError:
                if ',' in prediction_field_value:
                     return [s.strip() for s in prediction_field_value.split(',') if s.strip()]
                else: # Treat as lines if no commas
                    return [s.strip() for s in prediction_field_value.splitlines() if s.strip()]
        return []

    def forward(self, transcript: str, session_context: dict | None,
                    # Keep original optional params, will be packed into session_context for DSPy
                    dialogue_acts: list | None = None,
                    speaker_diarization: list | None = None) -> ConversationFlow:

        # Prepare session_context for DSPy module
        dspy_session_context = session_context.copy() if session_context else {}
        if dialogue_acts:
            # Summarize to keep prompt shorter if many acts, as in original service
            if len(dialogue_acts) > 10:
                summary_acts = [f"{act.get('speaker', 'S')}: {act.get('act_type', 'Unknown')[:20]}..." for act in dialogue_acts[:5]]
                summary_acts.append("...")
                summary_acts.extend([f"{act.get('speaker', 'S')}: {act.get('act_type', 'Unknown')[:20]}..." for act in dialogue_acts[-2:]])
                dspy_session_context['dialogue_acts_json'] = json.dumps(summary_acts)
            else:
                dspy_session_context['dialogue_acts_json'] = json.dumps(dialogue_acts)
        if speaker_diarization:
            dspy_session_context['speaker_diarization_json'] = json.dumps(speaker_diarization)

        session_context_str = json.dumps(dspy_session_context) if dspy_session_context else "{}"

        prediction = self.predictor(transcript=transcript, session_context=session_context_str)

        try:
            coherence_score_raw = getattr(prediction, 'topic_coherence_score', "0.0")
            coherence_score = float(coherence_score_raw) if coherence_score_raw else 0.0

            dominance_str = getattr(prediction, 'conversation_dominance', '{}')
            dominance = json.loads(dominance_str) if dominance_str and dominance_str.strip() else {}
            if not isinstance(dominance, dict): dominance = {}

            disruptions = self._parse_list_str_field(getattr(prediction, 'flow_disruptions', []))


        except (ValueError, TypeError, json.JSONDecodeError) as e:
            print(f"Error converting ConversationFlow prediction fields: {e}. Prediction: {prediction}")
            return ConversationFlow() # Fallback

        return ConversationFlow(
            engagement_level=str(getattr(prediction, 'engagement_level', "Medium")),
            topic_coherence_score=coherence_score,
            conversation_dominance=dominance,
            turn_taking_efficiency=str(getattr(prediction, 'turn_taking_efficiency', "Analysis not available.")),
            conversation_phase=str(getattr(prediction, 'conversation_phase', "Analysis not available.")),
            flow_disruptions=disruptions
        )

# Added dspy import just in case it's not at the very top, though it should be.
import dspy
# json is already imported at the top
from backend.models import EmotionDetail # Add this

class TranscriptionSignature(dspy.Signature):
    """Transcribe the provided audio data accurately.
    If there are multiple speakers, indicate them as "Speaker 1:", "Speaker 2:", etc.
    Include all spoken words, including filler words. Preserve natural speech flow.
    """
    # For multimodal models, the prompt structure for dspy.Predict needs to align with
    # how the specific dspy.LM implementation (e.g., for Gemini) handles multimodal inputs.
    # Typically, this might involve passing structured data (like a dict) if the LM wrapper supports it,
    # or embedding base64 data directly if the model/LM takes it as a string field.
    # The current dspy.LM for Gemini might expect a specific format or might only support text.
    # This signature assumes the LM can interpret these fields for a multimodal task.
    # If dspy.LM for Gemini doesn't directly support passing base64 strings via fields for audio,
    # this approach would need adjustment, possibly by enhancing the LM wrapper or using a more
    # specific multimodal input field type if DSPy introduces one.
    audio_base64_string: str = dspy.InputField(desc="Base64 encoded string of the audio data.")
    audio_mime_type: str = dspy.InputField(desc="MIME type of the audio data (e.g., 'audio/wav', 'audio/mp3').")
    # context_prompt: str = dspy.InputField(desc="Optional context or specific instructions for transcription.", default="") # If needed later

    transcript_text: str = dspy.OutputField(desc="The transcribed text from the audio.")

class DSPyTranscriptionModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # Using Predict as transcription is often a direct instruction without complex reasoning steps.
        self.predictor = dspy.Predict(TranscriptionSignature)

    def forward(self, audio_base64_string: str, audio_mime_type: str) -> str:
        # The effectiveness of this depends HEAVILY on how dspy.LM for Gemini handles these fields.
        # It needs to construct a request that Gemini's multimodal API understands.
        # This might involve the dspy.LM wrapper creating a specific JSON structure for Gemini,
        # including the 'inlineData' part for the audio.
        # If this is not automatically handled by the dspy.LM for Gemini, this call will likely fail
        # or not perform as expected (e.g., treating base64 string as text).
        prediction = self.predictor(
            audio_base64_string=audio_base64_string,
            audio_mime_type=audio_mime_type
        )
        return getattr(prediction, 'transcript_text', "Transcription failed or returned no text.")

class EmotionAnalysisSignature(dspy.Signature):
    """Analyze the emotional content of the audio data and transcript.
    Identify primary emotions and their confidence scores.
    Focus on categories: neutral, happy, sad, angry, fear, surprise, disgust,
    confidence, uncertainty, stress, calm, excitement, boredom, sincerity, deception, nervousness, comfort.
    Return a JSON string list of emotion objects, each with "emotion" (label) and "score" fields.
    If inferable, also include "timestamp_start" and "timestamp_end" for each emotion segment.
    Example: '[{\"emotion\": \"neutral\", \"score\": 0.6, \"timestamp_start\": 0.5, \"timestamp_end\": 2.3}]'
    """
    # Similar to transcription, this assumes the dspy.LM for Gemini can handle multimodal input
    # by interpreting these fields correctly for the API call.
    audio_base64_string: str = dspy.InputField(desc="Base64 encoded string of the audio data.")
    audio_mime_type: str = dspy.InputField(desc="MIME type of the audio data.")
    transcript: str = dspy.InputField(desc="Transcript of the audio for context.")

    emotion_analysis_json: str = dspy.OutputField(desc="JSON string list of emotion objects.")

class DSPyEmotionAnalysisModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(EmotionAnalysisSignature) # Or ChainOfThought if reasoning helps

    def forward(self, audio_base64_string: str, audio_mime_type: str, transcript: str) -> list[EmotionDetail]:
        prediction = self.predictor(
            audio_base64_string=audio_base64_string,
            audio_mime_type=audio_mime_type,
            transcript=transcript
        )
        raw_json = getattr(prediction, 'emotion_analysis_json', "[]")
        try:
            emotions_data = json.loads(raw_json)
            if not isinstance(emotions_data, list):
                emotions_data = []

            parsed_emotions = []
            for item in emotions_data:
                if isinstance(item, dict) and 'emotion' in item and 'score' in item:
                    try:
                        score = float(item['score'])
                    except (ValueError, TypeError):
                        score = 0.0

                    parsed_emotions.append(EmotionDetail(
                        emotion=str(item['emotion']),
                        score=score,
                        timestamp_start=item.get('timestamp_start'),
                        timestamp_end=item.get('timestamp_end')
                    ))
            return parsed_emotions
        except json.JSONDecodeError:
            print(f"Error decoding emotion analysis JSON: {raw_json}")
            return []
