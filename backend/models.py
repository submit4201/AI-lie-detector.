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

class RiskAssessment(BaseModel):
    overall_risk: str = Field(..., description="Overall risk level (low/medium/high).")
    risk_factors: List[str] = Field(..., description="Specific risk factors identified.")
    mitigation_suggestions: List[str] = Field(..., description="Suggestions to mitigate identified risks.")

class SessionInsights(BaseModel):
    consistency_analysis: str
    behavioral_evolution: str
    risk_trajectory: str
    conversation_dynamics: str

class AnalyzeResponse(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the conversation session.")
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
    session_insights: Optional[SessionInsights] = Field(None, description="Insights based on conversation history within the session.")

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
