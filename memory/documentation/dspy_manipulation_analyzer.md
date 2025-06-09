# DSPyManipulationAnalyzer Module Documentation

## Purpose

The `DSPyManipulationAnalyzer` module is designed to analyze a conversation transcript for signs of psychological manipulation. It aims to identify whether manipulative tactics are present, quantify the likelihood and confidence of manipulation, specify the techniques used, and provide an explanation for its assessment. The module is instructed to consider common manipulation techniques such as Gaslighting, Guilt-tripping, Love bombing, Appeal to pity, Intimidation, and Minimization.

## ManipulationSignature

The `DSPyManipulationAnalyzer` operates based on the `ManipulationSignature`, which defines the contract for the expected inputs and outputs of the analysis.

### Input Fields

The signature defines the following input fields:

*   **`transcript`**:
    *   **Type**: `str`
    *   **Description**: This field accepts the full conversation transcript that needs to be analyzed for signs of manipulation.
*   **`session_context`**:
    *   **Type**: `str`
    *   **Description**: This field takes an optional JSON string that provides additional context about the session. This could include details about previous interactions, speaker profiles, or other relevant background information that might help in assessing manipulation. It can be an empty string if no such context is available.

### Output Fields

The signature defines the following output fields, which the `DSPyManipulationAnalyzer` populates:

*   **`is_manipulative`**:
    *   **Type**: `bool`
    *   **Description**: An overall assessment indicating whether manipulation is considered present in the transcript.
*   **`manipulation_score`**:
    *   **Type**: `float`
    *   **Description**: A numerical score between 0.0 and 1.0 representing the likelihood that manipulation is occurring.
*   **`manipulation_techniques`**:
    *   **Type**: `list[str]`
    *   **Description**: A list of specific manipulation techniques identified in the transcript (e.g., "Gaslighting", "Guilt-tripping").
*   **`manipulation_confidence`**:
    *   **Type**: `float`
    *   **Description**: A score between 0.0 and 1.0 indicating the confidence level in the provided assessment.
*   **`manipulation_explanation`**:
    *   **Type**: `str`
    *   **Description**: A brief explanation for the assessment, which should cite examples from the transcript to support the findings.
*   **`manipulation_score_analysis`**:
    *   **Type**: `str`
    *   **Description**: A more detailed analysis that supports the `manipulation_score`, elaborating on why the score was given.

## Usage

The `DSPyManipulationAnalyzer` module is typically integrated into a broader analysis pipeline, likely within a service responsible for processing conversation data (e.g., a `ManipulationAnalysisService` or a more general `ConversationAnalysisService`). This service would:
1.  Obtain the conversation transcript and any relevant session context.
2.  Instantiate the `DSPyManipulationAnalyzer`.
3.  Invoke the `forward` method of the analyzer, passing the transcript and session context (the context dictionary is converted to a JSON string within the module).
4.  The `forward` method returns a `ManipulationAssessment` Pydantic model, which the service can then use for further actions, such as reporting or decision-making.

Internally, the `DSPyManipulationAnalyzer` utilizes `dspy.ChainOfThought(ManipulationSignature)`. This prompts the Language Model (LM) to engage in a step-by-step reasoning process before arriving at the structured output defined by `ManipulationSignature`. The module's `forward` method also includes logic to robustly parse the LM's output, converting string representations of booleans, floats, and lists of techniques into their correct Python types for the `ManipulationAssessment` model, including handling potential errors during this conversion.

## Underlying DSPy Signature: `ManipulationSignature`

The `ManipulationSignature` class, inheriting from `dspy.Signature`, is crucial for the module's operation.

*   **Purpose**: It explicitly defines the inputs (`transcript`, `session_context`) that the LM should consider and the structured outputs (e.g., `is_manipulative`, `manipulation_score`) it is expected to generate. The docstring of the signature also provides high-level instructions to the LM, such as the types of manipulation techniques to look for.
*   **Mechanism**: Each field within the signature is declared using `dspy.InputField` or `dspy.OutputField`. These declarations include a `desc` parameter that provides a natural language description for the LM, guiding it on how to interpret the input and what to produce for the output.
*   **Benefit**: This structured approach enables DSPy to manage interactions with the LM effectively. It improves the consistency and reliability of the manipulation analysis by clearly demarcating the scope and format of the desired information. The parsing and type conversion logic in the `DSPyManipulationAnalyzer` further ensures that the data conforms to the `ManipulationAssessment` Pydantic model.
