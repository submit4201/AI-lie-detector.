from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
# from typing import Optional, Dict, List, Any # Duplicate, remove
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

class GeminiSummary(BaseModel): # This seems to be from an older structure, may need review if still used directly
    tone: str = Field(default="Tone analysis not available.", description="Detailed analysis of speaker's tone and manner.")
    motivation: str = Field(default="Motivation assessment not available.", description="Assessment of underlying motivations and intent.")
    credibility: str = Field(default="Credibility assessment not available.", description="Specific credibility assessment with reasoning.")
    emotional_state: str = Field(default="Emotional state analysis not available.", description="Emotional consistency and authenticity analysis.")
    communication_style: str = Field(default="Communication style analysis not available.", description="Communication patterns and verbal behaviors.")
    key_concerns: str = Field(default="Key concerns not identified.", description="Main red flags or concerns identified.")
    strengths: str = Field(default="Strengths not identified.", description="Aspects that support credibility.")

class LinguisticAnalysisModel(BaseModel): # Renamed from LinguisticAnalysis to avoid conflict if there's another
    word_count: int = Field(default=0, description="Total number of words in the transcript.")
    hesitation_count: int = Field(default=0, description="Number of hesitation markers (um, uh, er, ah, like, you know).")
    qualifier_count: int = Field(default=0, description="Number of uncertainty qualifiers (maybe, perhaps, might, etc.).")
    certainty_count: int = Field(default=0, description="Number of certainty indicators (definitely, absolutely, sure, etc.).")
    filler_count: int = Field(default=0, description="Number of filler words (um, uh, er, ah).")
    repetition_count: int = Field(default=0, description="Number of word repetitions detected.")
    formality_score: float = Field(default=0.0, description="Formality score (0-100) based on formal language usage.")
    complexity_score: float = Field(default=0.0, description="Linguistic complexity score (0-100).")
    avg_word_length: float = Field(default=0.0, description="Average word length in characters.")
    avg_words_per_sentence: float = Field(default=0.0, description="Average number of words per sentence.")
    sentence_count: int = Field(default=0, description="Total number of sentences.")
    speech_rate_wpm: Optional[float] = Field(None, description="Speech rate in words per minute (if duration available).")
    hesitation_rate: Optional[float] = Field(None, description="Hesitation rate per minute (if duration available).")
    confidence_ratio: float = Field(default=0.0, description="Ratio of certainty to uncertainty indicators (0-1).")
    speech_patterns: str = Field(default="Speech patterns analysis not available.", description="Analysis of speech rhythm, pace, pauses.")
    word_choice: str = Field(default="Word choice analysis not available.", description="Analysis of vocabulary and phrasing choices.")
    emotional_consistency: str = Field(default="Emotional consistency analysis not available.", description="Consistency between claimed emotions and expression.")
    detail_level: str = Field(default="Detail level analysis not available.", description="Appropriate level of detail vs vagueness.")
    pause_analysis: str = Field(default="Pause analysis not available.", description="Analysis of pauses and their significance.")
    filler_word_analysis: str = Field(default="Filler word analysis not available.", description="Analysis of filler words and their impact.")
    repetition_analysis: str = Field(default="Repetition analysis not available.", description="Analysis of word repetitions and their implications.")
    hesitation_analysis: str = Field(default="Hesitation analysis not available.", description="Analysis of hesitation markers and their impact.")
    qualifier_analysis: str = Field(default="Qualifier analysis not available.", description="Analysis of uncertainty qualifiers and their impact.")
    certainty_analysis: str = Field(default="Certainty analysis not available.", description="Analysis of certainty indicators and their impact.")
    formality_analysis: str = Field(default="Formality analysis not available.", description="Analysis of formality in language usage.")
    complexity_analysis: str = Field(default="Complexity analysis not available.", description="Analysis of linguistic complexity and its implications.")
    avg_word_length_analysis: str = Field(default="Average word length analysis not available.", description="Analysis of average word length and its implications.")
    avg_words_per_sentence_analysis: str = Field(default="Average words per sentence analysis not available.", description="Analysis of average words per sentence and its implications.")
    sentence_count_analysis: str = Field(default="Sentence count analysis not available.", description="Analysis of sentence count and its implications.")
    overall_linguistic_analysis: str = Field(default="Overall linguistic analysis not available.", description="Overall analysis of linguistic patterns and their implications.")

class RiskAssessment(BaseModel):
    overall_risk: str = Field(default="Risk assessment not available.", description="Overall risk level (low/medium/high).")
    risk_factors: List[str] = Field(default_factory=list, description="Specific risk factors identified.")
    mitigation_suggestions: List[str] = Field(default_factory=list, description="Suggestions to mitigate identified risks.")
    risk_factors_analysis: str = Field(default="Risk factors analysis not available.", description="Analysis of each risk factor and its implications.")
    mitigation_suggestions_analysis: str = Field(default="Mitigation suggestions analysis not available.", description="Analysis of each mitigation suggestion and its potential impact.")
    overall_risk_analysis: str = Field(default="Overall risk analysis not available.", description="Overall analysis of the risk assessment and its implications.")
    confidence_in_risk_assessment: float = Field(default=0.0, description="Confidence level in the risk assessment (0-1).")

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
    pattern_type: str
    description: str
    occurrences: int
    examples: List[str] = Field(default_factory=list)
    significance_score: Optional[float] = None

class LinguisticFeature(BaseModel): # Consider merging/aligning with LinguisticAnalysisModel
    word_count: int = 0
    unique_words: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    vocabulary_richness: Optional[float] = None

class DialogueAct(BaseModel):
    speaker: str
    act_type: str
    text_segment: str
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None

class SpeakerSegment(BaseModel):
    speaker_label: str = "Unknown"
    start_time: float
    end_time: float
    transcript_segment: Optional[str] = None

class ManipulationAssessment(BaseModel):
    is_manipulative: bool = False
    manipulation_score: float = Field(default=0.0, description="Score from 0.0 to 1.0 indicating likelihood of manipulation.")
    manipulation_techniques: List[str] = Field(default_factory=list, description="List of identified manipulation techniques.")
    manipulation_confidence: float = Field(default=0.0, description="Confidence in the manipulation assessment.")
    manipulation_explanation: str = Field(default="Analysis not available.", description="Explanation of the manipulation assessment.")
    manipulation_score_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the manipulation score.")

class ArgumentAnalysis(BaseModel):
    arguments_present: bool = False
    key_arguments: List[Dict[str, str]] = Field(default_factory=list, description="List of key arguments, e.g., {'claim': '...', 'evidence': '...'}.")
    argument_strength: float = Field(default=0.0, description="Overall strength of arguments presented (0.0 to 1.0).")
    fallacies_detected: List[str] = Field(default_factory=list, description="List of logical fallacies detected.")
    argument_summary: str = Field(default="Analysis not available.", description="Summary of the arguments.")
    argument_structure_rating: float = Field(default=0.0, description="Rating of the argument structure (0.0 to 1.0).")
    argument_structure_analysis: str = Field(default="Analysis not available.", description="Detailed analysis of the argument structure.")

class SpeakerAttitude(BaseModel):
    dominant_attitude: str = Field(default="Neutral", description="Dominant attitude of the speaker.")
    attitude_scores: Dict[str, float] = Field(default_factory=dict, description="Scores for various attitudes, e.g., {'respectful': 0.8}.")
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
    key_inconsistencies_analysis: str = Field(default="Key inconsistencies analysis not available.", description="Analysis of each key inconsistency and its implications.")
    areas_of_evasiveness_analysis: str = Field(default="Areas of evasiveness analysis not available.", description="Analysis of each area of evasiveness and its implications.")
    suggested_follow_up_questions_analysis: str = Field(default="Suggested follow-up questions analysis not available.", description="Analysis of each suggested follow-up question and its potential impact.")
    fact_checking_analysis: str = Field(default="Fact checking analysis not available.", description="Analysis of each unverified claim and its implications.")
    deep_dive_analysis: str = Field(default="Deep dive enhanced understanding analysis not available.", description="Deep dive analysis of the enhanced understanding.")

class PsychologicalAnalysis(BaseModel):
    emotional_state: str = Field(default="Neutral", description="Overall emotional state inferred.")
    cognitive_load: str = Field(default="Normal", description="Inferred cognitive load (e.g., Low, Normal, High).")
    stress_level: float = Field(default=0.0, description="Inferred stress level (0.0 to 1.0).")
    confidence_level: float = Field(default=0.0, description="Inferred confidence level (0.0 to 1.0).")
    psychological_summary: str = Field(default="Analysis not available.", description="Summary of the psychological state analysis.")
    potential_biases: List[str] = Field(default_factory=list, description="Identified potential cognitive biases.")

class SessionInsights(BaseModel):
    consistency_analysis: str = Field(default="Consistency analysis not available.", description="Analysis of consistency patterns across session interactions.")
    behavioral_evolution: str = Field(default="Behavioral evolution analysis not available.", description="How speaker behavior has evolved throughout the session.")
    risk_trajectory: str = Field(default="Risk trajectory analysis not available.", description="Trend analysis of risk levels across the session.")
    conversation_dynamics: str = Field(default="Conversation dynamics analysis not available.", description="Analysis of conversation flow and interaction patterns.")
    consistency_analysis_analysis: str = Field(default="Consistency analysis details not available.", description="Analysis of the consistency analysis and its implications.")
    behavioral_evolution_analysis: str = Field(default="Behavioral evolution details not available.", description="Analysis of the behavioral evolution and its implications.")
    risk_trajectory_analysis: str = Field(default="Risk trajectory details not available.", description="Analysis of the risk trajectory and its implications.")
    conversation_dynamics_analysis: str = Field(default="Conversation dynamics details not available.", description="Analysis of the conversation dynamics and its implications.")
    deep_dive_analysis: str = Field(default="Deep dive session insights analysis not available.", description="Deep dive analysis of the session insights.")
    overall_session_analysis: str = Field(default="Overall session analysis not available.", description="Overall analysis of the session insights.")
    trust_building_indicators: str = Field(default="Trust building indicators analysis not available.", description="Analysis of trust-building indicators in the conversation.")
    concern_escalation: str = Field(default="Concern escalation analysis not available.", description="Analysis of concern escalation patterns in the conversation.")
    
class TextAudioAnalysisModel(BaseModel): # Renamed from AudioAnalysis to avoid confusion with audio files/quality
    speech_clarity_score: float = Field(default=0.0, description="Clarity of speech (0.0 to 1.0).")
    background_noise_level: str = Field(default="Low", description="Level of background noise (e.g., Low, Medium, High).")
    speech_rate_wpm: int = Field(default=0, description="Average speech rate in words per minute.")
    pauses_and_fillers: Dict[str, int] = Field(default_factory=dict, description="Count of pauses and fillers, e.g., {'pauses': 5, 'um': 2}.")
    intonation_patterns: str = Field(default="Analysis not available.", description="Description of intonation patterns observed.")
    audio_quality_assessment: str = Field(default="Analysis not available.", description="Overall assessment of audio quality.")

class QuantitativeMetrics(BaseModel):
    talk_to_listen_ratio: float = Field(default=0.0, description="Ratio of talking time to listening time for a speaker or overall.")
    speaker_turn_duration_avg: float = Field(default=0.0, description="Average duration of speaker turns in seconds.")
    interruptions_count: int = Field(default=0, description="Number of interruptions detected.")
    sentiment_trend: List[Dict[str, float]] = Field(default_factory=list, description="Trend of sentiment over time, e.g., [{'time': 10.5, 'sentiment': 0.7}].")
    word_count: int = Field(default=0, description="Total word count.")
    vocabulary_richness_score: float = Field(default=0.0, description="Score indicating richness of vocabulary (e.g., TTR).")

class ConversationFlow(BaseModel):
    engagement_level: str = Field(default="Medium", description="Overall engagement level (e.g., Low, Medium, High).")
    topic_coherence_score: float = Field(default=0.0, description="Coherence of topics discussed (0.0 to 1.0).")
    conversation_dominance: Dict[str, float] = Field(default_factory=dict, description="Speaker dominance, e.g., {'speaker_A': 0.6, 'speaker_B': 0.4}.")
    turn_taking_efficiency: str = Field(default="Analysis not available.", description="Assessment of turn-taking efficiency.")
    conversation_phase: str = Field(default="Analysis not available.", description="Current phase of conversation (e.g., Opening, Development, Closing).")
    flow_disruptions: List[str] = Field(default_factory=list, description="Identified disruptions in conversation flow.")

class SpeakerIntent(BaseModel): # New Model Added Here
    inferred_intent: str = Field(default="Unknown", description="The primary inferred intent of the speaker (e.g., To persuade, To inform, To inquire, To build rapport, To resolve conflict).")
    confidence_score: float = Field(default=0.0, description="Confidence in the inferred intent (0.0 to 1.0).")
    key_phrases_supporting_intent: List[str] = Field(default_factory=list, description="Key phrases or statements from the transcript that support the inferred intent.")
    overall_assessment: str = Field(default="Analysis not available.", description="Brief justification or overall assessment of the speaker's intent.")
    secondary_intents: List[str] = Field(default_factory=list, description="Any secondary intents detected.")

# Main Analysis Response Model
class AnalyzeResponse(BaseModel):
    session_id: str = ""
    transcript: str = ""
    enhanced_transcript: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    overall_sentiment: str = "Neutral"
    overall_sentiment_score: float = 0.0
    emotions_detected: List[str] = Field(default_factory=list)
    emotion_details: List[EmotionDetail] = Field(default_factory=list)
    key_phrases: List[str] = Field(default_factory=list)
    summary: str = "Analysis not available."
    alerts: List[str] = Field(default_factory=list)
    patterns_identified: List[PatternDetail] = Field(default_factory=list)
    dialogue_acts: List[DialogueAct] = Field(default_factory=list)
    speaker_diarization: List[SpeakerSegment] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, description="Overall confidence in the analysis results.")
    version: str = "2.1.0" # Incremented version

    # Modularized analysis components
    audio_quality_metrics: Optional[AudioQualityMetrics] = None
    manipulation_assessment: Optional[ManipulationAssessment] = None
    argument_analysis: Optional[ArgumentAnalysis] = None
    speaker_attitude: Optional[SpeakerAttitude] = None
    enhanced_understanding: Optional[EnhancedUnderstanding] = None
    psychological_analysis: Optional[PsychologicalAnalysis] = None
    audio_analysis: Optional[TextAudioAnalysisModel] = None # Text-inferred audio characteristics
    quantitative_metrics: Optional[QuantitativeMetrics] = None
    conversation_flow: Optional[ConversationFlow] = None
    speaker_intent: Optional[SpeakerIntent] = None # Added new field
    session_insights: Optional[SessionInsights] = None
    linguistic_analysis: Optional[LinguisticAnalysisModel] = None


class ProgressUpdate(BaseModel):
    stage: str
    percentage: float
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class AnalyzeStreamResponse(BaseModel):
    event_type: str
    data: Optional[Any] = None
    session_id: Optional[str] = None
    error_message: Optional[str] = None
    progress: Optional[ProgressUpdate] = None

class StreamInput(BaseModel):
    session_id: str

# Session Management Models
class SessionCreateRequest(BaseModel):
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    initial_audio_path: Optional[str] = None
    initial_transcript_path: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

class SessionCreateResponse(BaseModel):
    session_id: str
    status: SessionStatus
    message: str
    created_at: str

class SessionUpdateRequest(BaseModel):
    status: Optional[SessionStatus] = None

class SessionUpdateResponse(BaseModel):
    session_id: str
    status: SessionStatus
    message: str
    updated_at: str

class SessionResponse(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    status: SessionStatus
    created_at: str
    updated_at: Optional[str] = None
    analysis_summary: Optional[Dict[str, Any]] = None

class SessionListItem(BaseModel):
    session_id: str
    session_name: Optional[str] = None
    status: SessionStatus
    created_at: str

class SessionInsightsInput(BaseModel):
    session_ids: List[str]
    insight_types: Optional[List[str]] = None

class SessionInsight(BaseModel):
    insight_type: str
    data: Any
    description: Optional[str] = None

class SessionInsightsResponse(BaseModel):
    requested_session_ids: List[str]
    insights: List[SessionInsight] = Field(default_factory=list)
    summary_across_sessions: Optional[str] = None

```
