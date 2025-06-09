# DSPyQuantitativeMetricsAnalyzer Module Documentation

## Purpose

The `DSPyQuantitativeMetricsAnalyzer` module is designed to analyze a conversation transcript and associated session context to determine various quantitative communication metrics. These metrics include talk-to-listen ratio, average speaker turn duration, interruption counts, sentiment trends, word count, and vocabulary richness. The module can leverage speaker diarization and sentiment trend data if provided within the session context to enhance its analysis.

## QuantitativeMetricsSignature

The `DSPyQuantitativeMetricsAnalyzer` operates based on the `QuantitativeMetricsSignature`. This signature defines the input fields the module expects and the output fields it aims to produce, guiding the Language Model (LM) in its analysis.

### Input Fields

The signature specifies the following input fields:

*   **`transcript`**:
    *   **Type**: `str`
    *   **Description**: The full conversation transcript that will be analyzed for quantitative metrics.
*   **`session_context`**:
    *   **Type**: `str`
    *   **Description**: A JSON string providing context for the analysis. This field is crucial as it can contain `'speaker_diarization_json'` and `'sentiment_trend_json'` strings, which the module can use to inform its calculations for metrics like talk-to-listen ratio or sentiment trend. It can be an empty string if no additional context is available.

### Output Fields

The signature defines the following output fields, which the `DSPyQuantitativeMetricsAnalyzer` will populate:

*   **`talk_to_listen_ratio`**:
    *   **Type**: `float`
    *   **Description**: The ratio of talking time to listening time. The module will attempt to infer this, potentially using speaker diarization data from the `session_context`. Defaults to 0.0 if not inferable.
*   **`speaker_turn_duration_avg`**:
    *   **Type**: `float`
    *   **Description**: The average duration of speaker turns in seconds. This may also be inferred using speaker diarization data. Defaults to 0.0 if not inferable.
*   **`interruptions_count`**:
    *   **Type**: `int`
    *   **Description**: The number of interruptions detected in the conversation. Defaults to 0 if not inferable.
*   **`sentiment_trend`**:
    *   **Type**: `str` (JSON string of a list of dictionaries)
    *   **Description**: A JSON string representing a list of dictionaries, where each dictionary indicates sentiment at a point in time (e.g., `[{"time": 10.5, "sentiment": 0.7}]`). The module uses `sentiment_trend_json` from `session_context` if provided; otherwise, it may attempt to infer this or default to an empty list (`'[]'`).
*   **`word_count`**:
    *   **Type**: `int`
    *   **Description**: The total number of words in the transcript. The module has a fallback to calculate this directly from the input transcript if the LM doesn't provide it.
*   **`vocabulary_richness_score`**:
    *   **Type**: `float`
    *   **Description**: A score representing the richness of vocabulary used (e.g., Type-Token Ratio - TTR). Defaults to 0.0 if not inferable.

## Usage

The `DSPyQuantitativeMetricsAnalyzer` is intended for use within a service layer that processes conversation data. The typical workflow is:
1.  The service layer prepares the transcript. It also prepares a `session_context` dictionary which may include raw data like `speaker_diarization` (list) and `sentiment_trend_data_input` (list).
2.  An instance of `DSPyQuantitativeMetricsAnalyzer` is created.
3.  The service calls the `forward` method, passing the transcript, the `session_context` dictionary, and optionally the `speaker_diarization` and `sentiment_trend_data_input` lists.
4.  Inside the `forward` method, if `speaker_diarization` or `sentiment_trend_data_input` are provided, they are serialized into JSON strings and added to the `dspy_session_context` dictionary, which is then itself serialized into the `session_context_str` for the LM.
5.  The module then uses a `dspy.ChainOfThought(QuantitativeMetricsSignature)` predictor to interact with the LM.
6.  The method returns a `QuantitativeMetrics` Pydantic model. This model contains the calculated metrics, with fields populated after parsing and type conversion by the module. Robust error handling ensures that defaults are used if the LM output is missing or unparsable.

## Underlying DSPy Signature: `QuantitativeMetricsSignature`

The `QuantitativeMetricsSignature`, derived from `dspy.Signature`, defines the task for the LM.

*   **Purpose**: It specifies the inputs (`transcript`, `session_context`) and the quantitative metrics to be extracted or inferred as outputs. The docstring for the signature informs the LM that the `session_context` might contain JSON strings for speaker diarization and sentiment trends.
*   **Mechanism**: Inputs are `dspy.InputField` and outputs are `dspy.OutputField`. The `desc` attribute for each field guides the LM. For instance, `session_context`'s description mentions the potential presence of `speaker_diarization_json` and `sentiment_trend_json`. Output field descriptions clarify what each metric represents.
*   **Benefit**: This structure helps DSPy in prompting the LM effectively for extracting and inferring numerical and structured data. The module's logic for preparing the `session_context_str` and parsing the LM's response (including JSON strings for `sentiment_trend`) ensures that the data is correctly fed to the LM and the results are accurately mapped to the `QuantitativeMetrics` Pydantic model.
