# DSPyEmotionAnalysisModule Module Documentation

## Purpose

The `DSPyEmotionAnalysisModule` is a DSPy module designed to analyze the emotional content of a conversation by processing both the audio data (as a base64 string) and its corresponding transcript. It aims to identify primary emotions, assign confidence scores, and potentially identify timestamps for emotional segments. This module is intended for use with multimodal Language Models (LMs) capable of interpreting both audio and textual information.

## EmotionAnalysisSignature

The `DSPyEmotionAnalysisModule` operates based on the `EmotionAnalysisSignature`. This signature defines the inputs (audio and transcript) and the expected structured output (a JSON string representing a list of emotion details).

### Input Fields

The signature specifies the following input fields:

*   **`audio_base64_string`**:
    *   **Type**: `str`
    *   **Description**: A base64 encoded string of the audio data to be analyzed for emotional content.
*   **`audio_mime_type`**:
    *   **Type**: `str`
    *   **Description**: The MIME type of the audio data (e.g., 'audio/wav', 'audio/mp3'). This helps the LM correctly process the audio.
*   **`transcript`**:
    *   **Type**: `str`
    *   **Description**: The transcript of the audio, providing textual context for the emotion analysis.

### Output Fields

The signature defines the following output field:

*   **`emotion_analysis_json`**:
    *   **Type**: `str`
    *   **Description**: A JSON string representing a list of emotion objects. Each object is expected to have an "emotion" label (string) and a "score" (float). Optionally, "timestamp_start" and "timestamp_end" can be included for each emotion segment if inferable by the LM.
        *   Example: `'[{"emotion": "neutral", "score": 0.6, "timestamp_start": 0.5, "timestamp_end": 2.3}]'`

## Usage

The `DSPyEmotionAnalysisModule` is primarily utilized within services that perform multimodal analysis, such as the `dspy_analyze_emotions_audio` function in `backend/services/core_dspy_services.py`.

The typical workflow is:
1.  An audio file path and its transcript are provided to a service function (e.g., `dspy_analyze_emotions_audio`).
2.  The service function reads the audio file, encodes it into a base64 string, and determines its MIME type.
3.  An instance of `DSPyEmotionAnalysisModule` is created.
4.  The `forward` method of the module is called, passing the `audio_base64_string`, `audio_mime_type`, and the `transcript`.
5.  The module uses `dspy.Predict(EmotionAnalysisSignature)` (or potentially `dspy.ChainOfThought` if more complex reasoning is desired, though `Predict` is shown in the current implementation) to interact with the LM.
6.  The `forward` method receives the `emotion_analysis_json` string from the LM. It then parses this JSON string into a list of `EmotionDetail` Pydantic models. This parsing step includes error handling: if the JSON is invalid or the structure is not as expected, an empty list or a default error `EmotionDetail` object might be returned.
7.  The service function (`dspy_analyze_emotions_audio`) also handles LM configuration checks and file operations, similar to the transcription service. It typically runs the synchronous `forward` method in a separate thread using `asyncio.to_thread`.

**Note on LM Configuration:** The successful operation of this module is highly dependent on the `dspy.LM` (e.g., `GeminiService`) being correctly configured to handle multimodal inputs, specifically the combination of audio (via base64 string) and text transcript.

## Underlying DSPy Signature: `EmotionAnalysisSignature`

The `EmotionAnalysisSignature` class, inheriting from `dspy.Signature`, provides the blueprint for the emotion analysis task.

*   **Purpose**: It clearly defines for the LM the multimodal inputs it will receive (`audio_base64_string`, `audio_mime_type`, `transcript`) and the expected structured output format (`emotion_analysis_json`). The signature's docstring guides the LM on the categories of emotions to focus on and the desired JSON output structure.
*   **Mechanism**: It uses `dspy.InputField` for the audio data and transcript, and `dspy.OutputField` for the JSON string of emotion analysis. The descriptions (`desc`) for these fields, especially for `emotion_analysis_json`, are crucial for prompting the LM to return data in the specified format.
*   **Benefit**: This structured approach enables DSPy to manage the interaction with the multimodal LM for complex tasks like emotion analysis from audio and text. It standardizes the input presentation and output expectation, and the module's parsing logic then converts the LM's JSON output into a list of `EmotionDetail` Pydantic models, ready for further use in the application.
