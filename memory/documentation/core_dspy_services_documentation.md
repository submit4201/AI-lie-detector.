# Core DSPy Services Documentation

This document provides an overview of the core asynchronous service functions that leverage DSPy modules for fundamental audio processing tasks like transcription and emotion analysis. These services are typically called by higher-level application logic that manages audio files and their associated data.

## `dspy_transcribe_audio`

### Purpose
The `dspy_transcribe_audio` asynchronous function is responsible for transcribing a given audio file into text. It utilizes the `DSPyTranscriptionModule` to interact with a configured multimodal Language Model (LM).

### Input Parameters
*   **`audio_path: str`**:
    *   The file system path to the audio file that needs to be transcribed.

### Return Value
*   **`str`**:
    *   The transcribed text of the audio file. In case of a failure during the transcription process (e.g., file not found, LM error), it may return an error message string or raise an exception.

### DSPy Module Used
*   **`DSPyTranscriptionModule`**: This module is instantiated and its `forward` method is called with the base64 encoded audio data and its MIME type.

### Important Notes
*   **LM Configuration**:
    *   The function includes checks to ensure that `dspy.settings.lm` is configured. If not, it attempts to initialize it by calling `GeminiService()`.
    *   A `RuntimeError` is raised if the LM cannot be configured, as transcription cannot proceed.
    *   Proper configuration of the LM to handle multimodal inputs (audio as base64) is critical for the module's success.
*   **Audio Processing**:
    *   The function reads the audio file, encodes it into a base64 string, and infers the MIME type from the file extension (defaulting to 'audio/wav').
*   **Asynchronous Execution**:
    *   The synchronous `forward` method of the `DSPyTranscriptionModule` is called using `await asyncio.to_thread` to prevent blocking other asynchronous operations.
*   **Error Handling**:
    *   Includes `try-except` blocks to catch `FileNotFoundError` and other general exceptions during transcription.
    *   Logs errors using the `logging` module.
    *   In case of an exception, it might return a string like "Transcription failed due to an error." or re-raise the exception depending on the specific error.

## `dspy_analyze_emotions_audio`

### Purpose
The `dspy_analyze_emotions_audio` asynchronous function analyzes the emotional content of a given audio file, using both the audio data and its transcript. It employs the `DSPyEmotionAnalysisModule` for this task.

### Input Parameters
*   **`audio_path: str`**:
    *   The file system path to the audio file.
*   **`transcript: str`**:
    *   The transcript of the audio, which provides textual context for the emotion analysis.

### Return Value
*   **`List[EmotionDetail]`**:
    *   A list of `EmotionDetail` Pydantic models, where each model instance contains details about an identified emotion (e.g., emotion label, score, optional timestamps).
    *   In case of errors (e.g., LM not configured, file not found, processing error), it returns a list containing a default `EmotionDetail` object indicating the error (e.g., `EmotionDetail(emotion="error_lm_not_configured", ...)`).

### DSPy Module Used
*   **`DSPyEmotionAnalysisModule`**: This module is instantiated, and its `forward` method is called with the base64 encoded audio, MIME type, and the transcript.

### Important Notes
*   **LM Configuration**:
    *   Similar to `dspy_transcribe_audio`, this function checks for LM configuration and attempts to initialize it via `GeminiService()` if needed.
    *   If LM configuration fails, it logs an error and returns a default error `EmotionDetail` list.
*   **Audio and Text Processing**:
    *   Reads and base64 encodes the audio file, and determines its MIME type.
    *   Utilizes both the audio data and the provided transcript as input to the `DSPyEmotionAnalysisModule`.
*   **Asynchronous Execution**:
    *   The synchronous `forward` method of `DSPyEmotionAnalysisModule` (which includes parsing the JSON output from the LM) is run in a separate thread using `await asyncio.to_thread`.
*   **Error Handling**:
    *   Catches `FileNotFoundError` and other general exceptions.
    *   Logs errors and returns a default `EmotionDetail` list indicating the type of error if an exception occurs during processing.
*   **Output Parsing**: The `DSPyEmotionAnalysisModule` itself is responsible for parsing the JSON string output from the LM into the `List[EmotionDetail]` structure.
