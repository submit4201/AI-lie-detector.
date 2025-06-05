import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException # For type hinting if needed, not for raising in tests
import os
from unittest.mock import patch, MagicMock, mock_open # For more complex mocking if needed

# It's good practice to ensure the app is loaded from the correct path
# especially if tests are run from a different directory.
# However, TestClient typically handles this by importing the app instance.
from backend.main import app, conversation_history # Import your FastAPI app

client = TestClient(app)

# --- Test Data & Helper Functions ---
VALID_AUDIO_FILENAME = "test_audio.wav"
INVALID_AUDIO_FILENAME = "test_text.txt"

# Create dummy audio file content (actual WAV content is not strictly necessary if pydub is mocked)
# For a simple "non-empty" check, any bytes would do.
# A real minimal WAV header might be better if not mocking pydub deeply.
DUMMY_WAV_CONTENT = b"RIFF....WAVEfmt ...." # Minimal non-empty bytes

@pytest.fixture(autouse=True)
def clear_session_store_before_each_test():
    """Fixture to clear the session store before each test."""
    conversation_history.sessions.clear()
    yield # Test runs here
    conversation_history.sessions.clear() # Cleanup after test if needed, though usually new app instance per test is cleaner if possible

# --- Session Management Endpoint Tests ---

def test_create_new_session():
    response = client.post("/session/new")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "message" in data
    assert data["message"] == "New session created successfully."
    assert len(data["session_id"]) == 36 # UUID4 length

def test_get_session_history_empty():
    # Create a session first
    session_response = client.post("/session/new")
    session_id = session_response.json()["session_id"]

    response = client.get(f"/session/{session_id}/history")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["history"] == []

def test_get_session_history_non_existent():
    non_existent_session_id = "non-existent-uuid"
    response = client.get(f"/session/{non_existent_session_id}/history")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Session ID '{non_existent_session_id}' not found."

def test_delete_session():
    # Create a session
    session_response = client.post("/session/new")
    session_id = session_response.json()["session_id"]

    # Delete the session
    response = client.delete(f"/session/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["message"] == "Session deleted successfully."

    # Verify it's gone
    history_response = client.get(f"/session/{session_id}/history")
    assert history_response.status_code == 404

def test_delete_session_non_existent():
    non_existent_session_id = "non-existent-uuid-for-delete"
    response = client.delete(f"/session/{non_existent_session_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Session ID '{non_existent_session_id}' not found or already deleted."


# --- /analyze Endpoint Tests (Initial Setup) ---

# Mocked external dependencies for /analyze endpoint
@pytest.fixture
def mock_audio_segment(mocker):
    mock = mocker.patch("backend.main.AudioSegment.from_file")
    # Mock instance methods if they are called on the result of from_file
    mock_instance = MagicMock()
    mock_instance.frame_rate = 16000
    mock_instance.channels = 1
    mock_instance.dBFS = -10.0 # Example loudness
    # mock_instance.export = MagicMock(return_value=None) # if export is called
    # mock.__len__ = MagicMock(return_value=5000) # if len(audio_segment) is used
    # Making len(audio_segment) work:
    type(mock_instance).duration_seconds = property(MagicMock(return_value=5.0)) # pydub uses duration_seconds
    # For assess_audio_quality:
    # len(audio_segment) / 1000.0 -> mock_instance.duration_seconds
    # audio_segment.frame_rate -> mock_instance.frame_rate
    # audio_segment.channels -> mock_instance.channels
    # audio_segment.dBFS -> mock_instance.dBFS

    # Make from_file return this configured instance
    mock.return_value = mock_instance
    return mock # This is the mock for AudioSegment itself, if needed

@pytest.fixture
def mock_speech_recognizer(mocker):
    mock_recognizer_instance = MagicMock()
    # Configure the recognize_google method
    mock_recognizer_instance.recognize_google.return_value = "This is a test transcript."

    mock_sr = mocker.patch("backend.main.sr.Recognizer")
    mock_sr.return_value = mock_recognizer_instance # When sr.Recognizer() is called

    # Mock sr.AudioFile as a context manager
    mock_audio_file = mocker.patch("backend.main.sr.AudioFile")
    mock_audio_file.return_value.__enter__.return_value = MagicMock() # Mock the result of __enter__
    mock_audio_file.return_value.__exit__.return_value = None

    return mock_sr, mock_recognizer_instance # Return both for easier access in tests

@pytest.fixture
def mock_emotion_classifier(mocker):
    mock = mocker.patch("backend.main.emotion_classifier")
    mock.return_value = [ # Example structure from transformers pipeline
        {"label": "neutral", "score": 0.8},
        {"label": "joy", "score": 0.1},
    ]
    return mock

@pytest.fixture
def mock_gemini_api(mocker):
    mock_post = mocker.patch("backend.main.requests.post")
    mock_response = MagicMock()
    mock_response.status_code = 200
    # A minimal valid JSON structure expected by validate_and_structure_gemini_response
    # Needs to align with the fields accessed in that function and the Pydantic models
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": json.dumps({ # The text part itself should be a JSON string
                        "speaker_transcripts": {"Speaker 1": "Test transcript from Gemini."},
                        "red_flags_per_speaker": {"Speaker 1": []},
                        "credibility_score": 80,
                        "confidence_level": "high",
                        "gemini_summary": {
                            "tone": "neutral", "motivation": "information", "credibility": "high",
                            "emotional_state": "calm", "communication_style": "clear",
                            "key_concerns": "none", "strengths": "clarity"
                        },
                        "recommendations": ["No specific recommendations."],
                        "linguistic_analysis": {
                            "speech_patterns": "normal", "word_choice": "simple",
                            "emotional_consistency": "consistent", "detail_level": "adequate"
                        },
                        "risk_assessment": {
                            "overall_risk": "low", "risk_factors": [], "mitigation_suggestions": []
                        }
                    })
                }]
            }
        }]
    }
    mock_post.return_value = mock_response
    return mock_post

# More tests for /analyze will be added here
# test_analyze_audio_success, test_analyze_audio_invalid_file_type, etc.

# Placeholder for a successful /analyze test
def test_analyze_audio_success(mock_audio_segment, mock_speech_recognizer, mock_emotion_classifier, mock_gemini_api):
    # Ensure dummy audio file exists for the test client to "upload"
    # TestClient handles file uploads by reading bytes from a file-like object

    # Create a dummy file in the current directory or a specified test temp directory
    # For simplicity here, using a BytesIO, but TestClient can also take a path.
    from io import BytesIO

    files = {"audio": (VALID_AUDIO_FILENAME, BytesIO(DUMMY_WAV_CONTENT), "audio/wav")}
    response = client.post("/analyze", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["transcript"] == "This is a test transcript."
    assert data["credibility_score"] == 80 # From mock_gemini_api
    assert data["audio_quality"]["quality_score"] > 0 # Check some derived value
    assert "session_id" in data

    # Verify mocks were called (example)
    mock_audio_segment.assert_called_once() # Check AudioSegment.from_file was called
    sr_recognizer_constructor, sr_recognizer_instance = mock_speech_recognizer
    sr_recognizer_constructor.assert_called_once() # sr.Recognizer()
    sr_recognizer_instance.recognize_google.assert_called_once()
    mock_emotion_classifier.assert_called_once()
    mock_gemini_api.assert_called_once()

def test_analyze_audio_invalid_content_type():
    from io import BytesIO
    files = {"audio": ("test.txt", BytesIO(b"This is not an audio file"), "text/plain")}
    response = client.post("/analyze", files=files)
    assert response.status_code == 400 # Based on our explicit check
    assert response.json()["detail"] == "File must be an audio file"

def test_analyze_audio_speech_recognition_unknown_value(mock_audio_segment, mock_speech_recognizer, mock_emotion_classifier):
    sr_recognizer_constructor, sr_recognizer_instance = mock_speech_recognizer
    # Configure recognize_google to raise UnknownValueError
    sr_recognizer_instance.recognize_google.side_effect = sr.UnknownValueError("API could not understand audio")

    from io import BytesIO
    files = {"audio": (VALID_AUDIO_FILENAME, BytesIO(DUMMY_WAV_CONTENT), "audio/wav")}
    response = client.post("/analyze", files=files)

    assert response.status_code == 400
    assert "Could not understand the audio" in response.json()["detail"]
    mock_emotion_classifier.assert_not_called() # Should not reach emotion analysis

def test_analyze_audio_speech_recognition_request_error(mock_audio_segment, mock_speech_recognizer, mock_emotion_classifier):
    sr_recognizer_constructor, sr_recognizer_instance = mock_speech_recognizer
    # Configure recognize_google to raise RequestError
    sr_recognizer_instance.recognize_google.side_effect = sr.RequestError("API unavailable")

    from io import BytesIO
    files = {"audio": (VALID_AUDIO_FILENAME, BytesIO(DUMMY_WAV_CONTENT), "audio/wav")}
    response = client.post("/analyze", files=files)

    assert response.status_code == 503 # Service Unavailable
    assert "Speech recognition service error: API unavailable" in response.json()["detail"]
    mock_emotion_classifier.assert_not_called()

def test_analyze_audio_short_transcript(mock_audio_segment, mock_speech_recognizer, mock_emotion_classifier):
    sr_recognizer_constructor, sr_recognizer_instance = mock_speech_recognizer
    sr_recognizer_instance.recognize_google.return_value = "Hi" # Too short

    from io import BytesIO
    files = {"audio": (VALID_AUDIO_FILENAME, BytesIO(DUMMY_WAV_CONTENT), "audio/wav")}
    response = client.post("/analyze", files=files)

    assert response.status_code == 400
    assert "Transcript too short or empty" in response.json()["detail"]
    mock_emotion_classifier.assert_not_called()

def test_analyze_audio_gemini_api_error(mock_audio_segment, mock_speech_recognizer, mock_emotion_classifier, mock_gemini_api):
    # Configure mock_gemini_api (which mocks requests.post) to return an error
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Gemini internal server error"
    mock_gemini_api.return_value = mock_response

    from io import BytesIO
    files = {"audio": (VALID_AUDIO_FILENAME, BytesIO(DUMMY_WAV_CONTENT), "audio/wav")}
    response = client.post("/analyze", files=files)

    # The backend's query_gemini returns a dict with "error" key,
    # then validate_and_structure_gemini_response uses default structure but logs a warning.
    # The overall /analyze response should still be 200 but with default Gemini values.
    assert response.status_code == 200
    data = response.json()
    assert data["gemini_summary"]["tone"] == "Analysis pending - technical issue encountered" # Default value
    assert data["credibility_score"] == 50 # Default value

def test_analyze_audio_gemini_malformed_json(mock_audio_segment, mock_speech_recognizer, mock_emotion_classifier, mock_gemini_api):
    # Configure mock_gemini_api to return malformed JSON in the text part
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "this is not json"}]}}]
    }
    mock_gemini_api.return_value = mock_response

    from io import BytesIO
    files = {"audio": (VALID_AUDIO_FILENAME, BytesIO(DUMMY_WAV_CONTENT), "audio/wav")}
    response = client.post("/analyze", files=files)

    assert response.status_code == 200
    data = response.json()
    # Should use default structure due to parsing error
    assert data["gemini_summary"]["tone"] == "Analysis pending - technical issue encountered"
    assert data["credibility_score"] == 50
    # We can also check logs if we could capture them, to see the warning about parsing failure.

# Example of how to test session history being populated (simplified)
def test_analyze_populates_session_history(mock_audio_segment, mock_speech_recognizer, mock_emotion_classifier, mock_gemini_api):
    session_res = client.post("/session/new")
    session_id = session_res.json()["session_id"]

    from io import BytesIO
    files = {"audio": (VALID_AUDIO_FILENAME, BytesIO(DUMMY_WAV_CONTENT), "audio/wav")}

    # First analysis
    client.post("/analyze", files=files, data={"session_id": session_id})

    # Second analysis
    # Re-configure mock_speech_recognizer if its state matters for different calls or make it stateless
    sr_constructor, sr_instance = mock_speech_recognizer
    sr_instance.recognize_google.return_value = "Second transcript for history."
    # Re-configure gemini if its state matters
    mock_gemini_api.return_value.json.return_value["candidates"][0]["content"]["parts"][0]["text"] = json.dumps({
        "speaker_transcripts": {"Speaker 1": "Second Gemini transcript."},
        "red_flags_per_speaker": {"Speaker 1": []}, "credibility_score": 70, "confidence_level": "medium",
        "gemini_summary": {
            "tone": "calm", "motivation": "info", "credibility": "medium",
            "emotional_state": "neutral", "communication_style": "direct",
            "key_concerns": "none", "strengths": "directness"
        },
        "recommendations": ["None"], "linguistic_analysis": {
            "speech_patterns": "even", "word_choice": "clear",
            "emotional_consistency": "yes", "detail_level": "good"
        },
        "risk_assessment": {"overall_risk": "low", "risk_factors": [], "mitigation_suggestions": []}
    })

    client.post("/analyze", files=files, data={"session_id": session_id})

    history_response = client.get(f"/session/{session_id}/history")
    assert history_response.status_code == 200
    data = history_response.json()
    assert len(data["history"]) == 2
    assert data["history"][0]["transcript"] == "This is a test transcript."
    assert data["history"][0]["analysis_summary"]["credibility_score"] == 80 # From first call's Gemini mock
    assert data["history"][1]["transcript"] == "Second transcript for history."
    assert data["history"][1]["analysis_summary"]["credibility_score"] == 70 # From second call's Gemini mock
