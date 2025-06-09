import logging
import google.generativeai as genai # For non-DSPy use
from backend.config import GEMINI_API_KEY
import json
import dspy # Added for DSPy configuration
import re # For regex in deprecated query_gemini_for_raw_json

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.model = None # For non-DSPy use cases
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not found in environment variables. Gemini-based functionalities (including DSPy) will be limited.")
        else:
            try:
                # Configure for non-DSPy use (google.generativeai SDK)
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                logger.info("GeminiService initialized with google.generativeai model gemini-1.5-flash-latest.")
            except Exception as e:
                logger.error(f"Google GenAI SDK configuration failed: {e}", exc_info=True)
                # self.model remains None

        # DSPy Language Model Configuration
        # Check if dspy.settings.lm is already configured
        lm_configured = False
        try:
            if dspy.settings.lm: # This will throw AttributeError if lm is not set
                lm_configured = True
        except AttributeError:
            pass # lm is not configured


        if GEMINI_API_KEY and not lm_configured:
            try:
                gemini_lm = dspy.LM(
                    "gemini/gemini-1.5-flash-latest",
                    api_key=GEMINI_API_KEY,
                    max_tokens=1024, # Sensible default
                )
                # Configure DSPy settings, including temperature if desired globally
                dspy.settings.configure(lm=gemini_lm, temperature=0.7)
                logger.info("DSPy LM configured globally in GeminiService with gemini/gemini-1.5-flash-latest.")
            except Exception as e:
                logger.error(f"DSPy LM configuration failed in GeminiService: {e}", exc_info=True)
        elif not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not found. DSPy LM cannot be configured.")
        elif lm_configured:
            logger.info("DSPy LM already configured.")
        else:
             logger.warning("DSPy LM not configured for an unknown reason despite API key possibly existing.")


    async def generate_text(self, prompt: str, is_json_output: bool = False) -> str | dict:
        # This method remains for non-DSPy use cases using the google.generativeai SDK
        if not self.model:
            logger.error("GeminiService google.generativeai model not initialized. Cannot generate text.")
            raise ConnectionError("GeminiService google.generativeai model not available.")

        logger.info(f"Generating text (non-DSPy) with prompt starting with: {prompt[:100]}...")
        try:
            response = await self.model.generate_content_async(prompt)
            
            text_response = ""
            # Ensure all parts of the response are concatenated
            for part in response.parts:
                text_response += part.text
            
            logger.info(f"Successfully received non-DSPy response from Gemini. Length: {len(text_response)}")

            if is_json_output:
                try:
                    cleaned_response = text_response.strip()
                    if cleaned_response.startswith("```json"):
                        cleaned_response = cleaned_response[7:]
                        if cleaned_response.endswith("```"):
                            cleaned_response = cleaned_response[:-3]

                    json_response = json.loads(cleaned_response)
                    logger.info("Successfully parsed JSON from non-DSPy response.")
                    return json_response
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from non-DSPy response: {e}. Response text: {text_response}")
                    return text_response

            return text_response
        except Exception as e:
            logger.error(f"Error generating text from non-DSPy Gemini: {e}", exc_info=True)
            raise

    async def query_gemini_for_raw_json(self, prompt: str) -> str | None:
        """
        DEPRECATED: DSPy modules should handle their own prompting and parsing.
        This method used the non-DSPy google.generativeai SDK.
        """
        logger.warning("`query_gemini_for_raw_json` is deprecated. Use DSPy modules for structured output.")
        if not self.model:
            logger.error("GeminiService google.generativeai model not initialized. Cannot query for raw JSON.")
            return None

        logger.info(f"Querying Gemini (non-DSPy) for raw JSON with prompt: {prompt[:100]}...")
        try:
            response = await self.model.generate_content_async(prompt)
            raw_response_text = ""
            for part in response.parts:
                raw_response_text += part.text

            logger.info(f"Successfully received raw non-DSPy response from Gemini. Length: {len(raw_response_text)}")
            match = re.search(r"```json\s*([\s\S]*?)\s*```", raw_response_text, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
            else:
                start_brace = raw_response_text.find('{')
                end_brace = raw_response_text.rfind('}')
                if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
                    json_str = raw_response_text[start_brace:end_brace+1].strip()
                else:
                    json_str = raw_response_text.strip()
            try:
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError:
                logger.warning(f"Could not validate extracted string as JSON from non-DSPy: {json_str[:200]}...")
                return raw_response_text
        except Exception as e:
            logger.error(f"Error querying non-DSPy Gemini for raw JSON: {e}", exc_info=True)
            return None

# Note: The complex pipeline functions previously in this file were removed by this overwrite.
# This refactoring focuses on centralizing DSPy configuration within GeminiService.
