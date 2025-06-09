# AI Lie Detector - Backend

This backend is built using Python with the FastAPI framework. It provides API endpoints for analyzing audio content to detect potential deception.

## Key Technologies

- Python 3.9+
- FastAPI: For building high-performance APIs.
- Pydantic: For data validation.
- SpeechRecognition: For speech-to-text transcription (using Google Speech-to-Text).
- PyDub: For audio processing and quality assessment.
- Transformers (Hugging Face): For emotion analysis.
- Google Gemini: For advanced AI-driven analysis.

## Setup and Running

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    - Create a `.env` file in the `backend` directory or set environment variables directly.
    - The most important one is `GEMINI_API_KEY` for accessing the Google Gemini API.
      ```env
      GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
      ```

5.  **Run the development server:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The API will be accessible at `http://localhost:8000`.

## API Endpoints

The API provides several endpoints for audio analysis and session management.

- **`POST /analyze`**: Uploads an audio file and performs a comprehensive analysis.
    - **Request Body**: `multipart/form-data` with `audio` (file) and optional `session_id` (string).
    - **Response**: Detailed JSON object with transcript, audio quality, emotion analysis, credibility score, AI summary, linguistic patterns, risk assessment, and session insights.
- **`GET /`**: API root/health check.
- **`GET /test-structured-output`**: Returns a mock structured response for frontend testing.
- **`POST /session/new`**: Creates a new conversation session.
- **`GET /session/{session_id}/history`**: Retrieves the analysis history for a given session.
- **`DELETE /session/{session_id}`**: Deletes a session and its history.

For detailed API documentation, run the server and navigate to `http://localhost:8000/docs` in your browser to see the Swagger UI.

## Project Structure

- **`main.py`**: FastAPI application entry point, middleware configuration, and router inclusion.
- **`api/`**: Contains API route definitions.
    - `analysis_routes.py`: Routes related to audio analysis.
    - `general_routes.py`: General API routes like health check.
    - `session_routes.py`: Routes for session management.
- **`services/`**: Contains business logic and integrations with external services.
    - `audio_service.py`: Handles audio processing, transcription, and basic emotion analysis.
    - `gemini_service.py`: Interacts with the Google Gemini API for advanced analysis and structured output validation.
    - `linguistic_service.py`: Performs quantitative linguistic analysis on transcripts.
    - `session_insights_service.py`: Generates insights based on conversation history within a session.
    - `session_service.py`: Manages conversation sessions and history.
- **`models.py`**: Pydantic models for request/response validation and structuring data.
- **`config.py`**: Application configuration, including API keys and model loading for services like emotion analysis.
- **`requirements.txt`**: List of Python dependencies.

## Error Handling

The API uses standard HTTP status codes to indicate success or failure. Error responses are generally in JSON format with a "detail" field explaining the error.
Common status codes:
- `200 OK`: Request successful.
- `400 Bad Request`: Invalid input (e.g., invalid file type, missing parameters).
- `404 Not Found`: Resource not found (e.g., non-existent session ID).
- `413 Payload Too Large`: Uploaded file exceeds size limits.
- `422 Unprocessable Entity`: Validation error for request data.
- `500 Internal Server Error`: Unexpected server-side error.
- `503 Service Unavailable`: External service (e.g., speech recognition) error.
