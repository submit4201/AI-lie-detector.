# ManipulationService Documentation

This document provides an overview of the `ManipulationService` class, which is responsible for analyzing conversation transcripts for signs of psychological manipulation.

## Class: `ManipulationService`

### Overall Purpose
The `ManipulationService` analyzes textual transcripts to identify potential manipulative tactics. It utilizes the `DSPyManipulationAnalyzer` module, which leverages a Language Model (LM) configured via DSPy, to perform this analysis. The service handles the interaction with the DSPy module, including checks for LM configuration and a fallback mechanism if the primary analysis fails.

---

### `__init__(self, gemini_service: Optional[GeminiService] = None)`

#### Purpose
The constructor initializes the `ManipulationService`.

#### Parameters
*   **`gemini_service: Optional[GeminiService]`** (Default: `None`):
    *   An optional instance of `GeminiService`. If not provided, a new one is instantiated. This is crucial because the `GeminiService` constructor is responsible for configuring the DSPy Language Model (LM) settings (`dspy.settings.lm`) globally.

#### Initialization
*   **`self.gemini_service_instance`**: Stores the `GeminiService` instance. This action ensures that `GeminiService.__init__` is called, which should set up the DSPy LM.
*   **`self.dspy_analyzer = DSPyManipulationAnalyzer()`**: An instance of the `DSPyManipulationAnalyzer` module is created and stored. This module contains the logic for detecting manipulation.
*   **LM Configuration Check**:
    *   After attempting to ensure `GeminiService` has initialized, it checks if `dspy.settings.lm` is actually configured.
    *   Logs a warning if the LM is not found in `dspy.settings`, as this might lead to issues or reliance on fallbacks.
    *   Logs an informational message if the LM configuration is found.

---

### `async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> ManipulationAssessment`

#### Purpose
This asynchronous method performs manipulation analysis on the provided `transcript`. It uses the `DSPyManipulationAnalyzer` to obtain a structured assessment.

#### Input Parameters
*   **`transcript: str`**:
    *   The conversation transcript to be analyzed. If empty, a default `ManipulationAssessment` object is returned.
*   **`session_context: Optional[Dict[str, Any]]`** (Default: `None`):
    *   An optional dictionary providing additional context for the analysis (e.g., speaker profiles, history of interaction). This context is passed to the `DSPyManipulationAnalyzer`.

#### Return Value
*   **`ManipulationAssessment`**:
    *   A Pydantic model (`ManipulationAssessment`) containing the results of the manipulation analysis (e.g., `is_manipulative`, `manipulation_score`, `manipulation_techniques`).
    *   Returns a default `ManipulationAssessment` if the input `transcript` is empty.
    *   If errors occur or the DSPy LM is not properly configured, it returns results from the `_fallback_text_analysis` method.

#### Key Operations
1.  **Empty Transcript Check**: If `transcript` is empty, returns a default `ManipulationAssessment`.
2.  **LM Configuration Check**:
    *   Explicitly checks if `dspy.settings.lm` is configured before attempting the DSPy analysis.
    *   If not configured, it logs an error and attempts to initialize `GeminiService` again as a last-ditch effort to configure the LM.
    *   If the LM is still not configured, it logs a further error and resorts to `_fallback_text_analysis`.
3.  **DSPy Analysis**:
    *   If the LM is configured, it calls `self.dspy_analyzer.forward(transcript, session_context)`.
    *   This synchronous call to the DSPy module's `forward` method is executed in a separate thread using `await asyncio.to_thread` to maintain asynchronous behavior in the service method.
    *   Returns the `ManipulationAssessment` model populated by the `DSPyManipulationAnalyzer`.
4.  **Error Handling**:
    *   A `try-except` block captures any exceptions during the DSPy module call.
    *   If an exception occurs, it's logged (with stack trace), and the `_fallback_text_analysis` method is invoked.

---

### `_fallback_text_analysis(self, transcript: str) -> ManipulationAssessment`

#### Purpose
This private method provides a very basic, keyword-based fallback analysis for manipulation detection if the primary DSPy-based analysis cannot be performed.

#### Input Parameters
*   **`transcript: str`**: The transcript to be analyzed.

#### Return Value
*   **`ManipulationAssessment`**: A Pydantic model (`ManipulationAssessment`) populated with rudimentary analysis results.

#### Key Operations
1.  Logs that fallback analysis is being performed.
2.  Initializes default values: `is_manipulative = False`, `score = 0.0`, `confidence = 0.3` (low).
3.  Performs simple keyword spotting for potential manipulative tactics:
    *   Checks for "you always" or "you never" (potential overgeneralization).
    *   Checks for "if you really loved me" or "a good person would" (potential guilt-tripping/moralizing).
4.  If keywords are found, `is_manipulative` is set to `True`, techniques are noted, and the `score` is slightly increased.
5.  The `explanation` field is updated based on whether any tactics were detected.
6.  Returns a `ManipulationAssessment` model with these heuristically derived values. The `manipulation_score_analysis` provides context about the fallback.
