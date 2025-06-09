# API Documentation: Analysis Routes (`analysis_routes.py`)

This document provides an overview of the API routes defined in `backend/api/analysis_routes.py`. These routes handle requests for various types of audio and text analysis, including full batch analysis, streaming analysis, and text-only analysis.

**General Purpose**: To expose endpoints that allow clients to submit audio or text data and receive comprehensive linguistic, psychological, and behavioral analyses. The routes interface with various backend services, many of which are powered by DSPy and Google Gemini models.

---

## WebSocket Endpoint: `/ws/{session_id}`

*   **HTTP Method**: WebSocket
*   **URL Path**: `/ws/{session_id}`
*   **Description**: Establishes a WebSocket connection for a given session ID. This connection is used by the `AnalysisStreamer` service to send real-time updates (analysis results, progress, errors) to the client during streaming analysis operations.
*   **Path Parameters**:
    *   `session_id: str`: The unique identifier for the session.
*   **Behavior**:
    *   Calls `analysis_streamer.connect(websocket, session_id)` to accept and store the connection.
    *   Enters a loop to `await websocket.receive_text()`, primarily to keep the connection alive and handle client-side messages if any were designed.
    *   On `WebSocketDisconnect`, it calls `analysis_streamer.disconnect(session_id)`.
*   **Key Services/Functions Called**:
    *   `analysis_streamer.connect`
    *   `analysis_streamer.disconnect`

---

## Endpoint: `/analyze/stream`

*   **HTTP Method**: POST
*   **URL Path**: `/analyze/stream`
*   **Tags**: `Analysis`
*   **Summary**: Stream Audio Analysis
*   **Description**: Accepts an audio file and initiates a streaming analysis pipeline. Results are streamed back to the client as Server-Sent Events (SSE).
*   **Request Parameters/Body**:
    *   `audio: UploadFile` = `File(...)`: The audio file to be analyzed (multipart/form-data). Valid content types include common audio and video formats (e.g., `audio/wav`, `video/mp4`, `audio/mp3`).
    *   `session_id: Optional[str]` = `Form(None)` (aliased as `session_id_form` in code): An optional session ID. If not provided, a new one is created or an existing one retrieved by `conversation_history_service`.
*   **Response**:
    *   **Success (200 OK)**: `StreamingResponse` with `media_type="text/event-stream"`. The stream consists of Server-Sent Events, each containing JSON data for progress updates, individual analysis results, or errors.
    *   **Error (422 Unprocessable Entity)**: If the uploaded file is not a valid audio type.
    *   **Error (500 Internal Server Error)**: If an unexpected error occurs during the streaming pipeline setup or execution (e.g., file handling issues, critical pipeline error). Detail provided in the response.
*   **Key Services/Functions Called**:
    *   `conversation_history_service.get_or_create_session`: To manage the session ID.
    *   `stream_analysis_pipeline` (from `backend.services.streaming_service`): This is the core function that orchestrates the multi-step analysis and generates the SSE stream. The audio file is saved to a temporary path before being passed to this pipeline.
*   **Error Handling**:
    *   Validates audio file type based on content type and extension.
    *   Handles exceptions during file operations and pipeline execution, returning HTTP 500.
    *   Ensures temporary audio files are deleted in a `finally` block.

---

## Endpoint: `/analyze`

*   **HTTP Method**: POST
*   **URL Path**: `/analyze`
*   **Tags**: `Analysis`
*   **Summary**: Analyze Audio File (DSPy Pipeline)
*   **Description**: Uploads an audio file (max 15MB) and performs a comprehensive, non-streaming (batch) analysis using DSPy-powered services.
*   **Request Parameters/Body**:
    *   `audio: UploadFile` = `File(...)`: The audio file (e.g., WAV, MP3). Maximum size is 15MB.
    *   `session_id: Optional[str]` = `Form(None)` (aliased as `session_id_form` in code): Optional session ID.
*   **Response**:
    *   **Success (200 OK)**: `AnalyzeResponse` (Pydantic model) containing a comprehensive set of analysis results including transcript, audio quality, emotion analysis, and various text-based analyses (manipulation, arguments, etc.), plus session insights if applicable.
    *   **Error (400 Bad Request)**: If the file is not a valid audio format.
    *   **Error (413 Payload Too Large)**: If the file size exceeds 15MB.
    *   **Error (422 Unprocessable Entity)**: For validation errors not caught by other specific codes.
    *   **Error (500 Internal Server Error)**: For unexpected server-side errors during analysis.
*   **Key Services/Functions Called**:
    *   `conversation_history_service.get_or_create_session`
    *   `conversation_history_service.get_session_context`
    *   `full_audio_analysis_pipeline_dspy` (from `backend.pipelines`): This function orchestrates the entire analysis process for a given audio file, likely calling various DSPy-powered services.
    *   `session_insights_generator.generate_session_insights` (if `previous_analyses > 0` in session context).
    *   `conversation_history_service.add_analysis`: To store the results.
*   **Error Handling**:
    *   Validates audio file type and size.
    *   Uses a `try-except-finally` block to ensure temporary audio file cleanup.
    *   Catches `HTTPException`s and re-raises them.
    *   Catches general exceptions and returns an HTTP 500.
*   **Response Model Population**: Includes logic to ensure all fields of the `AnalyzeResponse` model are populated, using default values for any missing keys from the pipeline output to prevent validation errors.

---

## Endpoint: `/analyze_text`

*   **HTTP Method**: POST
*   **URL Path**: `/analyze_text`
*   **Tags**: `Analysis`
*   **Summary**: Analyze Text Input (DSPy Services)
*   **Description**: Accepts raw text input and performs a suite of DSPy-powered analyses (manipulation, argument structure, speaker attitude, etc.). This endpoint is for analyzing text directly without audio input.
*   **Request Parameters/Body**:
    *   `request_data: Dict[str, Any]` (JSON body): Expected to contain:
        *   `"text": str`: The text to analyze (must be at least 10 characters).
        *   `"speaker_name": Optional[str]` (Default: "Speaker").
    *   `session_id: Optional[str]` = `Form(None)` (aliased as `session_id_form` in code): Optional session ID.
*   **Response**:
    *   **Success (200 OK)**: `AnalyzeResponse` (Pydantic model) containing the aggregated results from various text analysis services, along with dummy/default values for audio-related fields (like `audio_quality_metrics`, `emotion_analysis`).
    *   **Error (400 Bad Request)**: If the input text is less than 10 characters.
    *   **Error (500 Internal Server Error)**: For unexpected server-side errors.
*   **Key Services/Functions Called**:
    *   `conversation_history_service.get_or_create_session`
    *   `conversation_history_service.get_session_context`
    *   `GeminiService()`: Instantiated to ensure DSPy LM is configured.
    *   Multiple DSPy-powered analysis services are instantiated and their `analyze` methods are called concurrently using `asyncio.gather`:
        *   `ManipulationService`
        *   `ArgumentService`
        *   `SpeakerAttitudeService`
        *   `EnhancedUnderstandingService`
        *   `PsychologicalService`
        *   `TextAudioAnalysisService` (for text-inferred audio features)
        *   `QuantitativeMetricsService`
        *   `ConversationFlowService`
        *   `SpeakerIntentService`
    *   `analyze_linguistic_patterns` (from `backend.services.linguistic_service`): Called using `asyncio.to_thread`.
    *   `session_insights_generator.generate_session_insights` (if applicable).
    *   `conversation_history_service.add_analysis`.
*   **Error Handling**:
    *   Validates text length.
    *   Logs if DSPy LM is not configured (analysis will use service-level fallbacks).
    *   `asyncio.gather` is used with `return_exceptions=True` to handle errors from individual analysis tasks gracefully, logging them and using default Pydantic models for failed tasks.
    *   General error handling for unexpected issues.
*   **Response Model Population**: Similar to the `/analyze` route, it ensures all fields of `AnalyzeResponse` are present, providing defaults for missing data or data not applicable to text-only analysis (e.g., `audio_quality_metrics` is default, `transcript` is the input text).

---
