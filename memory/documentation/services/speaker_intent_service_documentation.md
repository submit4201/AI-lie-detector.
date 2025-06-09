# SpeakerIntentService Documentation

This document provides an overview of the `SpeakerIntentService` class, which is responsible for analyzing conversation transcripts to infer the intent behind a speaker's utterances.

## Class: `SpeakerIntentService`

### Overall Purpose
The `SpeakerIntentService` analyzes textual transcripts to determine the primary and secondary intents of a speaker. It leverages the `DSPySpeakerIntentAnalyzer` module, which interfaces with a Language Model (LM) configured via DSPy, to perform this analysis. The service manages the interaction with the DSPy module, including checks for LM configuration and basic error handling.

---

### `__init__(self, gemini_service: Optional[GeminiService] = None)`

#### Purpose
The constructor initializes the `SpeakerIntentService`.

#### Parameters
*   **`gemini_service: Optional[GeminiService]`** (Default: `None`):
    *   An optional instance of `GeminiService`. If not provided, a new `GeminiService` instance is created. This is primarily to ensure that the `GeminiService` (which handles DSPy LM configuration) is initialized.

#### Initialization
*   **`self.gemini_service_instance`**: Stores the `GeminiService` instance. This ensures its `__init__` method, which should configure `dspy.settings.lm`, is called.
*   **`self.dspy_analyzer = DSPySpeakerIntentAnalyzer()`**: An instance of the `DSPySpeakerIntentAnalyzer` module is created. This module contains the specific prompts and logic for inferring speaker intent.
*   **LM Configuration Check (Initial)**:
    *   The constructor checks if `dspy.settings.lm` is configured after `GeminiService` is expected to have run.
    *   Logs a warning if the LM configuration is not detected at this stage, as subsequent calls might fail if the LM isn't configured elsewhere.

---

### `async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> SpeakerIntent`

#### Purpose
This asynchronous method performs speaker intent analysis on the provided `transcript` and optional `session_context`. It uses the `DSPySpeakerIntentAnalyzer` to generate a structured `SpeakerIntent` report.

#### Input Parameters
*   **`transcript: str`**:
    *   The conversation transcript to be analyzed. If empty, a default `SpeakerIntent` object is returned.
*   **`session_context: Optional[Dict[str, Any]]`** (Default: `None`):
    *   An optional dictionary providing additional context for the analysis (e.g., speaker roles, ongoing situation). This context is passed to the `DSPySpeakerIntentAnalyzer`. If `None`, an empty dictionary is passed.

#### Return Value
*   **`SpeakerIntent`**:
    *   A Pydantic model (`SpeakerIntent`) containing the results of the speaker intent analysis (e.g., `inferred_intent`, `confidence_score`, `key_phrases_supporting_intent`, `secondary_intents`).
    *   Returns a default `SpeakerIntent` model if the input `transcript` is empty.
    *   If the DSPy LM is not configured and cannot be configured, returns a default `SpeakerIntent` with an error message in `overall_assessment`.
    *   If an error occurs during the DSPy module execution, returns a default `SpeakerIntent` with the error message in `overall_assessment`.

#### Key Operations
1.  **Empty Transcript Check**: If `transcript` is empty, returns a default `SpeakerIntent` model.
2.  **LM Configuration Check (Pre-Analysis)**:
    *   Verifies if `dspy.settings.lm` is configured globally.
    *   If not, it logs an error and makes a final attempt to configure the LM by instantiating `GeminiService` again.
    *   If the LM is still not configured, it logs a critical error and returns a `SpeakerIntent` object with an error message in the `overall_assessment` field.
3.  **Session Context Handling**: If `session_context` is `None`, it's initialized to an empty dictionary before being passed to the analyzer.
4.  **DSPy Analysis**:
    *   If the LM is configured, it calls `self.dspy_analyzer.forward(transcript, session_context)`.
    *   This synchronous call is executed in a separate thread using `await asyncio.to_thread` to ensure the `analyze` method remains non-blocking.
    *   Returns the `SpeakerIntent` model populated by the `DSPySpeakerIntentAnalyzer`.
5.  **Error Handling**:
    *   A `try-except` block captures any exceptions during the DSPy module interaction.
    *   If an exception occurs, it's logged (including stack trace), and a `SpeakerIntent` object is returned with the error message included in its `overall_assessment` field.

---

**Note on Fallback:** Unlike some other services, this service does not have a dedicated `_fallback_analysis` method that attempts to compute heuristic values for all fields. In case of critical errors (like LM misconfiguration or DSPy module exceptions), it returns a default `SpeakerIntent` model where the `overall_assessment` field is populated with an error message. Other fields will take their default Pydantic model values.
