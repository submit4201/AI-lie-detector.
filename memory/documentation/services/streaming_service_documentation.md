# Streaming Service Documentation (`streaming_service.py`)

This document provides an overview of the functionalities within `backend/services/streaming_service.py`. This module is primarily responsible for managing real-time analysis updates via WebSockets through the `AnalysisStreamer` class and for orchestrating a multi-step analysis pipeline for audio files, yielding results as Server-Sent Events (SSE) via the `stream_analysis_pipeline` function.

---

## Class: `AnalysisStreamer`

### Overall Purpose
The `AnalysisStreamer` class manages active WebSocket connections for different sessions. Its main role is to send various types of messages (analysis updates, progress updates, errors) to connected clients during a streaming analysis session.

---

### `__init__(self)`

#### Purpose
The constructor initializes the `AnalysisStreamer`.

#### Initialization
*   **`self.active_connections: Dict[str, WebSocket]`**: An in-memory dictionary to store active WebSocket connections, mapping session IDs to WebSocket objects.

---

### Public Methods

#### `async def connect(self, websocket: WebSocket, session_id: str)`
*   **Purpose**: Accepts a new WebSocket connection and stores it for the given session ID.
*   **Input Parameters**:
    *   `websocket: WebSocket`: The FastAPI WebSocket object for the client connection.
    *   `session_id: str`: The unique ID for the session.
*   **Key Operations**:
    *   Calls `await websocket.accept()`.
    *   Stores the `websocket` in `self.active_connections` mapped by `session_id`.
    *   Logs the connection.

#### `def disconnect(self, session_id: str)`
*   **Purpose**: Removes a WebSocket connection from the active list, typically called when a client disconnects.
*   **Input Parameters**:
    *   `session_id: str`: The ID of the session to disconnect.
*   **Key Operations**:
    *   Deletes the `session_id` entry from `self.active_connections` if it exists.
    *   Logs the disconnection.

#### `async def send_analysis_update(self, session_id: str, analysis_type: str, data: Any)`
*   **Purpose**: Sends a specific analysis result (e.g., transcription, emotion analysis) to the client connected for the given session ID.
*   **Input Parameters**:
    *   `session_id: str`: The target session ID.
    *   `analysis_type: str`: A string identifying the type of analysis being sent (e.g., "transcript", "manipulation_assessment").
    *   `data: Any`: The analysis data. If it's a Pydantic model, it's serialized using `.model_dump()` (Pydantic v2) or `.dict()` (Pydantic v1).
*   **Key Operations**:
    *   Constructs a message dictionary: `{"type": "analysis_update", "analysis_type": analysis_type, "data": payload_data}`.
    *   Sends the JSON serialized message via the WebSocket.
    *   Logs errors and disconnects the session if sending fails.

#### `async def send_progress_update(self, session_id: str, step: str, progress: int, total_steps: int)`
*   **Purpose**: Sends a progress update to the client, indicating the current step and overall progress of the analysis pipeline.
*   **Input Parameters**:
    *   `session_id: str`: The target session ID.
    *   `step: str`: Description of the current analysis step.
    *   `progress: int`: The current step number.
    *   `total_steps: int`: The total number of steps in the pipeline.
*   **Key Operations**:
    *   Calculates `percentage`.
    *   Constructs and sends a message: `{"type": "progress_update", "step": step, "progress": progress, "total_steps": total_steps, "percentage": ...}`.

#### `async def send_error(self, session_id: str, error_message: str)`
*   **Purpose**: Sends an error message to the client.
*   **Input Parameters**:
    *   `session_id: str`: The target session ID.
    *   `error_message: str`: The error message to send.
*   **Key Operations**:
    *   Constructs and sends a message: `{"type": "error", "message": error_message}`.

---

**Global Instance:**
A global instance `analysis_streamer = AnalysisStreamer()` is created for easy access to WebSocket functionalities.

---

## Asynchronous Generator Function: `stream_analysis_pipeline(audio_path: str, session_id: str, session_context: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]`

### Overall Purpose
This function orchestrates a multi-stage analysis of an audio file. It processes the audio through initial steps like quality assessment, transcription (DSPy-based), and emotion analysis (DSPy-based). Then, it iterates through a map of various text-based analysis services (like manipulation, argument, attitude, etc.), applying them to the transcript. Results are yielded incrementally as Server-Sent Events (SSE).

### Input Parameters
*   **`audio_path: str`**: The file system path to the audio file to be analyzed.
*   **`session_id: str`**: A unique identifier for the session, used for logging and potentially for context in future enhancements (though not directly used by `analysis_streamer` within this function for SSE).
*   **`session_context: Optional[Dict[str, Any]]`** (Default: `None`):
    *   An optional dictionary for session-specific context. It can include data like `'speaker_diarization'` or `'sentiment_trend_data'` which are used by specific services like `QuantitativeMetricsService` and `ConversationFlowService`.

### Return Value
*   **`AsyncGenerator[str, None]`**: An asynchronous generator that yields strings formatted as Server-Sent Events (SSE). Each event contains data for progress updates, analysis results, or errors.

### Key Operations
1.  **Initialization**:
    *   Instantiates `GeminiService` (to ensure DSPy LM is configured).
    *   Initializes instances of various analysis services: `ManipulationService`, `ArgumentService`, `SpeakerAttitudeService`, `EnhancedUnderstandingService`, `PsychologicalService`, `ModularAudioAnalysisService` (for text-inferred audio features), `QuantitativeMetricsService`, `ConversationFlowService`, and `SpeakerIntentService`.
    *   Defines a `text_analysis_map_template` mapping analysis type names to their respective service methods.
    *   Calculates `total_steps` for progress reporting.
2.  **Audio Quality Assessment**:
    *   Yields a progress update.
    *   Uses `pydub.AudioSegment` and `assess_audio_quality` (from `audio_service.py`) to get audio metrics.
    *   Yields the result as an SSE event.
3.  **Transcription (DSPy-based)**:
    *   Yields a progress update.
    *   Calls `dspy_transcribe_audio` (from `core_dspy_services.py`) to get the transcript.
    *   Yields the transcript as an SSE event.
4.  **Emotion Analysis (DSPy-based)**:
    *   Yields a progress update.
    *   Calls `dspy_analyze_emotions_audio` (from `core_dspy_services.py`) using the audio path and the generated transcript.
    *   Yields emotion details as an SSE event.
5.  **Iterative Text-Based Analyses**:
    *   Loops through the `text_analysis_map_template`.
    *   For each analysis type:
        *   Yields a progress update.
        *   Prepares arguments for the service method. Specific services like `QuantitativeMetricsService` and `ConversationFlowService` receive additional data (e.g., `speaker_diarization`, `dialogue_acts`) extracted from `session_context`. Most other services receive the `transcript_text` and the general `session_context`.
        *   Calls the respective service's `analyze` method (e.g., `manipulation_service.analyze(...)`).
        *   Yields the analysis result as an SSE event.
        *   Handles and yields errors for individual analysis steps.
6.  **Completion**: Yields a completion message.
7.  **Error Handling**: A main `try-except` block catches critical errors in the pipeline and yields an error SSE.
8.  **Cleanup**: A `finally` block attempts to delete the temporary audio file specified by `audio_path`.

### SSE Formatting
*   Uses a helper function `sse_format(data: Dict[str, Any]) -> str` to format dictionary data into the `data: json_string\n\n` SSE structure.

---
