"""
Pydantic Models for API Data Structures

This file defines all Pydantic models used for request and response validation,
data serialization/deserialization, and OpenAPI schema generation for the API.
These models ensure data consistency and provide clear data contracts for API consumers.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

# --- Pydantic Models for API Request/Response Schemas ---

class AudioQualityMetrics(BaseModel):
    """Metrics related to the quality of the processed audio."""
    duration: float = Field(..., example=15.7, description="Duration of the audio in seconds.")
    sample_rate: int = Field(..., example=44100, description="Sample rate of the audio in Hertz (Hz).")
    channels: int = Field(..., example=1, description="Number of audio channels (e.g., 1 for mono, 2 for stereo).")
    loudness: float = Field(..., example=-25.5, description="Average loudness of the audio in dBFS (decibels relative to full scale).")
    quality_score: int = Field(..., example=85, ge=0, le=100, description="An overall quality score for the audio, typically ranging from 0 to 100.")

class EmotionScore(BaseModel):
    """Represents a detected emotion and its confidence score."""
    label: str = Field(..., example="neutral", description="The label of the detected emotion (e.g., 'anger', 'joy', 'sadness', 'neutral').")
    score: float = Field(..., example=0.85, ge=0.0, le=1.0, description="The confidence score for the detected emotion, ranging from 0.0 to 1.0.")

class GeminiSummary(BaseModel):
    """Detailed summary and interpretation from the Gemini AI analysis."""
    tone: str = Field(..., example="The speaker's tone was generally calm but showed signs of hesitation when discussing future plans.", description="Detailed analysis of the speaker's vocal tone, pitch, and delivery.")
    motivation: str = Field(..., example="The speaker seems motivated by a desire for recognition, though financial aspects are also mentioned.", description="Assessment of underlying motivations and intent derived from the content and vocal cues.")
    credibility: str = Field(..., example="Credibility is assessed as moderate due to inconsistencies in timelines provided.", description="Specific credibility assessment with reasoning based on content and vocal patterns.")
    emotional_state: str = Field(..., example="The speaker's emotional state appeared to shift from confident to anxious when questioned about specifics.", description="Analysis of emotional consistency and authenticity throughout the speech.")
    communication_style: str = Field(..., example="The speaker uses clear, direct language but occasionally resorts to vague terms when pressed.", description="Analysis of communication patterns, verbal behaviors, and use of language.")
    key_concerns: str = Field(..., example="Notable pauses before answering critical questions and increased pitch suggest discomfort with certain topics.", description="Main red flags, vocal stress indicators, or concerns identified during the analysis.")
    strengths: str = Field(..., example="The speaker maintains good eye contact (if video) and uses articulate language for most of the conversation.", description="Aspects of the speaker's communication that support credibility and authenticity.")

class LinguisticAnalysis(BaseModel):
    """Quantitative and qualitative analysis of linguistic patterns in the transcript."""
    # Quantitative metrics
    word_count: int = Field(..., example=250, description="Total number of words in the transcript.")
    hesitation_count: int = Field(..., example=12, description="Number of hesitation markers (e.g., 'um', 'uh', 'like', 'you know').")
    qualifier_count: int = Field(..., example=5, description="Number of words indicating uncertainty or qualification (e.g., 'maybe', 'perhaps', 'I think').")
    certainty_count: int = Field(..., example=8, description="Number of words indicating certainty or confidence (e.g., 'definitely', 'absolutely').")
    filler_count: int = Field(..., example=7, description="Number of common filler words (e.g., 'um', 'uh', 'er', 'ah').")
    repetition_count: int = Field(..., example=3, description="Number of immediately repeated words or short phrases detected.")
    formality_score: float = Field(..., example=65.5, ge=0, le=100, description="Formality score (0-100) based on language usage, where higher is more formal.")
    complexity_score: float = Field(..., example=72.0, ge=0, le=100, description="Linguistic complexity score (0-100) based on vocabulary and sentence structure.")
    avg_word_length: float = Field(..., example=4.5, description="Average length of words in characters.")
    avg_words_per_sentence: float = Field(..., example=15.2, description="Average number of words per sentence.")
    sentence_count: int = Field(..., example=16, description="Total number of sentences identified in the transcript.")
    speech_rate_wpm: Optional[float] = Field(None, example=150.0, description="Speaker's speech rate in words per minute. Available if audio duration is known.")
    hesitation_rate_hpm: Optional[float] = Field(None, alias="hesitation_rate", example=10.0, description="Number of hesitations per minute. Available if audio duration is known.") # Alias for backward compatibility if needed
    confidence_ratio: float = Field(..., example=0.62, ge=0, le=1, description="Ratio of certainty indicators to the sum of certainty and qualifier indicators (0 to 1). Higher values suggest more confident language.")
    
    # Descriptive analysis (can be generated by linguistic service or Gemini)
    speech_patterns: str = Field(..., example="The speaker exhibited a moderate pace with occasional pauses.", description="Qualitative description of speech rhythm, pace, pauses, and fluency.")
    word_choice: str = Field(..., example="Vocabulary was generally formal, with some use of technical jargon.", description="Qualitative analysis of vocabulary richness, specificity, and appropriateness of phrasing.")
    emotional_consistency: str = Field(..., example="Reported emotions appear consistent with the language used, though some nervousness is noted.", description="Assessment of consistency between linguistically expressed emotions and other vocal/content cues.")
    detail_level: str = Field(..., example="The speaker provided a high level of detail on technical aspects but was vague on personal motivations.", description="Analysis of the level of detail provided (e.g., specific vs. vague, elaborate vs. concise).")

class RiskAssessment(BaseModel):
    """Assessment of overall risk and specific factors contributing to it."""
    overall_risk: str = Field(..., example="medium", description="Overall assessed risk level (e.g., 'low', 'medium', 'high').")
    risk_factors: List[str] = Field(..., example=["Contradictory statements about timelines", "Hesitation when discussing finances"], description="A list of specific factors identified that contribute to the risk assessment.")
    mitigation_suggestions: List[str] = Field(..., example=["Request clarification on timeline discrepancies.", "Ask for detailed financial records."], description="Actionable suggestions to mitigate or further investigate the identified risks.")

# New Models for Enhanced Analysis Dimensions (as introduced in Gemini prompt)
class ManipulationAssessment(BaseModel):
    """Assessment of manipulative language and tactics used by the speaker."""
    manipulation_score: int = Field(default=0, ge=0, le=100, example=25, description="Likelihood score (0-100) of manipulative language being used.")
    manipulation_tactics: List[str] = Field(default=[], example=["Flattery", "Guilt-tripping"], description="A list of identified manipulative tactics (e.g., gaslighting, guilt-tripping, flattery).")
    manipulation_explanation: str = Field(default="N/A", example="The speaker used excessive flattery early on, potentially to build undue rapport.", description="Explanation of how and why the identified manipulative tactics were used.")
    example_phrases: List[str] = Field(default=[], example=["You're too smart to fall for that trick."], description="Specific phrases from the transcript that exemplify the identified manipulative tactics.")

class ArgumentAnalysis(BaseModel):
    """Analysis of the speaker's arguments, including strengths, weaknesses, and coherence."""
    argument_strengths: List[str] = Field(default=[], example=["Provided clear data points for sales figures."], description="List of identified strong points or well-supported claims in the speaker's arguments.")
    argument_weaknesses: List[str] = Field(default=[], example=["Relied on anecdotal evidence for market trends."], description="List of identified weak points, logical fallacies, or unsupported claims in the speaker's arguments.")
    overall_argument_coherence_score: int = Field(default=0, ge=0, le=100, example=70, description="An overall score (0-100) representing the logical coherence and structure of the speaker's arguments.")

class SpeakerAttitude(BaseModel):
    """Evaluation of the speaker's attitude, including respectfulness and detection of sarcasm."""
    respect_level_score: int = Field(default=50, ge=0, le=100, example=80, description="A score (0-100) indicating the level of respectfulness detected in the speaker's tone and language (higher is more respectful).")
    sarcasm_detected: bool = Field(default=False, example=True, description="Boolean flag indicating whether sarcasm was detected in the speaker's communication.")
    sarcasm_confidence_score: int = Field(default=0, ge=0, le=100, example=65, description="Confidence score (0-100) in the detection of sarcasm, if `sarcasm_detected` is true.")
    tone_indicators_respect_sarcasm: List[str] = Field(default=[], example=["Used polite address terms.", "Slightly mocking tone when saying 'of course'"], description="Specific words, phrases, or vocal tone characteristics that indicate respectfulness or sarcasm.")

class EnhancedUnderstanding(BaseModel):
    """Deeper insights into the conversation, such as inconsistencies, evasiveness, and areas for follow-up."""
    key_inconsistencies: List[str] = Field(default=[], example=["Claimed to be at the meeting, but later said they were out of town."], description="List of key contradictions or inconsistencies found in the speaker's statements across the conversation.")
    areas_of_evasiveness: List[str] = Field(default=[], example=["Avoided direct answers about budget allocation."], description="Topics or questions where the speaker appeared to be evasive or deflective.")
    suggested_follow_up_questions: List[str] = Field(default=[], example=["Can you provide the exact dates you were out of town?"], description="A list of suggested follow-up questions to clarify ambiguities or probe areas of concern.")
    unverified_claims: List[str] = Field(default=[], example=["Claimed 90% customer satisfaction without citing a source."], description="Specific claims made by the speaker that may require external fact-checking or further verification.")

class AudioAnalysis(BaseModel): # Added based on Gemini prompt, good to have distinct from linguistic.
    """Specific analysis of audio features beyond basic quality metrics."""
    vocal_stress_indicators: str = Field(default="N/A", description="Specific vocal stress patterns detected (e.g., pitch changes, strained voice).")
    speaking_rate_variations: str = Field(default="N/A", description="Changes in speaking speed and fluency during the conversation.")
    pitch_analysis: str = Field(default="N/A", description="Analysis of pitch variations and their potential emotional undertones.")
    pause_patterns: str = Field(default="N/A", description="Analysis of significant pauses, hesitations, or interruptions in speech flow.")
    voice_quality: str = Field(default="N/A", description="Overall assessment of voice quality, clarity, and authenticity.")


class SessionInsights(BaseModel):
    """Aggregated insights derived from analyzing the entire session history."""
    consistency_analysis: str = Field(..., example="Speaker shows high consistency in credibility (avg: 75/100) and emotional state.", description="Analysis of consistency in speaker's statements, credibility, and emotions across the session.")
    behavioral_evolution: str = Field(..., example="Speaker's formality decreased over the session, while speech rate increased slightly.", description="Analysis of how the speaker's behavior (e.g., stress, formality) evolved during the conversation.")
    risk_trajectory: str = Field(..., example="Overall risk remained low but showed a slight increase in the last segment.", description="Analysis of the trend in risk levels and deception indicators throughout the session.")
    conversation_dynamics: str = Field(..., example="The conversation had a moderate pace with balanced turn-taking.", description="Analysis of the overall conversation flow, pace, and interaction patterns.")

class AnalyzeResponse(BaseModel):
    """The main response model for the /analyze endpoint, consolidating all analysis results."""
    session_id: str = Field(..., example="a1b2c3d4-e5f6-7890-1234-567890abcdef", description="Unique identifier for the current conversation session.")
    transcript: str = Field(..., example="Hello, this is a test audio for analysis.", description="Full transcribed text from the provided audio.")
    audio_quality: AudioQualityMetrics = Field(..., description="Detailed metrics assessing the quality of the input audio.")
    emotion_analysis: List[EmotionScore] = Field(..., description="A list of detected emotions, each with a label and confidence score.")
    speaker_transcripts: Dict[str, str] = Field(..., example={"Speaker 1": "Hello, this is a test."}, description="Transcript content separated by identified speakers. The key is the speaker label (e.g., 'Speaker 1').")
    red_flags_per_speaker: Dict[str, List[str]] = Field(..., example={"Speaker 1": ["Increased hesitation before critical answers."]}, description="List of potential deception indicators or red flags identified for each speaker.")
    credibility_score: int = Field(..., example=75, ge=0, le=100, description="Overall credibility score assigned to the speaker's statements, ranging from 0 to 100.")
    confidence_level: str = Field(..., example="medium", description="The analysis model's confidence in its assessment (e.g., 'high', 'medium', 'low').")
    gemini_summary: GeminiSummary = Field(..., description="A detailed narrative summary and interpretation of the analysis from the Gemini AI model.")
    recommendations: List[str] = Field(..., example=["Clarify point X.", "Observe non-verbal cues for topic Y."], description="Actionable recommendations based on the overall analysis.")
    linguistic_analysis: LinguisticAnalysis = Field(..., description="Comprehensive analysis of quantitative and qualitative linguistic patterns.")
    risk_assessment: RiskAssessment = Field(..., description="Detailed risk assessment including overall risk, contributing factors, and mitigation suggestions.")
    audio_analysis: AudioAnalysis = Field(..., description="Detailed analysis of audio-specific features like vocal stress and pitch.") # Added this field
    session_insights: Optional[SessionInsights] = Field(None, description="Optional insights generated by analyzing the conversation history within the current session. Not present for the first analysis of a session.")

    # Adding new optional analysis dimension fields, ensuring descriptions are clear.
    manipulation_assessment: Optional[ManipulationAssessment] = Field(None, description="Optional: Assessment of manipulative language and tactics, if detected or applicable.")
    argument_analysis: Optional[ArgumentAnalysis] = Field(None, description="Optional: Analysis of the speaker's argument structure, strengths, weaknesses, and coherence.")
    speaker_attitude: Optional[SpeakerAttitude] = Field(None, description="Optional: Evaluation of the speaker's attitude, including respectfulness and sarcasm detection.")
    enhanced_understanding: Optional[EnhancedUnderstanding] = Field(None, description="Optional: Deeper insights such as key inconsistencies, areas of evasiveness, suggested follow-up questions, and unverified claims.")

class NewSessionResponse(BaseModel):
    """Response model for confirming the creation of a new session."""
    session_id: str = Field(..., example="a1b2c3d4-e5f6-7890-1234-567890abcdef", description="The unique identifier for the newly created conversation session.")
    message: str = Field(..., example="New session created successfully.", description="A confirmation message indicating the outcome of the session creation request.")

class SessionHistoryItem(BaseModel):
    """Represents a single entry in the session's conversation history."""
    timestamp: datetime = Field(..., description="The date and time when this analysis entry was recorded.")
    transcript: str = Field(..., example="This was my statement at that time.", description="The transcript corresponding to this specific analysis entry in the history.")
    analysis: Dict[str, Any] = Field(..., example={"credibility_score": 60, "top_emotion": "neutral"}, description="A summarized version or key metrics of the analysis result for this historical entry.")
    analysis_number: int = Field(..., example=3, description="The sequential number of this analysis within the session (e.g., 1st, 2nd, 3rd analysis).")

class SessionHistoryResponse(BaseModel):
    """Response model for providing the history of a conversation session."""
    session_id: str = Field(..., example="a1b2c3d4-e5f6-7890-1234-567890abcdef", description="The session ID for which the history is being provided.")
    history: List[SessionHistoryItem] = Field(..., description="A list of analysis entries, each representing a segment of the conversation history for the session.")

class DeleteSessionResponse(BaseModel):
    """Response model for confirming the deletion of a session."""
    session_id: str = Field(..., example="a1b2c3d4-e5f6-7890-1234-567890abcdef", description="The unique identifier of the session that was successfully deleted.")
    message: str = Field(..., example="Session deleted successfully.", description="A confirmation message indicating the outcome of the session deletion request.")

class ErrorResponse(BaseModel):
    """Standard error response model for API errors."""
    detail: str = Field(..., example="File processing error: Invalid audio format.", description="A detailed message describing the error that occurred.")
