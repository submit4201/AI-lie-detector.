# DSPyPsychologicalAnalyzer Module Documentation

## Purpose

The `DSPyPsychologicalAnalyzer` module is tasked with inferring the psychological state of a speaker based on their conversation transcript. It focuses on identifying the speaker's emotional state, cognitive load, stress and confidence levels, potential cognitive biases, and provides an overall psychological summary. This analysis helps in understanding the underlying mental and emotional context of the speaker's communication.

## PsychologicalAnalysisSignature

The `DSPyPsychologicalAnalyzer` operates using the `PsychologicalAnalysisSignature`, which outlines the inputs required for the analysis and the outputs the module is expected to generate.

### Input Fields

The signature defines the following input fields:

*   **`transcript`**:
    *   **Type**: `str`
    *   **Description**: The complete conversation transcript that serves as the primary data for inferring the speaker's psychological state.
*   **`session_context`**:
    *   **Type**: `str`
    *   **Description**: An optional JSON string providing additional context about the session (e.g., known stressors, speaker history). This can be an empty string if no such context is available.

### Output Fields

The signature defines the following output fields, which the `DSPyPsychologicalAnalyzer` aims to populate:

*   **`emotional_state`**:
    *   **Type**: `str`
    *   **Description**: The overall emotional state inferred from the transcript (e.g., Neutral, Anxious, Calm, Happy, Sad).
*   **`cognitive_load`**:
    *   **Type**: `str`
    *   **Description**: An assessment of the speaker's inferred cognitive load (e.g., Low, Normal, High), accompanied by a brief justification.
*   **`stress_level`**:
    *   **Type**: `float`
    *   **Description**: A numerical score (0.0 to 1.0) representing the inferred level of stress experienced by the speaker.
*   **`confidence_level`**:
    *   **Type**: `float`
    *   **Description**: A numerical score (0.0 to 1.0) indicating the speaker's inferred level of confidence.
*   **`psychological_summary`**:
    *   **Type**: `str`
    *   **Description**: A summary that encapsulates the overall findings of the psychological state analysis.
*   **`potential_biases`**:
    *   **Type**: `str` (JSON string of a list of strings)
    *   **Description**: A JSON string representing a list of identified potential cognitive biases exhibited by the speaker (e.g., `'["Confirmation bias"] LIKELY because...'`). The list should be empty (`'[]'`) if no biases are detected or if parsing fails.

## Usage

The `DSPyPsychologicalAnalyzer` is typically employed as a part of a larger analytical system, likely orchestrated by a service layer (e.g., `PsychologicalProfilingService` or integrated within a comprehensive `InteractionAnalysisService`). The general workflow is:
1.  The service layer gathers the transcript and any relevant session context.
2.  An instance of `DSPyPsychologicalAnalyzer` is created.
3.  The service invokes the `forward` method of this instance, passing the transcript and the session context dictionary (the module internally converts the context to a JSON string).
4.  The `forward` method utilizes a `dspy.ChainOfThought(PsychologicalAnalysisSignature)` predictor. This prompts the Language Model (LM) to engage in a more detailed reasoning process to arrive at its conclusions.
5.  The method returns a `PsychologicalAnalysis` Pydantic model. This model is populated with the psychological insights. The module includes logic for parsing the LM's output, converting string representations of floats and lists (from JSON strings) into their appropriate Python types, and providing default values or "Analysis not available." messages in case of parsing issues or missing data from the LM.

## Underlying DSPy Signature: `PsychologicalAnalysisSignature`

The `PsychologicalAnalysisSignature`, a class inheriting from `dspy.Signature`, is central to the module's functionality.

*   **Purpose**: It explicitly defines the inputs (`transcript`, `session_context`) the LM will use and the structured outputs (e.g., `emotional_state`, `stress_level`, `potential_biases`) it is expected to produce for the psychological analysis. The signature's docstring provides guidance to the LM on the key aspects of psychological state to assess.
*   **Mechanism**: Fields are defined using `dspy.InputField` and `dspy.OutputField`. Each field definition contains a `desc` attribute, which provides a natural language description to the LM, clarifying what information is expected for that input or should be generated for that output. This is key for guiding the LM to provide specific assessments, numerical scores, and structured data like JSON strings for lists of biases.
*   **Benefit**: This structured approach enables DSPy to effectively prompt and manage the LM, thereby improving the consistency and reliability of the psychological analysis. The descriptive fields direct the LM's generation process, and the module's parsing logic ensures the final output is a well-structured `PsychologicalAnalysis` Pydantic model. The `_parse_list_str_field` helper method is used to robustly parse fields expected to be lists of strings from the LM's output.
