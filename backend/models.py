from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

# --- Pydantic Models for API Documentation ---

class AudioQualityMetrics(BaseModel):
    duration: float = Field(default=0.0, description="Duration of the audio in seconds.")
    sample_rate: int = Field(default=0, description="Sample rate of the audio in Hz.")
    channels: int = Field(default=0, description="Number of audio channels.")
    loudness: float = Field(default=0.0, description="Loudness of the audio in dBFS.")
    quality_score: int = Field(default=0, description="Overall quality score (0-100).")
    overall_quality: str = Field(default="Good", description="Overall quality assessment (e.g., 'Good', 'Fair', 'Poor').")
    signal_to_noise_ratio: float = Field(default=0.0, description="Signal to noise ratio.")
    clarity_score: float = Field(default=50.0, description="Audio clarity score (0-100).")
    volume_consistency: float = Field(default=50.0, description="Volume consistency score (0-100).")
    background_noise_level: float = Field(default=0.0, description="Background noise level assessment.")

class EmotionScore(BaseModel):
    label: str = Field(default="", description="Emotion label (e.g., 'anger', 'joy').")
    score: float = Field(default=0.0, description="Confidence score for the emotion (0.0-1.0).")

class NumericalLinguisticMetrics(BaseModel):
    word_count: int = Field(default=0, description="Total number of words in the transcript.")
    unique_word_count: int = Field(default=0, description="Total number of unique words in the transcript.")
    hesitation_marker_count: int = Field(default=0, description="Number of common hesitation markers (e.g., um, uh, er, ah).")
    filler_word_count: int = Field(default=0, description="Number of common filler words (e.g., like, you know, basically).")  # Differentiated from hesitation markers
    qualifier_count: int = Field(default=0, description="Number of uncertainty qualifiers (e.g., maybe, perhaps, might, sort of, kind of).")
    certainty_indicator_count: int = Field(default=0, description="Number of certainty indicators (e.g., definitely, absolutely, sure, clearly).")
    repetition_count: int = Field(default=0, description="Number of significant word or phrase repetitions detected.")
    sentence_count: int = Field(default=0, description="Total number of sentences.")
    avg_word_length_chars: float = Field(default=0.0, description="Average word length in characters.")
    avg_sentence_length_words: float = Field(default=0.0, description="Average number of words per sentence.")
    speech_rate_wpm: Optional[float] = Field(default=None, description="Speech rate in words per minute (calculated if audio duration is known or can be estimated).")
    hesitation_rate_hpm: Optional[float] = Field(default=None, description="Hesitation markers per minute (calculated if audio duration is known or can be estimated).")
    vocabulary_richness_ttr: float = Field(default=0.0, description="Type-Token Ratio (unique words / total words) as a measure of vocabulary richness.")
    confidence_metric_ratio: Optional[float] = Field(default=None, description="Ratio of certainty indicators to the sum of certainty and uncertainty indicators. Ranges from 0 (all uncertainty) to 1 (all certainty), or None if no indicators found.")
    formality_score_calculated: float = Field(default=0.0, description="Calculated formality score (0-100) based on specific linguistic cues, not LLM opinion.")
    complexity_score_calculated: float = Field(default=0.0, description="Calculated linguistic complexity score (0-100) based on metrics like sentence length, word length, etc.")

class LinguisticAnalysis(BaseModel):
    # Descriptive analysis (for backwards compatibility or direct LLM assessment)
    speech_patterns_description: str = Field(default="Speech patterns analysis not available.", description="LLM analysis of speech rhythm, pace, pauses not covered by specific counts.")
    word_choice_description: str = Field(default="Word choice analysis not available.", description="LLM analysis of vocabulary and phrasing choices, beyond simple counts.")
    emotional_consistency_description: str = Field(default="Emotional consistency analysis not available.", description="LLM assessment of consistency between claimed emotions and linguistic expression.")
    detail_level_description: str = Field(default="Detail level analysis not available.", description="LLM assessment of whether the level of detail is appropriate versus vague or overly granular.")

    # LLM-generated analysis of numerical linguistic data (referencing NumericalLinguisticMetrics)
    word_count_analysis: str = Field(default="Word count analysis not available.", description="LLM interpretation of the significance of the word count in context.")
    hesitation_marker_analysis: str = Field(default="Hesitation marker analysis not available.", description="LLM interpretation of the impact of hesitation markers on communication.")
    filler_word_analysis: str = Field(default="Filler word analysis not available.", description="LLM interpretation of the impact of filler words on communication.")
    qualifier_analysis: str = Field(default="Qualifier analysis not available.", description="LLM interpretation of the impact of uncertainty qualifiers.")
    certainty_indicator_analysis: str = Field(default="Certainty indicator analysis not available.", description="LLM interpretation of the impact of certainty indicators.")
    repetition_analysis: str = Field(default="Repetition analysis not available.", description="LLM interpretation of word/phrase repetitions and their implications.")
    sentence_count_analysis: str = Field(default="Sentence count analysis not available.", description="LLM interpretation of the sentence count in context.")
    avg_word_length_analysis: str = Field(default="Average word length analysis not available.", description="LLM interpretation of average word length and its implications.")
    avg_sentence_length_analysis: str = Field(default="Average sentence length analysis not available.", description="LLM interpretation of average sentence length and its implications.")
    speech_rate_analysis: str = Field(default="Speech rate analysis not available.", description="LLM interpretation of speech rate (WPM) and its impact, if WPM is available.")
    hesitation_rate_analysis: str = Field(default="Hesitation rate analysis not available.", description="LLM interpretation of hesitation rate (HPM) and its impact, if HPM is available.")
    vocabulary_richness_analysis: str = Field(default="Vocabulary richness analysis not available.", description="LLM interpretation of vocabulary richness (TTR) and its implications.")
    confidence_metric_analysis: str = Field(default="Confidence metric analysis not available.", description="LLM interpretation of the calculated confidence metric ratio.")
    formality_score_analysis: str = Field(default="Formality score analysis not available.", description="LLM interpretation of the calculated formality score.")
    complexity_score_analysis: str = Field(default="Complexity score analysis not available.", description="LLM interpretation of the calculated complexity score.")
    pause_occurrence_analysis: str = Field(default="Pause analysis not available.", description="LLM analysis of pauses (based on transcript markers or audio silence detection) and their significance.")  # Renamed from pause_analysis
    overall_linguistic_style_summary: str = Field(default="Overall linguistic style summary not available.", description="LLM's comprehensive summary of linguistic patterns and their implications.")  # Renamed from overall_linguistic_analysis

class RiskAssessment(BaseModel):
    overall_risk: str = Field(default="Risk assessment not available.", description="Overall risk level (low/medium/high).")
    risk_factors: List[str] = Field(default_factory=list, description="Specific risk factors identified.")
    mitigation_suggestions: List[str] = Field(default_factory=list, description="Suggestions to mitigate identified risks.")
    # New fields for risk assessment
    risk_factors_analysis: str = Field(default="Risk factors analysis not available.", description="Analysis of each risk factor and its implications.")
    mitigation_suggestions_analysis: str = Field(default="Mitigation suggestions analysis not available.", description="Analysis of each mitigation suggestion and its potential impact.")
    overall_risk_analysis: str = Field(default="Overall risk analysis not available.", description="Overall analysis of the risk assessment and its implications.")
    confidence_in_risk_assessment: float = Field(default=0.0, description="Confidence level in the risk assessment (0-1).")


# New Models for Enhanced Analysis Dimensions

class SessionStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    PENDING = "pending"

class AnalysisInput(BaseModel):
    session_id: Optional[str] = None
    audio_file_path: Optional[str] = None
    transcript_file_path: Optional[str] = None
    text_input: Optional[str] = None
    language: str = "en"
    user_id: Optional[str] = None
    enable_detailed_analysis: bool = True

class EmotionDetail(BaseModel):
    emotion: str
    score: float
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None

class PatternDetail(BaseModel):
    pattern_type: str  # e.g., "RepetitivePhrasing", "HesitationCluster"
    description: str
    occurrences: int
    examples: List[str] = Field(default_factory=list)
    significance_score: Optional[float] = None  # 0-1 scale

class DialogueAct(BaseModel):
    speaker: str
    act_type: str  # e.g., "Question", "Statement", "Agreement", "Disagreement"
    text_segment: str
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None

class SpeakerSegment(BaseModel):
    speaker_label: str = "Unknown"
    start_time: float
    end_time: float
    transcript_segment: Optional[str] = None

# New Detailed Analysis Models
class ManipulationAssessment(BaseModel):
    is_manipulative: bool = False
    manipulation_score: float = Field(default=0.0, description="Score from 0.0 to 1.0 indicating likelihood of manipulation.")
    manipulation_techniques: List[str] = Field(default_factory=list, description="List of identified manipulation techniques.")
    manipulation_confidence: float = Field(default=0.0, description="Confidence in the manipulation assessment.")
    manipulation_explanation: str = Field(default="Analysis not available.", description="Explanation of the manipulation assessment.")
    manipulation_score_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the manipulation score.")

class ArgumentAnalysis(BaseModel):
    arguments_present: bool = False
    key_arguments: List[Dict[str, str]] = Field(default_factory=list, description="List of key arguments, e.g., {'claim': '...', 'evidence': '...'}."
    )
    argument_strength: float = Field(default=0.0, description="Overall strength of arguments presented (0.0 to 1.0).")
    fallacies_detected: List[str] = Field(default_factory=list, description="List of logical fallacies detected.")
    argument_summary: str = Field(default="Analysis not available.", description="Summary of the arguments.")
    argument_structure_rating: float = Field(default=0.0, description="Rating of the argument structure (0.0 to 1.0).")
    argument_structure_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the argument structure.")

class SpeakerAttitude(BaseModel):
    dominant_attitude: str = Field(default="Neutral", description="Dominant attitude of the speaker.")
    attitude_scores: Dict[str, float] = Field(default_factory=dict, description="Scores for various attitudes, e.g., {'respectful': 0.8}."
    )
    respect_level: str = Field(default="Neutral", description="Assessed level of respect.")
    respect_level_score: float = Field(default=0.0, description="Numerical score for respect level (0.0 to 1.0).")
    respect_level_score_analysis: str = Field(default="Analysis not available.", description="Analysis of the respect level score.")
    formality_score: float = Field(default=0.0, description="Formality score (0.0 informal to 1.0 formal).")
    formality_assessment: str = Field(default="Analysis not available.", description="Qualitative assessment of formality.")
    politeness_score: float = Field(default=0.0, description="Politeness score (0.0 to 1.0).")
    politeness_assessment: str = Field(default="Analysis not available.", description="Qualitative assessment of politeness.")

class EnhancedUnderstanding(BaseModel):
    key_topics: List[str] = Field(default_factory=list, description="Key topics discussed.")
    action_items: List[str] = Field(default_factory=list, description="Identified action items.")
    unresolved_questions: List[str] = Field(default_factory=list, description="Unresolved questions from the conversation.")
    summary_of_understanding: str = Field(default="Analysis not available.", description="Summary of the core understanding derived.")
    contextual_insights: List[str] = Field(default_factory=list, description="Insights based on context.")
    nuances_detected: List[str] = Field(default_factory=list, description="Subtle nuances detected in communication.")
    key_inconsistencies: List[str] = Field(default_factory=list, description="List of key contradictions or inconsistencies in statements.")
    areas_of_evasiveness: List[str] = Field(default_factory=list, description="Topics or questions the speaker seemed to avoid.")
    suggested_follow_up_questions: List[str] = Field(default_factory=list, description="Suggested questions to ask for clarity or further probing.")
    unverified_claims: List[str] = Field(default_factory=list, description="Claims made by the speaker that may require fact-checking.")
    # new fields for enhanced understanding
    key_inconsistencies_analysis: str = Field(default="Key inconsistencies analysis not available.", description="Analysis of each key inconsistency and its implications.")
    areas_of_evasiveness_analysis: str = Field(default="Areas of evasiveness analysis not available.", description="Analysis of each area of evasiveness and its implications.")
    suggested_follow_up_questions_analysis: str = Field(default="Suggested follow-up questions analysis not available.", description="Analysis of each suggested follow-up question and its potential impact.")
    fact_checking_analysis: str = Field(default="Fact checking analysis not available.", description="Analysis of each unverified claim and its implications.")
    deep_dive_analysis: str = Field(default="Deep dive enhanced understanding analysis not available.", description="Deep dive analysis of the enhanced understanding.")


class PsychologicalAnalysis(BaseModel):
    emotional_state: str = Field(default="Neutral", description="Overall emotional state inferred.")
    emotional_state_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the inferred emotional state.")  # Added
    cognitive_load: str = Field(default="Normal", description="Inferred cognitive load (e.g., Low, Normal, High).")
    cognitive_load_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the inferred cognitive load.")  # Added
    stress_level: float = Field(default=0.0, description="Inferred stress level (0.0 to 1.0).")
    stress_level_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the inferred stress level.")
    confidence_level: float = Field(default=0.0, description="Inferred confidence level (0.0 to 1.0).")
    confidence_level_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the inferred confidence level.")  # Added
    psychological_summary: str = Field(default="Analysis not available.", description="Summary of the psychological state analysis.")
    potential_biases: List[str] = Field(default_factory=list, description="Identified potential cognitive biases.")
    potential_biases_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the identified potential cognitive biases and their possible impact.")  # Added

class SessionInsights(BaseModel):
    consistency_analysis: str = Field(default="Consistency analysis not available.", description="Analysis of consistency patterns across session interactions.")
    behavioral_evolution: str = Field(default="Behavioral evolution analysis not available.", description="How speaker behavior has evolved throughout the session.")
    risk_trajectory: str = Field(default="Risk trajectory analysis not available.", description="Trend analysis of risk levels across the session.")
    conversation_dynamics: str = Field(default="Conversation dynamics analysis not available.", description="Analysis of conversation flow and interaction patterns.")
    # new fields for session insights
    consistency_analysis_analysis: str = Field(default="Consistency analysis details not available.", description="Analysis of the consistency analysis and its implications.")
    behavioral_evolution_analysis: str = Field(default="Behavioral evolution details not available.", description="Analysis of the behavioral evolution and its implications.")
    risk_trajectory_analysis: str = Field(default="Risk trajectory details not available.", description="Analysis of the risk trajectory and its implications.")
    conversation_dynamics_analysis: str = Field(default="Conversation dynamics details not available.", description="Analysis of the conversation dynamics and its implications.")
    deep_dive_analysis: str = Field(default="Deep dive session insights analysis not available.", description="Deep dive analysis of the session insights.")
    overall_session_analysis: str = Field(default="Overall session analysis not available.", description="Overall analysis of the session insights.")
    trust_building_indicators: str = Field(default="Trust building indicators analysis not available.", description="Analysis of trust-building indicators in the conversation.")
    concern_escalation: str = Field(default="Concern escalation analysis not available.", description="Analysis of concern escalation patterns in the conversation.")


class AudioAnalysis(BaseModel):
    # Existing fields, some refined for clarity and with added analysis fields
    speech_clarity_score: float = Field(default=0.0, description="Clarity of speech (0.0 to 1.0).")
    speech_clarity_analysis: Optional[str] = Field(default="Analysis not available.", description="Explanation of the speech clarity assessment.")

    background_noise_assessment: str = Field(default="Low", description="Qualitative level of background noise (e.g., Low, Medium, High).")
    background_noise_analysis: Optional[str] = Field(default="Analysis not available.", description="Details about the background noise characteristics and impact.")

    average_speech_rate_wpm: int = Field(default=0, description="Average speech rate in words per minute, derived from audio timing and transcript word count.")
    speech_rate_variability_analysis: Optional[str] = Field(default="Analysis not available.", description="Analysis of speech rate consistency and significant variations observed in the audio.")

    intonation_patterns_analysis: str = Field(default="Analysis not available.", description="Description of intonation patterns (e.g., monotonous, expressive, questioning) and their perceived implications from the audio.")

    overall_audio_quality_assessment: str = Field(default="Analysis not available.", description="Overall qualitative assessment of the audio recording's technical quality.")

    # New fields for deeper audio analysis
    audio_duration_seconds: Optional[float] = Field(default=None, description="Duration of the analyzed audio segment in seconds.")

    loudness_dbfs: Optional[float] = Field(default=None, description="Average loudness of the audio in dBFS.")
    loudness_analysis: Optional[str] = Field(default="Analysis not available.", description="Analysis of audio volume levels (e.g., too quiet, too loud, appropriate, dynamic range).")

    signal_to_noise_ratio_db: Optional[float] = Field(default=None, description="Estimated signal-to-noise ratio in dB.")
    signal_to_noise_ratio_analysis: Optional[str] = Field(default="Analysis not available.", description="Explanation of SNR and its impact on intelligibility.")

    pitch_profile_analysis: Optional[str] = Field(default="Analysis not available.", description="Analysis of pitch characteristics from the audio (e.g., average, range, variability, common contours) and perceived meaning.")

    voice_timbre_description: Optional[str] = Field(default="Analysis not available.", description="Description of voice timbre/quality observed in the audio (e.g., resonant, thin, hoarse, nasal, breathy).")

    vocal_effort_assessment: Optional[str] = Field(default="Analysis not available.", description="Assessment of vocal effort apparent in the audio (e.g., strained, relaxed, projected, whispered).")

    acoustic_event_detection: List[str] = Field(default_factory=list, description="Notable non-speech acoustic events detected from the audio (e.g., cough, door slam, laughter).")
    acoustic_event_analysis: Optional[str] = Field(default="Analysis not available.", description="Analysis of detected acoustic events and their potential relevance or impact.")

    pause_characteristics_analysis: Optional[str] = Field(default="Analysis not available.", description="Analysis of pause frequency, duration, and placement from an acoustic perspective (silence detection).")

    vocal_stress_indicators_acoustic: List[str] = Field(default_factory=list, description="Acoustically identified vocal stress indicators from the audio (e.g., pitch breaks, voice tremors, strained phonation).")
    vocal_stress_indicators_acoustic_analysis: Optional[str] = Field(default="Analysis not available.", description="Explanation of the acoustically identified vocal stress indicators.")


class InteractionMetrics(BaseModel):  # Renamed from QuantitativeMetrics
    talk_to_listen_ratio: Optional[float] = Field(default=None, description="Ratio of talking time for a primary speaker to total speaking time or to other speakers' time. Context-dependent."
    )
    speaker_turn_duration_avg_seconds: Optional[float] = Field(default=None, description="Average duration of speaker turns in seconds, if speaker diarization is available."
    )
    interruptions_count: Optional[int] = Field(default=None, description="Number of interruptions detected, typically requiring diarization or explicit markers."
    )
    sentiment_trend: List[Dict[str, Any]] = Field(default_factory=list, description="Trend of sentiment over time or segments, e.g., [{'segment': 'opening', 'sentiment_score': 0.7, 'sentiment_label': 'positive'}]."
    )
    # Removed word_count and vocabulary_richness_score as they are in NumericalLinguisticMetrics

class ConversationFlow(BaseModel):
    engagement_level: str = Field(default="Medium", description="Overall engagement level (e.g., Low, Medium, High).")
    topic_coherence_score: float = Field(default=0.0, description="Coherence of topics discussed (0.0 to 1.0).")
    conversation_dominance: Dict[str, float] = Field(default_factory=dict, description="Speaker dominance, e.g., {'speaker_A': 0.6, 'speaker_B': 0.4}."
    )
    turn_taking_efficiency: str = Field(default="Analysis not available.", description="Assessment of turn-taking efficiency.")
    conversation_phase: str = Field(default="Analysis not available.", description="Current phase of conversation (e.g., Opening, Development, Closing).")
    flow_disruptions: List[str] = Field(default_factory=list, description="Identified disruptions in conversation flow.")

# Main Analysis Response Model
class AnalyzeResponse(BaseModel):
    session_id: str = ""
    transcript: str = ""
    enhanced_transcript: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    overall_sentiment: str = "Neutral"
    overall_sentiment_score: float = 0.0
    emotions_detected: List[str] = Field(default_factory=list)
    emotion_details: List[EmotionDetail] = Field(default_factory=list)
    communication_effectiveness_score: float = 0.0
    key_phrases: List[str] = Field(default_factory=list)
    summary: str = "Analysis not available."
    alerts: List[str] = Field(default_factory=list)
    patterns_identified: List[PatternDetail] = Field(default_factory=list)
    numerical_linguistic_metrics: Optional[NumericalLinguisticMetrics] = None  # Added
    dialogue_acts: List[DialogueAct] = Field(default_factory=list)
    speaker_diarization: List[SpeakerSegment] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, description="Overall confidence in the analysis results.")
    version: str = "2.1.0"  # Updated version due to significant model changes

    # Modularized analysis components
    manipulation_assessment: Optional[ManipulationAssessment] = None
    argument_analysis: Optional[ArgumentAnalysis] = None
    speaker_attitude: Optional[SpeakerAttitude] = None
    enhanced_understanding: Optional[EnhancedUnderstanding] = None
    psychological_analysis: Optional[PsychologicalAnalysis] = None
    audio_analysis: Optional[AudioAnalysis] = None
    interaction_metrics: Optional[InteractionMetrics] = None  # Updated from quantitative_metrics
    linguistic_analysis: Optional[LinguisticAnalysis] = None  # Ensure this is added if it wasn't explicitly part of AnalyzeResponse before
    conversation_flow: Optional[ConversationFlow] = None

class ProgressUpdate(BaseModel):
    stage: str
    percentage: float
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class AnalyzeStreamResponse(BaseModel):
    event_type: str  # e.g., "full_response", "interim_transcript", "analysis_update", "error", "progress_update"
    data: Optional[Any] = None  # Can be AnalyzeResponse, str (for transcript), or specific analysis model
    session_id: Optional[str] = None
    error_message: Optional[str] = None
    progress: Optional[ProgressUpdate] = None  # For granular progress updates

class StreamInput(BaseModel):
    session_id: str
    # Potentially other parameters like what to stream

# Session Management Models
class SessionCreateRequest(BaseModel):
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    initial_audio_path: Optional[str] = None  # Path to pre-existing audio
    initial_transcript_path: Optional[str] = None  # Path to pre-existing transcript
    configuration: Optional[Dict[str, Any]] = None  # e.g., specific analyses to run

class SessionCreateResponse(BaseModel):
    session_id: str
    status: SessionStatus
    message: str
    created_at: str  # ISO format timestamp

class SessionUpdateRequest(BaseModel):
    status: Optional[SessionStatus] = None
    # Potentially other fields to update, e.g., add new data

class SessionUpdateResponse(BaseModel):
    session_id: str
    status: SessionStatus
    message: str
    updated_at: str  # ISO format timestamp

class SessionResponse(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    status: SessionStatus
    created_at: str
    updated_at: Optional[str] = None
    # Potentially links to results or full analysis data if small
    analysis_summary: Optional[Dict[str, Any]] = None  # A brief overview

class SessionListItem(BaseModel):
    session_id: str
    session_name: Optional[str] = None
    status: SessionStatus
    created_at: str

class SessionInsightsInput(BaseModel):  # This is for multi-session analysis
    session_ids: List[str]
    insight_types: Optional[List[str]] = None  # e.g., ["sentiment_trend", "topic_comparison"]

class SessionInsight(BaseModel):  # This is for multi-session analysis
    insight_type: str
    data: Any  # Could be charts, tables, text summaries
    description: Optional[str] = None

class SessionInsightsResponse(BaseModel):  # This is for multi-session analysis
    requested_session_ids: List[str]
    insights: List[SessionInsight] = Field(default_factory=list)
    summary_across_sessions: Optional[str] = None

class GeminiSummary(BaseModel):
    tone: str = Field(default="Analysis not available", description="Description of the speaker's tone.")
    motivation: str = Field(default="Analysis not available", description="Analysis of the speaker's potential motivation.")
    credibility: str = Field(default="Analysis not available", description="Assessment of the speaker's credibility based on content and delivery.")
    emotional_state: str = Field(default="Analysis not available", description="Description of the speaker's emotional state.")
    communication_style: str = Field(default="Analysis not available", description="Analysis of the speaker's communication style.")
    key_concerns: str = Field(default="Analysis not available", description="Key concerns raised by the analysis.")
    strengths: str = Field(default="Analysis not available", description="Strengths of the speaker's communication.")


