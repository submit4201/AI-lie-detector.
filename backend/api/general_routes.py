"""
General API Routes

This module defines general-purpose API routes for the backend application,
such as health checks and testing endpoints.
"""
from fastapi import APIRouter
from models import AnalyzeResponse # Pydantic model for the structured response

router = APIRouter() # FastAPI router instance for these general routes

@router.get(
    "/",
    tags=["General"], # Tag for grouping in API documentation (e.g., Swagger UI)
    summary="API Root/Health Check",
    description="Provides a basic health check for the API. Confirms that the service is running and reachable."
)
async def root():
    """
    Root endpoint for the API.
    Serves as a health check, indicating that the API is operational.
    """
    # In a more complex application, this might include version information or status of critical services.
    # For this project, a simple message confirming the API is running is sufficient.
    # The original main.py used app.version; if that's needed, app/config would need to be accessible here.
    return {"message": "AI Lie Detector API is running and accessible."}

@router.get(
    "/test-structured-output",
    response_model=AnalyzeResponse, # Specifies the Pydantic model for the response.
    tags=["Testing"], # Groups this under "Testing" in API docs.
    summary="Get Mock Structured Analysis Response",
    description=(
        "Provides a complete, mock example of the `AnalyzeResponse` data structure. "
        "This endpoint is primarily intended for frontend development and testing, "
        "allowing developers to integrate and test UI components that display analysis results "
        "without needing to perform actual audio analysis."
    )
)
async def test_structured_output():
    """
    Returns a hardcoded, complete mock `AnalyzeResponse` object.
    
    This data can be used by frontend developers to:
    - Verify that their UI components correctly parse and display all fields.
    - Test different scenarios by modifying the mock data here (if needed for local testing).
    - Develop UI features without requiring a fully operational backend analysis pipeline.
    """

    # This mock_response is a complete and valid example of the AnalyzeResponse model.
    # It includes all nested structures and typical data patterns.
    mock_response = {
        "session_id": "test-session-123", # Example session ID
        "transcript": "This is a test transcript to verify the structured output display system is working correctly in the frontend application.",
        "audio_quality": {
            "duration": 5.2,
            "sample_rate": 44100,
            "channels": 1,
            "loudness": -20.5,
            "quality_score": 95
        },
        "emotion_analysis": [
            {"label": "neutral", "score": 0.7},
            {"label": "confidence", "score": 0.2},
            {"label": "slight_anxiety", "score": 0.1}
        ],
        "speaker_transcripts": {
            "Speaker 1": "This is a test transcript to verify the structured output display system is working correctly in the frontend application."
        },
        "red_flags_per_speaker": {
            "Speaker 1": [
                "Slightly elevated speech pace in middle section",
                "Brief pause before mentioning 'system'",
                "Minor vocal tension detected"
            ]
        },
        "credibility_score": 82,
        "confidence_level": "high",
        "gemini_summary": {
            "tone": "Professional and measured, with slight underlying tension suggesting awareness of being evaluated",
            "motivation": "Appears to be providing information for testing purposes with genuine intent to demonstrate system capabilities",
            "credibility": "High credibility overall with minor stress indicators typical of demonstration scenarios",
            "emotional_state": "Composed and focused, with slight performance anxiety which is normal for test scenarios",
            "communication_style": "Clear and articulate communication with professional vocabulary and structured delivery",
            "key_concerns": "Minor vocal tension suggests awareness of evaluation context; pace variations could indicate concentration on accuracy",
            "strengths": "Excellent clarity of speech; comprehensive information delivery; consistent tone throughout; professional presentation"
        },
        "recommendations": [
            "Continue with current communication approach as it demonstrates strong credibility",
            "Consider relaxation techniques if similar evaluation scenarios cause minor stress",
            "Maintain current level of detail and clarity in future communications"
        ],
        "linguistic_analysis": {
            "speech_patterns": "Consistent rhythm with appropriate pauses; professional pacing with minor acceleration during technical terms",
            "word_choice": "Technical vocabulary used appropriately; precise language selection; professional terminology maintained throughout",
            "emotional_consistency": "Emotions align well with stated purpose; minor tension consistent with demonstration context",
            "detail_level": "Excellent level of detail provided; comprehensive coverage of topic without excessive elaboration"
        },
        "risk_assessment": {
            "overall_risk": "low",
            "risk_factors": [
                "Minor performance anxiety in evaluation context",
                "Slight pace variations during technical descriptions"
            ],
            "mitigation_suggestions": [
                "No significant mitigation needed - patterns are normal for demonstration context",
                "Consider establishing comfort baseline before formal evaluations"
            ]
        },
        "session_insights": { # Example session insights data
            "consistency_analysis": "First analysis in session - establishing baseline patterns for future comparison. Credibility is stable.",
            "behavioral_evolution": "Initial session - no previous behavior patterns to compare. Speaker is using formal language.",
            "risk_trajectory": "Starting at low risk level - good foundation for the session. No concerning flags noted yet.",
            "conversation_dynamics": "Professional interaction style with clear demonstration intent. Response lengths are consistent."
        },
        # Ensuring all new fields from the Pydantic model are present
        "audio_analysis": {
            "vocal_stress_indicators": "Minor vocal tension detected, consistent with test scenario.",
            "speaking_rate_variations": "Slight acceleration when discussing technical details.",
            "pitch_analysis": "Pitch remained stable and within normal conversational range.",
            "pause_patterns": "Pauses were natural and used appropriately for emphasis.",
            "voice_quality": "Voice quality is clear and articulate."
        },
        "manipulation_assessment": {
            "manipulation_score": 10,
            "manipulation_tactics": ["Use of technical jargon to establish authority (minor)"],
            "manipulation_explanation": "The speaker uses technical terms which, while appropriate, can subtly create an air of authority. Not overtly manipulative.",
            "example_phrases": ["...verify the structured output display system..."]
        },
        "argument_analysis": {
            "argument_strengths": ["Clear statement of purpose", "Direct and unambiguous language"],
            "argument_weaknesses": ["Relies on the listener accepting the context of a 'test'"],
            "overall_argument_coherence_score": 85
        },
        "speaker_attitude": {
            "respect_level_score": 90,
            "sarcasm_detected": False,
            "sarcasm_confidence_score": 0,
            "tone_indicators_respect_sarcasm": ["Professional tone", "Helpful demeanor"]
        },
        "enhanced_understanding": {
            "key_inconsistencies": ["None noted in this test scenario."],
            "areas_of_evasiveness": ["Not applicable for a direct test statement."],
            "suggested_follow_up_questions": ["How does this integrate with real-time data feeds?"],
            "unverified_claims": ["None, as it's a statement of purpose."]
        }
    }
    
    # The **mock_response unpacks the dictionary into keyword arguments
    # for the AnalyzeResponse Pydantic model, which validates the data.
    return AnalyzeResponse(**mock_response)
