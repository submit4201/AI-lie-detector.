# DSPySpeakerAttitudeAnalyzer Module Documentation

## Purpose

The `DSPySpeakerAttitudeAnalyzer` module is designed to analyze a given conversation transcript to assess the speaker's attitude. It focuses on identifying the dominant attitude, evaluating the level of respect shown, and quantifying the formality and politeness of the speaker's language. This analysis provides insights into the interpersonal dynamics of the conversation.

## SpeakerAttitudeSignature

The `DSPySpeakerAttitudeAnalyzer` operates based on the `SpeakerAttitudeSignature`. This signature defines the input fields the module expects and the output fields it aims to produce, guiding the Language Model (LM) in its analysis.

### Input Fields

The signature specifies the following input fields:

*   **`transcript`**:
    *   **Type**: `str`
    *   **Description**: The full conversation transcript that will be analyzed for speaker attitude.
*   **`session_context`**:
    *   **Type**: `str`
    *   **Description**: An optional JSON string that can provide additional context about the session, such as speaker identities or prior interactions. This can be an empty string if no external context is available or relevant.

### Output Fields

The signature defines the following output fields, which the `DSPySpeakerAttitudeAnalyzer` will populate:

*   **`dominant_attitude`**:
    *   **Type**: `str`
    *   **Description**: The primary attitude conveyed by the speaker (e.g., Neutral, Positive, Negative, Mixed).
*   **`attitude_scores`**:
    *   **Type**: `str` (JSON string of a dictionary)
    *   **Description**: A JSON string representing a dictionary where keys are specific attitudes (e.g., "respectful", "friendly") and values are their corresponding scores, typically on a 0.0 to 1.0 scale. Example: `'{"respectful": 0.8, "friendly": 0.7}'`.
*   **`respect_level`**:
    *   **Type**: `str`
    *   **Description**: A qualitative assessment of the speaker's level of respect (e.g., High, Medium, Low, Disrespectful).
*   **`respect_level_score`**:
    *   **Type**: `float`
    *   **Description**: A numerical score (0.0 to 1.0) quantifying the assessed level of respect.
*   **`respect_level_score_analysis`**:
    *   **Type**: `str`
    *   **Description**: An analysis or justification for the assigned `respect_level_score`.
*   **`formality_score`**:
    *   **Type**: `float`
    *   **Description**: A numerical score indicating the formality of the speaker's language, typically ranging from 0.0 (very informal) to 1.0 (very formal).
*   **`formality_assessment`**:
    *   **Type**: `str`
    *   **Description**: A qualitative description or assessment of the speaker's formality level.
*   **`politeness_score`**:
    *   **Type**: `float`
    *   **Description**: A numerical score (0.0 to 1.0) quantifying the politeness exhibited by the speaker.
*   **`politeness_assessment`**:
    *   **Type**: `str`
    *   **Description**: A qualitative description or assessment of the speaker's politeness.

## Usage

The `DSPySpeakerAttitudeAnalyzer` is intended to be used as a component within a larger system, often managed by a service layer (e.g., `SpeakerAttitudeService` or as part of a broader `ConversationAnalysisService`). The typical operational flow is:
1.  The service layer obtains the transcript and any relevant session context.
2.  An instance of `DSPySpeakerAttitudeAnalyzer` is created.
3.  The service calls the `forward` method of this instance, providing the transcript and the session context dictionary. The module internally converts the context dictionary to a JSON string.
4.  The `forward` method employs a `dspy.ChainOfThought(SpeakerAttitudeSignature)` predictor. This encourages the LM to perform a more reasoned analysis before generating the output.
5.  The method returns a `SpeakerAttitude` Pydantic model. This model contains the analyzed attitude attributes, with data types (floats, parsed dictionaries from JSON strings) appropriately converted and validated by the module's parsing logic. Default values or "Analysis not available." are used as fallbacks if parsing errors occur or if the LM does not provide a value.

## Underlying DSPy Signature: `SpeakerAttitudeSignature`

The `SpeakerAttitudeSignature`, a class derived from `dspy.Signature`, is fundamental to the module's operation.

*   **Purpose**: It clearly defines the contract for the LM, specifying the input information (`transcript`, `session_context`) and the structured output fields related to speaker attitude (e.g., `dominant_attitude`, `respect_level_score`, `formality_score`). The signature's docstring gives the LM general instructions on what aspects of attitude to focus on.
*   **Mechanism**: Inputs are defined with `dspy.InputField` and outputs with `dspy.OutputField`. Each field definition includes a `desc` attribute, providing a natural language prompt to the LM about the specific information expected for that field. This is crucial for guiding the LM to produce specific scores and assessments, including JSON formatted strings for structured data like `attitude_scores`.
*   **Benefit**: This structured approach allows DSPy to reliably prompt and manage the LM's behavior, enhancing the consistency of the speaker attitude analysis. The descriptive fields guide the LM, and the module's parsing logic ensures the output is transformed into a usable `SpeakerAttitude` Pydantic model.
