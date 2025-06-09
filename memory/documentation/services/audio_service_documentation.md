# Audio Service Documentation (`audio_service.py`)

This document provides an overview of the functions within `backend/services/audio_service.py`. This service module primarily handles audio file operations, quality assessment, and orchestrates audio analysis pipelines. It does not directly contain DSPy modules but calls other services (like `GeminiService` or potentially `core_dspy_services`) that might use them.

---

## Function: `assess_audio_quality(audio_segment: AudioSegment) -> Dict[str, Any]`

### Purpose
This function assesses basic quality metrics of an audio segment.

### Input Parameters
*   **`audio_segment: AudioSegment`**:
    *   An audio segment object (presumably from a library like `pydub`).

### Return Value
*   **`Dict[str, Any]`**:
    *   A dictionary containing quality metrics:
        *   `"duration"`: Length of the audio in seconds.
        *   `"sample_rate"`: Frame rate of the audio.
        *   `"channels"`: Number of audio channels.
        *   `"loudness"`: Average loudness in dBFS.
        *   `"quality_score"`: A simple score (0-100) based on duration, sample rate, loudness, and channels.

### Key Operations
1.  Calculates duration, sample rate, channels, and loudness from the `audio_segment`.
2.  Assigns a quality score by adding points if certain thresholds are met (e.g., duration >= 1s, sample_rate >= 16kHz, loudness > -30 dBFS, channels >= 1).

---

## Function: `convert_audio_to_wav(audio_path: str) -> str`

### Purpose
Converts an audio file to WAV format. This is often done to ensure consistency before further processing or analysis.

### Input Parameters
*   **`audio_path: str`**:
    *   The file system path to the input audio file.

### Return Value
*   **`str`**:
    *   The file system path to the converted WAV audio file. The new path is typically the original path with `_converted.wav` appended (or replacing the original extension).

### Key Operations
1.  Loads the audio file from `audio_path` using `AudioSegment.from_file()`.
2.  Exports the audio segment to a new file in WAV format.

---

## Function: `async def streaming_audio_analysis_pipeline(audio_path: str, session_id: str = None) -> Dict[str, Any]`

### Purpose
This asynchronous function defines an audio-first streaming analysis pipeline. It processes an audio file through several stages and can send updates via a streaming service if a `session_id` is provided. It primarily uses functionalities from `GeminiService` for core AI tasks.

### Input Parameters
*   **`audio_path: str`**:
    *   Path to the input audio file.
*   **`session_id: str`** (Default: `None`):
    *   An optional session ID used for streaming updates via `analysis_streamer` (from `backend.services.streaming_service`).

### Return Value
*   **`Dict[str, Any]`**:
    *   A dictionary containing the combined results of the analysis pipeline, including:
        *   `"transcript"`
        *   `"audio_quality"`
        *   `"emotion_analysis"`
        *   `"linguistic_analysis"`
        *   Other results from `query_gemini_with_audio`.
    *   Raises an exception if a critical error occurs in the pipeline.

### Key Operations
1.  **Import Dependencies**: Dynamically imports services like `analysis_streamer` (from `.streaming_service`), `transcribe_with_gemini`, `query_gemini_with_audio`, `analyze_emotions_with_gemini` (from `services.gemini_service`), and `linguistic_analysis_pipeline` (from `services.linguistic_service`).
2.  **Audio Conversion**: Converts the input audio to WAV format using `convert_audio_to_wav`.
3.  **Audio Quality Assessment**: Calls `assess_audio_quality` on the WAV file. Sends updates if `session_id` is present.
4.  **Transcription**: Transcribes the audio using `transcribe_with_gemini` (from `GeminiService`). Sends updates.
5.  **Comprehensive Gemini Analysis**: Performs a broader analysis using `query_gemini_with_audio` (from `GeminiService`), taking the audio path and transcript. Sends updates.
6.  **Emotion Analysis**: Analyzes emotions using `analyze_emotions_with_gemini` (from `GeminiService`). Sends updates.
7.  **Linguistic Analysis**: Performs linguistic analysis on the transcript using `linguistic_analysis_pipeline`. Sends updates.
8.  **Combine Results**: Aggregates all analysis results into a single dictionary.
9.  **Error Handling**: Catches exceptions, logs them, sends an error update via `analysis_streamer` if `session_id` is available, and then re-raises an exception.

---

## Function: `audio_analysis_pipeline(audio_path: str) -> Dict[str, Any]`

### Purpose
This is a synchronous wrapper for the `streaming_audio_analysis_pipeline`. It's designed to maintain backward compatibility for parts of the system that may not be asynchronous.

### Input Parameters
*   **`audio_path: str`**:
    *   Path to the input audio file.

### Return Value
*   **`Dict[str, Any]`**:
    *   The same dictionary of combined results as `streaming_audio_analysis_pipeline`.
    *   Raises an exception if an error occurs in the underlying asynchronous pipeline.

### Key Operations
1.  Uses `asyncio.run()` to execute the `streaming_audio_analysis_pipeline` synchronously, passing `None` for `session_id`.
2.  **Error Handling**: Catches exceptions from the asynchronous pipeline, logs them, and re-raises.

---

**Note on DSPy Usage:**
While this service module itself doesn't directly instantiate or use DSPy modules (like `DSPyTranscriptionModule` or `DSPyEmotionAnalysisModule`), it orchestrates analysis pipelines that rely on other services (primarily `GeminiService` and potentially `core_dspy_services` indirectly if `GeminiService` calls them) which are responsible for the actual DSPy interactions for tasks like transcription or specific types of analysis. The functions `transcribe_with_gemini`, `query_gemini_with_audio`, and `analyze_emotions_with_gemini` are expected to handle the direct LM interactions, possibly using DSPy modules configured within `GeminiService` or `core_dspy_services`.
