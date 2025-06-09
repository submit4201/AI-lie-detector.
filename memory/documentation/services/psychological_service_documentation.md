# PsychologicalService Documentation

This document provides an overview of the `PsychologicalService` class, which is responsible for analyzing conversation transcripts to infer the psychological state of a speaker.

## Class: `PsychologicalService`

### Overall Purpose
The `PsychologicalService` analyzes textual transcripts to assess a speaker's psychological state, focusing on aspects like emotional state, cognitive load, stress, confidence, and potential biases. It employs the `DSPyPsychologicalAnalyzer` module, which uses a Language Model (LM) configured via DSPy for this analysis. The service manages interactions with this DSPy module, including LM configuration checks and a fallback mechanism if the primary analysis is unavailable.

---

### `__init__(self, gemini_service: Optional[GeminiService] = None)`

#### Purpose
The constructor initializes the `PsychologicalService`.

#### Parameters
*   **`gemini_service: Optional[GeminiService]`** (Default: `None`):
    *   An optional instance of `GeminiService`. If not provided, a new one is instantiated. This is important as the `GeminiService` constructor is responsible for setting up the global DSPy Language Model (LM) configuration (`dspy.settings.lm`).

#### Initialization
*   **`self.gemini_service_instance`**: Stores the `GeminiService` instance, ensuring its initialization routine (which configures DSPy) is executed.
*   **`self.dspy_analyzer = DSPyPsychologicalAnalyzer()`**: An instance of the `DSPyPsychologicalAnalyzer` module is created. This module contains the specific prompts and logic for psychological state analysis.
*   **LM Configuration Check**:
    *   It checks if `dspy.settings.lm` is configured after `GeminiService` is expected to have run its initialization.
    *   Logs a warning if the LM configuration is not detected, indicating that the service might have to rely on its fallback analysis.
    *   Logs an informational message if the LM configuration is found.

---

### `async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> PsychologicalAnalysis`

#### Purpose
This asynchronous method performs a psychological state analysis on the provided `transcript` and optional `session_context`. It utilizes the `DSPyPsychologicalAnalyzer` to generate a structured `PsychologicalAnalysis` report.

#### Input Parameters
*   **`transcript: str`**:
    *   The conversation transcript to be analyzed. If empty, a default `PsychologicalAnalysis` object is returned.
*   **`session_context: Optional[Dict[str, Any]]`** (Default: `None`):
    *   An optional dictionary providing additional context for the analysis (e.g., known situational factors, speaker background). This context is passed to the `DSPyPsychologicalAnalyzer`.

#### Return Value
*   **`PsychologicalAnalysis`**:
    *   A Pydantic model (`PsychologicalAnalysis`) containing the results of the psychological analysis (e.g., `emotional_state`, `cognitive_load`, `stress_level`, `confidence_level`, `potential_biases`).
    *   Returns a default `PsychologicalAnalysis` model if the input `transcript` is empty.
    *   If errors occur (e.g., LM not configured, DSPy module error), it returns results from the `_fallback_analysis` method.

#### Key Operations
1.  **Empty Transcript Check**: If `transcript` is empty, returns a default `PsychologicalAnalysis` model.
2.  **LM Configuration Check**:
    *   Before attempting DSPy analysis, it verifies if `dspy.settings.lm` is globally configured.
    *   If not, it logs an error and makes a final attempt to configure the LM by instantiating `GeminiService`.
    *   If the LM remains unconfigured, it logs another error and invokes `_fallback_analysis`.
3.  **DSPy Analysis**:
    *   If the LM is configured, it calls `self.dspy_analyzer.forward(transcript, session_context)`.
    *   This call, being synchronous, is executed in a separate thread using `await asyncio.to_thread` to ensure the `analyze` method remains non-blocking.
    *   Returns the `PsychologicalAnalysis` model populated by the `DSPyPsychologicalAnalyzer`.
4.  **Error Handling**:
    *   A `try-except` block is used to catch any exceptions during the DSPy module interaction.
    *   If an exception occurs, it's logged (including stack trace), and the `_fallback_analysis` method is called with the error details.

---

### `_fallback_analysis(self, transcript: str, error_message: Optional[str] = None) -> PsychologicalAnalysis`

#### Purpose
This private method provides a very basic fallback if the primary DSPy-based psychological analysis cannot be performed.

#### Input Parameters
*   **`transcript: str`**: The transcript (currently used only for logging a snippet).
*   **`error_message: Optional[str]`** (Default: `None`): An optional message detailing the error that triggered the fallback.

#### Return Value
*   **`PsychologicalAnalysis`**: A Pydantic model (`PsychologicalAnalysis`) where the `psychological_summary` field explains that fallback analysis was performed and includes the error message. Other fields will use their default values as defined in the Pydantic model.

#### Key Operations
1.  Logs that fallback analysis is being performed, including a snippet of the transcript.
2.  Constructs an `explanation` string indicating fallback, incorporating the `error_message` if provided.
3.  Returns a `PsychologicalAnalysis` model with the `psychological_summary` set to this explanation. Other analytical fields (like `emotional_state`, `stress_level`, etc.) will take their default values from the Pydantic model definition, implying no specific fallback calculation for these metrics is implemented in this method.
