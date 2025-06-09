# AudioAnalysisService Documentation

This document provides an overview of the `AudioAnalysisService` class, which is responsible for inferring audio characteristics from the textual content of a transcript.

## Class: `AudioAnalysisService`

### Overall Purpose
The `AudioAnalysisService` aims to provide an analysis of perceived audio characteristics based **solely on the text of a transcript**. It utilizes the `DSPyAudioAnalysisAnalyzer` module, which interfaces with a Language Model (LM) configured via DSPy. The service manages interaction with this DSPy module, including handling LM configuration and providing a text-based fallback analysis if the primary DSPy analysis fails or is not configured.

**Important Note:** This service and its underlying DSPy module **do not process actual audio files**. All inferences about audio characteristics are derived from the textual content of the provided transcript.

---

### `__init__(self, gemini_service: Optional[GeminiService] = None)`

#### Purpose
The constructor initializes the `AudioAnalysisService`.

#### Parameters
*   **`gemini_service: Optional[GeminiService]`** (Default: `None`):
    *   An optional instance of `GeminiService`. If provided, it's used; otherwise, a new `GeminiService` instance is created. This is to ensure that the DSPy Language Model (LM) settings (`dspy.settings.lm`) are configured as part of `GeminiService`'s initialization.

#### Initialization
*   **`self.gemini_service_instance`**: Stores the provided or newly created `GeminiService` instance.
*   **`self.dspy_analyzer = DSPyAudioAnalysisAnalyzer()`**: An instance of the `DSPyAudioAnalysisAnalyzer` module is created. This module is specifically designed to infer audio characteristics from text.
*   **LM Configuration Check**:
    *   The constructor checks if `dspy.settings.lm` is configured.
    *   It logs a warning if the LM is not configured as expected, suggesting that analysis might fall back to simpler heuristics.
    *   It logs an info message if the LM appears to be configured.

---

### `async def analyze(self, text: str, audio_file_path: Optional[str] = None) -> AudioAnalysis`

#### Purpose
This asynchronous method performs an analysis to infer audio characteristics based on the provided `text` (transcript). The `audio_file_path` parameter is currently unused by this specific DSPy module but is kept for potential signature consistency with other services.

#### Input Parameters
*   **`text: str`**:
    *   The transcript text from which audio characteristics will be inferred. If empty, the method returns a default `AudioAnalysis` object.
*   **`audio_file_path: Optional[str]`** (Default: `None`):
    *   Currently not used by the `DSPyAudioAnalysisAnalyzer` as it operates solely on text. It's included for potential future use or API consistency.

#### Return Value
*   **`AudioAnalysis`**:
    *   A Pydantic model (`AudioAnalysis`) containing the inferred audio characteristics (e.g., `speech_clarity_score`, `background_noise_level`, `speech_rate_wpm`).
    *   If the input `text` is empty, a default `AudioAnalysis` model is returned.
    *   In case of errors or if the DSPy LM is not configured, it returns results from the `_fallback_text_analysis` method.

#### Key Operations
1.  **Empty Text Check**: If `text` is empty, returns a default `AudioAnalysis` model.
2.  **LM Configuration Check**:
    *   Verifies if `dspy.settings.lm` is configured.
    *   If not, logs an error, attempts to initialize `GeminiService` to trigger configuration, and if still not configured, falls back to `_fallback_text_analysis`.
3.  **DSPy Analysis**:
    *   If the LM is configured, it calls `self.dspy_analyzer.forward(text, session_context={})`. An empty dictionary is passed for `session_context` as it's not utilized by this particular text-based audio inference module.
    *   The call is executed in a separate thread using `await asyncio.to_thread`.
    *   Returns the `AudioAnalysis` model from the `dspy_analyzer`.
4.  **Error Handling**:
    *   A `try-except` block captures exceptions during the DSPy call.
    *   If an error occurs, it's logged, and the `_fallback_text_analysis` method is invoked.

---

### `_fallback_text_analysis(self, text: str, error_message: Optional[str] = None) -> AudioAnalysis`

#### Purpose
This private method provides a basic, heuristic-based fallback analysis of audio characteristics from text if the primary DSPy-based analysis fails.

#### Input Parameters
*   **`text: str`**: The transcript text.
*   **`error_message: Optional[str]`** (Default: `None`): An optional message detailing the error that led to the fallback.

#### Return Value
*   **`AudioAnalysis`**: A Pydantic model (`AudioAnalysis`) populated with results from simple text heuristics.

#### Key Operations
1.  Logs that fallback analysis is being performed.
2.  The `audio_quality_assessment` field is populated with an explanation including the `error_message`.
3.  If `text` is provided:
    *   Estimates `speech_rate_wpm` based on word count and an assumed average reading speed (150 WPM).
    *   Counts potential fillers (e.g., "um", "uh") and textual pauses (e.g., "...", "---") using regex and string counting.
    *   Assigns a rudimentary `speech_clarity_score` based on word count.
4.  Returns an `AudioAnalysis` model with these heuristically derived values. `background_noise_level` defaults to "Low" and `intonation_patterns` to "Analysis not available (fallback)."
