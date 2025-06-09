# QuantitativeMetricsService Documentation

This document provides an overview of the `QuantitativeMetricsService` class, which is responsible for calculating various quantitative communication metrics from transcripts, potentially enhanced by speaker diarization and sentiment trend data.

## Class: `QuantitativeMetricsService`

### Overall Purpose
The `QuantitativeMetricsService` computes numerical metrics related to communication patterns, such as talk-to-listen ratio, speaker turn duration, interruption counts, word count, vocabulary richness, and sentiment trends. It utilizes the `DSPyQuantitativeMetricsAnalyzer` module, which interfaces with a Language Model (LM) configured via DSPy, to perform the core analysis. The service manages this interaction, including LM configuration checks and a fallback mechanism for analysis.

---

### `__init__(self, gemini_service: Optional[GeminiService] = None)`

#### Purpose
The constructor initializes the `QuantitativeMetricsService`.

#### Parameters
*   **`gemini_service: Optional[GeminiService]`** (Default: `None`):
    *   An optional instance of `GeminiService`. If not provided, a new one is instantiated. This ensures that the `GeminiService` (and its DSPy LM configuration logic) is initialized.

#### Initialization
*   **`self.gemini_service_instance`**: Stores the `GeminiService` instance.
*   **`self.dspy_analyzer = DSPyQuantitativeMetricsAnalyzer()`**: An instance of the `DSPyQuantitativeMetricsAnalyzer` module is created. This module is tailored for extracting quantitative metrics.
*   **LM Configuration Check**:
    *   Verifies if `dspy.settings.lm` is configured after `GeminiService` is expected to have initialized.
    *   Logs a warning if the LM configuration is not detected, indicating potential reliance on fallback methods.
    *   Logs an info message if the LM is found to be configured.

---

### `async def analyze(self, text: str, speaker_diarization: Optional[List[Dict[str, Any]]] = None, sentiment_trend_data_input: Optional[List[Dict[str, float]]] = None) -> QuantitativeMetrics`

#### Purpose
This asynchronous method analyzes the provided transcript (`text`) and optional `speaker_diarization` and `sentiment_trend_data_input` to calculate quantitative communication metrics.

#### Input Parameters
*   **`text: str`**:
    *   The conversation transcript. If empty, a default `QuantitativeMetrics` object with `word_count=0` is returned.
*   **`speaker_diarization: Optional[List[Dict[str, Any]]]`** (Default: `None`):
    *   Optional list of speaker diarization segments (dictionaries with keys like `speaker_label`, `start_time`, `end_time`, `duration`). This data is passed to the `DSPyQuantitativeMetricsAnalyzer` to potentially inform metrics like talk ratio and turn duration.
*   **`sentiment_trend_data_input: Optional[List[Dict[str, float]]]`** (Default: `None`):
    *   Optional list of sentiment data points (dictionaries, typically with `time` and `sentiment` keys). This is passed to the `DSPyQuantitativeMetricsAnalyzer` to inform the `sentiment_trend` output.

#### Return Value
*   **`QuantitativeMetrics`**:
    *   A Pydantic model (`QuantitativeMetrics`) containing the calculated metrics (e.g., `talk_to_listen_ratio`, `word_count`, `vocabulary_richness_score`).
    *   Returns a default `QuantitativeMetrics(word_count=0)` if the input `text` is empty.
    *   If errors occur or the DSPy LM is not configured, it returns results from the `_fallback_text_analysis` method.

#### Key Operations
1.  **Empty Text Check**: If `text` is empty, returns `QuantitativeMetrics(word_count=0)`.
2.  **LM Configuration Check**:
    *   Verifies if `dspy.settings.lm` is configured globally.
    *   If not, logs an error, attempts to re-initialize `GeminiService`, and if still unconfigured, invokes `_fallback_text_analysis`.
3.  **DSPy Analysis**:
    *   If the LM is configured, it calls `self.dspy_analyzer.forward()`.
    *   The `transcript` argument for `forward` is set to `text`.
    *   `speaker_diarization` and `sentiment_trend_data_input` are passed directly to the `forward` method of `DSPyQuantitativeMetricsAnalyzer`. The analyzer module itself handles the creation of the `session_context` string for the LM, including serializing these structured inputs if necessary. An empty dictionary `{}` is passed as the base `session_context` to the `forward` method as these specific parameters are handled explicitly by it.
    *   The call is executed in a separate thread using `await asyncio.to_thread`.
    *   Returns the `QuantitativeMetrics` model populated by the analyzer.
4.  **Error Handling**:
    *   A `try-except` block captures exceptions during the DSPy call.
    *   Errors are logged, and `_fallback_text_analysis` is called with the error details.

---

### `_fallback_text_analysis(self, text: str, speaker_diarization: Optional[List[Dict[str, Any]]] = None, sentiment_trend_data_input: Optional[List[Dict[str, float]]] = None, error_message: Optional[str] = None) -> QuantitativeMetrics`

#### Purpose
This private method provides a basic, heuristic-based fallback for calculating quantitative metrics if the primary DSPy-based analysis fails.

#### Input Parameters
*   **`text: str`**: The transcript.
*   **`speaker_diarization: Optional[List[Dict[str, Any]]]`**: Optional speaker diarization data.
*   **`sentiment_trend_data_input: Optional[List[Dict[str, float]]]`**: Optional sentiment trend data.
*   **`error_message: Optional[str]`**: An optional message detailing the error.

#### Return Value
*   **`QuantitativeMetrics`**: A Pydantic model (`QuantitativeMetrics`) populated with heuristically derived metrics.

#### Key Operations
1.  Logs that fallback analysis is being performed and includes any `error_message`.
2.  **Word Count**: Calculated by splitting the `text`.
3.  **Vocabulary Richness**: Calculated as the ratio of unique alphabetic words to total alphabetic words.
4.  **Sentiment Trend**: Uses `sentiment_trend_data_input` if provided. Otherwise, simulates a neutral trend based on estimated text duration (assuming 150 WPM).
5.  **Speaker Diarization Metrics (Rudimentary)**:
    *   If `speaker_diarization` is provided:
        *   `avg_turn_duration`: Calculated from the sum of turn durations and number of turns.
        *   `interruptions_count`: Naively estimated based on number of turns and average turn duration.
        *   `talk_to_listen_ratio`: Simplified to 0.5 if multiple unique speakers, 1.0 if one, 0.0 otherwise.
6.  Returns a `QuantitativeMetrics` model with these calculated/estimated values.
