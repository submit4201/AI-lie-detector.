# SpeakerAttitudeService Documentation

This document provides an overview of the `SpeakerAttitudeService` class, which is responsible for analyzing conversation transcripts to assess the speaker's attitude, including aspects like dominant attitude, respect level, formality, and politeness.

## Class: `SpeakerAttitudeService`

### Overall Purpose
The `SpeakerAttitudeService` analyzes textual transcripts to evaluate a speaker's attitude. It leverages the `DSPySpeakerAttitudeAnalyzer` module, which interfaces with a Language Model (LM) configured via DSPy, to perform this nuanced analysis. The service manages the interaction with the DSPy module, including crucial checks for LM configuration and a fallback mechanism if the primary DSPy-based analysis cannot be performed.

---

### `__init__(self, gemini_service: Optional[GeminiService] = None)`

#### Purpose
The constructor initializes the `SpeakerAttitudeService`.

#### Parameters
*   **`gemini_service: Optional[GeminiService]`** (Default: `None`):
    *   An optional instance of `GeminiService`. If not provided, a new `GeminiService` instance is created. This is important because the `GeminiService` is responsible for the global configuration of the DSPy Language Model (LM) settings (`dspy.settings.lm`).

#### Initialization
*   **`self.gemini_service_instance`**: Stores the `GeminiService` instance, ensuring that its initialization logic (which includes DSPy LM setup) is executed.
*   **`self.dspy_analyzer = DSPySpeakerAttitudeAnalyzer()`**: An instance of the `DSPySpeakerAttitudeAnalyzer` module is created. This module contains the specific prompts and logic for analyzing speaker attitude.
*   **LM Configuration Check**:
    *   After `GeminiService` is expected to have initialized, this constructor checks if `dspy.settings.lm` has been successfully configured.
    *   It logs a warning if the LM configuration is not detected, indicating that the service might have to rely on its fallback analysis method.
    *   It logs an informational message if the LM configuration is found, confirming readiness for DSPy-based analysis.

---

### `async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> SpeakerAttitude`

#### Purpose
This asynchronous method performs speaker attitude analysis on the provided `transcript` and optional `session_context`. It utilizes the `DSPySpeakerAttitudeAnalyzer` to generate a structured `SpeakerAttitude` report.

#### Input Parameters
*   **`transcript: str`**:
    *   The conversation transcript to be analyzed. If the transcript is empty, a default `SpeakerAttitude` object is returned.
*   **`session_context: Optional[Dict[str, Any]]`** (Default: `None`):
    *   An optional dictionary that can provide additional context for the analysis (e.g., speaker roles, relationship dynamics, topic of conversation). This context is passed to the `DSPySpeakerAttitudeAnalyzer`.

#### Return Value
*   **`SpeakerAttitude`**:
    *   A Pydantic model (`SpeakerAttitude`) containing the results of the speaker attitude analysis (e.g., `dominant_attitude`, `respect_level_score`, `formality_score`, `politeness_score`).
    *   Returns a default `SpeakerAttitude` model if the input `transcript` is empty.
    *   If errors occur (such as the LM not being configured or an issue within the DSPy module), it returns results from the `_fallback_analysis` method.

#### Key Operations
1.  **Empty Transcript Check**: If the `transcript` is empty, a default `SpeakerAttitude` model is returned immediately.
2.  **LM Configuration Check**:
    *   Before attempting the DSPy analysis, it verifies that `dspy.settings.lm` is configured globally.
    *   If not configured, it logs an error and makes a final attempt to configure the LM by instantiating `GeminiService`.
    *   If the LM remains unconfigured after this attempt, it logs a further error and invokes the `_fallback_analysis` method.
3.  **DSPy Analysis**:
    *   If the LM is configured, it calls `self.dspy_analyzer.forward(transcript, session_context)`.
    *   This call to the synchronous `forward` method of the DSPy module is executed in a separate thread using `await asyncio.to_thread` to ensure the `analyze` method itself remains non-blocking.
    *   Returns the `SpeakerAttitude` model populated by the `DSPySpeakerAttitudeAnalyzer`.
4.  **Error Handling**:
    *   A `try-except` block is used to catch any exceptions that might occur during the interaction with the DSPy module.
    *   If an exception occurs, it is logged (including the stack trace), and the `_fallback_analysis` method is called, passing the error message for context.

---

### `_fallback_analysis(self, transcript: str, error_message: Optional[str] = None) -> SpeakerAttitude`

#### Purpose
This private method provides a basic fallback mechanism if the primary DSPy-based speaker attitude analysis cannot be performed. It returns a `SpeakerAttitude` object with neutral/default values and an explanation.

#### Input Parameters
*   **`transcript: str`**: The transcript (currently used only for logging a snippet).
*   **`error_message: Optional[str]`** (Default: `None`): An optional message detailing the error that necessitated the fallback.

#### Return Value
*   **`SpeakerAttitude`**: A Pydantic model (`SpeakerAttitude`) populated with default, generally neutral attitude metrics and an explanation indicating that fallback analysis was performed.

#### Key Operations
1.  Logs that fallback analysis is being performed, including a snippet of the transcript.
2.  Constructs an `explanation` string, which will be used in the `respect_level_score_analysis` field, indicating that fallback analysis occurred and incorporating the `error_message` if provided.
3.  Returns a `SpeakerAttitude` model with pre-defined neutral/default values:
    *   `dominant_attitude`: "Neutral"
    *   `attitude_scores`: `{"neutral": 1.0}`
    *   `respect_level`: "Medium"
    *   `respect_level_score`: 0.5
    *   `respect_level_score_analysis`: The generated explanation string.
    *   `formality_score`: 0.5
    *   `formality_assessment`: "Mixed"
    *   `politeness_score`: 0.5
    *   `politeness_assessment`: "Neutral"
