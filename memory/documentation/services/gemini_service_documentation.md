# GeminiService Documentation

This document provides an overview of the `GeminiService` class, which is central to interfacing with Google's Gemini models. Its key responsibilities include initializing the Gemini API for direct SDK calls and configuring the DSPy framework to use Gemini as its underlying language model.

## Class: `GeminiService`

### Overall Purpose
The `GeminiService` acts as a bridge to Google's Gemini Pro models. It performs two main functions:
1.  Configures and initializes the `google-generativeai` SDK for direct interactions with the Gemini API (e.g., for text generation not managed by DSPy).
2.  Configures DSPy's global settings (`dspy.settings`) to use a specified Gemini model (e.g., `gemini-1.5-flash-latest`) as the default Language Model (LM) for all DSPy operations. This is crucial for all DSPy modules (like `DSPyArgumentAnalyzer`, `DSPyTranscriptionModule`, etc.) to function correctly.

The service ensures that the necessary API keys are loaded and that both the direct SDK and DSPy's LM are set up, logging appropriate messages regarding the status of these configurations.

---

### `__init__(self)`

#### Purpose
The constructor initializes the `GeminiService`. Its primary roles are to load the Gemini API key, configure the `google.generativeai` SDK for direct use, and configure `dspy.settings.lm` for DSPy framework use.

#### API Key Loading
*   It attempts to load `GEMINI_API_KEY` from `backend.config`.
*   Logs an error if the API key is not found, warning that Gemini-based functionalities (including DSPy) will be limited.

#### `google.generativeai` SDK Configuration (for non-DSPy use)
*   If the API key is found, it calls `genai.configure(api_key=GEMINI_API_KEY)`.
*   It initializes `self.model = genai.GenerativeModel('gemini-1.5-flash-latest')` for direct SDK calls.
*   Logs success or failure of this SDK configuration. `self.model` will remain `None` if this fails.

#### DSPy Language Model Configuration
*   It checks if `dspy.settings.lm` has already been configured to avoid re-configuration.
*   If the `GEMINI_API_KEY` is available and DSPy's LM is not already configured:
    *   It creates a `dspy.LM` instance using `dspy.LM("gemini/gemini-1.5-flash-latest", api_key=GEMINI_API_KEY, max_tokens=1024)`.
    *   It then calls `dspy.settings.configure(lm=gemini_lm, temperature=0.7)` to set this as the global LM for DSPy with a default temperature.
    *   Logs the success or failure of this DSPy configuration.
*   If the API key is missing, it logs an error stating DSPy LM cannot be configured.
*   If DSPy LM was already configured, it logs this fact.

---

### `async def generate_text(self, prompt: str, is_json_output: bool = False) -> str | dict`

#### Purpose
This asynchronous method provides a way to generate text directly using the `google.generativeai` SDK (i.e., not through a DSPy module).

#### Input Parameters
*   **`prompt: str`**: The text prompt to send to the Gemini model.
*   **`is_json_output: bool`** (Default: `False`):
    *   If `True`, the method attempts to parse the model's response as JSON. It includes logic to strip markdown code block fences (e.g., ```json ... ```) before parsing.

#### Return Value
*   **`str | dict`**:
    *   If `is_json_output` is `True` and parsing is successful, returns a Python dictionary.
    *   Otherwise, returns the generated text as a string.
    *   If JSON parsing fails when `is_json_output` is `True`, it logs an error and returns the raw text response.
*   **Raises**:
    *   `ConnectionError`: If `self.model` (the `google.generativeai` SDK model) was not initialized (e.g., due to missing API key or configuration failure).
    *   Other exceptions from the `generate_content_async` call if API interaction fails.

#### Key Operations
1.  Checks if `self.model` is initialized. Raises `ConnectionError` if not.
2.  Logs the beginning of the text generation request.
3.  Calls `await self.model.generate_content_async(prompt)` to get the response from the Gemini API.
4.  Concatenates text from all parts of the response.
5.  If `is_json_output` is `True`:
    *   Attempts to clean potential markdown JSON fences.
    *   Tries to parse the cleaned string using `json.loads()`.
    *   Returns the dictionary if successful, or the raw text if parsing fails (with an error log).
6.  Returns the plain text response if `is_json_output` is `False`.
7.  Logs errors and re-raises exceptions if the API call or other operations fail.

---

### `async def query_gemini_for_raw_json(self, prompt: str) -> str | None`

#### Purpose
**DEPRECATED.** This asynchronous method was intended to query the Gemini model (using the direct `google.generativeai` SDK) and attempt to extract a JSON string from its response. Modern DSPy modules are expected to handle their own prompting and robust parsing of structured data.

#### Input Parameters
*   **`prompt: str`**: The text prompt.

#### Return Value
*   **`str | None`**:
    *   A string that is potentially a JSON object, or the raw response if JSON extraction fails.
    *   `None` if `self.model` is not initialized.

#### Key Operations
1.  Logs a deprecation warning.
2.  Checks `self.model` initialization.
3.  Calls `await self.model.generate_content_async(prompt)`.
4.  Attempts to extract a JSON string from the response text using regex (for ```json ... ``` blocks) or by finding the outermost curly braces (`{ ... }`).
5.  Tries to validate the extracted string with `json.loads()`. If it's valid JSON, the string is returned. Otherwise, the (potentially non-JSON) string that was extracted or the full raw response is returned after logging a warning.
6.  Logs errors and returns `None` if the API call fails.

---

**Note on Service Evolution:**
The `GeminiService` has been refactored to primarily focus on the initialization and configuration aspects for both direct Gemini SDK usage and DSPy framework integration. More complex, direct Gemini-based analysis pipelines (if any were previously part of this service) have been moved to other, more specialized services or are expected to be implemented via DSPy modules which this service helps enable.
