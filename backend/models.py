from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

# --- Pydantic Models for API Documentation ---

class AudioQualityMetrics(BaseModel):
    duration: float = Field(..., description="Duration of the audio in seconds.")
    sample_rate: int = Field(..., description="Sample rate of the audio in Hz.")
    channels: int = Field(..., description="Number of audio channels.")
    loudness: float = Field(..., description="Loudness of the audio in dBFS.")
    quality_score: int = Field(..., description="Overall quality score (0-100).")
    overall_quality: str = Field(default="Good", description="Overall quality assessment (e.g., 'Good', 'Fair', 'Poor').")
    signal_to_noise_ratio: float = Field(default=0.0, description="Signal to noise ratio.")
    clarity_score: float = Field(default=50.0, description="Audio clarity score (0-100).")
    volume_consistency: float = Field(default=50.0, description="Volume consistency score (0-100).")
    background_noise_level: float = Field(default=0.0, description="Background noise level assessment.")

class EmotionScore(BaseModel):
    label: str = Field(..., description="Emotion label (e.g., 'anger', 'joy').")
    score: float = Field(..., description="Confidence score for the emotion (0.0-1.0).")

class GeminiSummary(BaseModel):
    tone: str = Field(..., description="Detailed analysis of speaker's tone and manner.")
    motivation: str = Field(..., description="Assessment of underlying motivations and intent.")
    credibility: str = Field(..., description="Specific credibility assessment with reasoning.")
    emotional_state: str = Field(..., description="Emotional consistency and authenticity analysis.")
    communication_style: str = Field(..., description="Communication patterns and verbal behaviors.")
    key_concerns: str = Field(..., description="Main red flags or concerns identified.")
    strengths: str = Field(..., description="Aspects that support credibility.")

class LinguisticAnalysis(BaseModel):
    # Quantitative metrics
    word_count: int = Field(..., description="Total number of words in the transcript.")
    hesitation_count: int = Field(..., description="Number of hesitation markers (um, uh, er, ah, like, you know).")
    qualifier_count: int = Field(..., description="Number of uncertainty qualifiers (maybe, perhaps, might, etc.).")
    certainty_count: int = Field(..., description="Number of certainty indicators (definitely, absolutely, sure, etc.).")
    filler_count: int = Field(..., description="Number of filler words (um, uh, er, ah).")
    repetition_count: int = Field(..., description="Number of word repetitions detected.")
    formality_score: float = Field(..., description="Formality score (0-100) based on formal language usage.")
    complexity_score: float = Field(..., description="Linguistic complexity score (0-100).")
    avg_word_length: float = Field(..., description="Average word length in characters.")
    avg_words_per_sentence: float = Field(..., description="Average number of words per sentence.")
    sentence_count: int = Field(..., description="Total number of sentences.")
    speech_rate_wpm: Optional[float] = Field(None, description="Speech rate in words per minute (if duration available).")
    hesitation_rate: Optional[float] = Field(None, description="Hesitation rate per minute (if duration available).")
    confidence_ratio: float = Field(..., description="Ratio of certainty to uncertainty indicators (0-1).")
    
    # Descriptive analysis (for backwards compatibility)
    speech_patterns: str = Field(..., description="Analysis of speech rhythm, pace, pauses.")
    word_choice: str = Field(..., description="Analysis of vocabulary and phrasing choices.")
    emotional_consistency: str = Field(..., description="Consistency between claimed emotions and expression.")
    detail_level: str = Field(..., description="Appropriate level of detail vs vagueness.")

    # New fields for linguistic analysis
    pause_analysis: str = Field(..., description="Analysis of pauses and their significance.")
    filler_word_analysis: str = Field(..., description="Analysis of filler words and their impact.")
    repetition_analysis: str = Field(..., description="Analysis of word repetitions and their implications.")
    hesitation_analysis: str = Field(..., description="Analysis of hesitation markers and their impact.")
    qualifier_analysis: str = Field(..., description="Analysis of uncertainty qualifiers and their impact.")
    certainty_analysis: str = Field(..., description="Analysis of certainty indicators and their impact.")
    formality_analysis: str = Field(..., description="Analysis of formality in language usage.")
    complexity_analysis: str = Field(..., description="Analysis of linguistic complexity and its implications.")
    avg_word_length_analysis: str = Field(..., description="Analysis of average word length and its implications.")
    avg_words_per_sentence_analysis: str = Field(..., description="Analysis of average words per sentence and its implications.")
    sentence_count_analysis: str = Field(..., description="Analysis of sentence count and its implications.")
    overall_linguistic_analysis: str = Field(..., description="Overall analysis of linguistic patterns and their implications.")

class RiskAssessment(BaseModel):
    overall_risk: str = Field(..., description="Overall risk level (low/medium/high).")
    risk_factors: List[str] = Field(..., description="Specific risk factors identified.")
    mitigation_suggestions: List[str] = Field(..., description="Suggestions to mitigate identified risks.")

# New Models for Enhanced Analysis Dimensions
class ManipulationAssessment(BaseModel):
    manipulation_score: int = Field(default=0, ge=0, le=100, description="Likelihood of manipulative language (0-100).")
    manipulation_tactics: List[str] = Field(default=[], description="Identified manipulative tactics (e.g., gaslighting, guilt-tripping).")
    manipulation_explanation: str = Field(default="No manipulation detected.", description="Explanation of manipulative tactics used.")
    example_phrases: List[str] = Field(default=[], description="Specific phrases indicating manipulation.")

class ArgumentAnalysis(BaseModel):
    argument_strengths: List[str] = Field(default=[], description="Speaker's strong points in their arguments.")
    argument_weaknesses: List[str] = Field(default=[], description="Speaker's weak points in their arguments.")
    overall_argument_coherence_score: int = Field(default=50, ge=0, le=100, description="Overall coherence of the arguments (0-100).")

class SpeakerAttitude(BaseModel):
    respect_level_score: int = Field(default=50, ge=0, le=100, description="Level of respectfulness in speaker's tone (0-100, high is respectful).")
    sarcasm_detected: bool = Field(default=False, description="Indicates if sarcasm was detected.")
    sarcasm_confidence_score: int = Field(default=0, ge=0, le=100, description="Confidence in sarcasm detection (0-100, if sarcasm_detected is true).")
    tone_indicators_respect_sarcasm: List[str] = Field(default=[], description="Words or phrases indicating respect or sarcasm.")

class EnhancedUnderstanding(BaseModel):
    key_inconsistencies: List[str] = Field(default=[], description="List of key contradictions or inconsistencies in statements.")
    areas_of_evasiveness: List[str] = Field(default=[], description="Topics or questions the speaker seemed to avoid.")
    suggested_follow_up_questions: List[str] = Field(default=[], description="Suggested questions to ask for clarity or further probing.")
    unverified_claims: List[str] = Field(default=[], description="Claims made by the speaker that may require fact-checking.")

class SessionInsights(BaseModel):
    consistency_analysis: str = Field(..., description="Analysis of consistency patterns across session interactions.")
    behavioral_evolution: str = Field(..., description="How speaker behavior has evolved throughout the session.")
    risk_trajectory: str = Field(..., description="Trend analysis of risk levels across the session.")
    conversation_dynamics: str = Field(..., description="Analysis of conversation flow and interaction patterns.")

class AudioAnalysis(BaseModel):
    vocal_stress_indicators: List[str] = Field(default=[], description="Indicators of vocal stress detected in the audio.")
    pitch_analysis: str = Field(default="Audio analysis not available for text input.", description="Analysis of pitch variations and consistency.")
    pause_patterns: str = Field(default="Audio analysis not available for text input.", description="Analysis of pauses and their significance.")
    vocal_confidence_level: int = Field(default=50, ge=0, le=100, description="Confidence level in the speaker's vocal delivery (0-100).")
    speaking_pace_consistency: str = Field(default="Audio analysis not available for text input.", description="Analysis of speaking pace consistency.")
    speaking_rate_variations: str = Field(default="Audio analysis not available for text input.", description="Analysis of speaking rate variations.")
    voice_quality: str = Field(default="Audio analysis not available for text input.", description="Assessment of voice quality and authenticity.")
    
# Simple models that match service output
class QuantitativeMetrics(BaseModel):
    speech_rate_words_per_minute: int = Field(default=0, description="Estimated speech rate in words per minute.")
    formality_score: int = Field(default=50, ge=0, le=100, description="Formality score (0-100) based on formal language usage.")
    hesitation_count: int = Field(default=0, description="Number of hesitation markers detected.")
    filler_word_frequency: int = Field(default=0, description="Frequency of filler words per 100 words.")
    repetition_count: int = Field(default=0, description="Number of word repetitions detected.")
    sentence_length_variability: int = Field(default=50, ge=0, le=100, description="Variability in sentence lengths (0-100).")
    vocabulary_complexity: int = Field(default=50, ge=0, le=100, description="Complexity of vocabulary used (0-100).")
    






class AnalyzeResponse(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the conversation session.")
    speaker_name: str = Field(..., description="Name or identifier of the speaker.")
    transcript: str = Field(..., description="Transcribed text from the audio.")
    audio_quality: AudioQualityMetrics = Field(..., description="Metrics related to the audio quality.")
    emotion_analysis: List[EmotionScore] = Field(..., description="List of detected emotions and their scores.")
    speaker_transcripts: Dict[str, str] = Field(..., description="Transcript content separated by speaker.")
    red_flags_per_speaker: Dict[str, List[str]] = Field(..., description="Deception indicators found for each speaker.")
    credibility_score: int = Field(..., description="Overall credibility score (0-100).")
    confidence_level: str = Field(..., description="Analysis confidence level (e.g., 'high', 'medium').")
    gemini_summary: GeminiSummary = Field(..., description="Detailed summary from Gemini AI analysis.")
    recommendations: List[str] = Field(..., description="Actionable recommendations based on the analysis.")
    linguistic_analysis: LinguisticAnalysis = Field(..., description="Analysis of linguistic patterns.")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment details.")
    
    # Enhanced analysis dimensions (complex objects)
    session_insights: Optional[SessionInsights] = Field(None, description="Insights based on conversation history within the session.")
    manipulation_assessment: Optional[ManipulationAssessment] = Field(None, description="Assessment of manipulative language and tactics.")
    argument_analysis: Optional[ArgumentAnalysis] = Field(None, description="Analysis of argument strength, weaknesses, and coherence.")
    speaker_attitude: Optional[SpeakerAttitude] = Field(None, description="Evaluation of speaker's attitude, including respect and sarcasm.")
    enhanced_understanding: Optional[EnhancedUnderstanding] = Field(None, description="Deeper insights like inconsistencies, evasiveness, and follow-up questions.")
    audio_analysis: Optional[AudioAnalysis] = Field(None, description="Analysis of audio quality and speaker's vocal patterns.")
    quantitative_metrics: Optional[QuantitativeMetrics] = Field(None, description="Quantitative metrics extracted from linguistic analysis.")
    
    # Simple string/list fields for new analysis areas (matching actual service output)
    conversation_flow: Optional[str] = Field(None, description="Analysis of conversation flow and dynamics.")
    behavioral_patterns: Optional[str] = Field(None, description="Analysis of behavioral patterns within the conversation.")
    verification_suggestions: Optional[List[str]] = Field(None, description="Suggestions for verification and fact-checking.")
    
    # Legacy/compatibility fields
    overall_risk: Optional[str] = Field(None, description="Overall risk level (low/medium/high) based on all analysis.")
    deception_flags: Optional[List[str]] = Field(None, description="Overall deception flags (legacy, if still used).")
    


    
class NewSessionResponse(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the newly created session.")
    message: str = Field(..., description="Confirmation message.")

class SessionHistoryItem(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp of the analysis.")
    transcript: str = Field(..., description="Transcript of this analysis entry.")
    analysis: Dict[str, Any] = Field(..., description="A summary or key parts of the analysis result for this entry.")
    analysis_number: int = Field(..., description="Sequential number of this analysis in the session.")

class SessionHistoryResponse(BaseModel):
    session_id: str = Field(..., description="Session ID for the history.")
    history: List[SessionHistoryItem] = Field(..., description="List of analysis entries in the session.")

class DeleteSessionResponse(BaseModel):
    session_id: str = Field(..., description="ID of the deleted session.")
    message: str = Field(..., description="Confirmation message of deletion.")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Detailed error message.")

