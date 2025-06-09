import json
import requests
import logging
import base64
import os
from typing import Dict, Any, Optional

from config import GEMINI_API_KEY # Import the Gemini API key from config

logger = logging.getLogger(__name__) # Logger for this module

# Placeholder API key for checking if the actual key is set
PLACEHOLDER_GEMINI_API_KEY = "AIzaSyB5KbPaVXPYkUeShTEE82fgpZiLiLl7YyM"

def query_gemini_with_audio(audio_path: str, transcript: str, flags: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Queries the Google Gemini Pro Vision model with both audio data and its transcript
    for a comprehensive multi-modal analysis.

    The function constructs a detailed prompt including the transcript, pre-identified flags,
    and optional session context. It then sends this along with the base64-encoded audio
    data to the Gemini API. The response is expected to be a JSON object matching a
    specific structure defined in the prompt.

    Args:
        audio_path: Path to the audio file to be analyzed.
        transcript: The text transcript of the audio.
        flags: A dictionary of preliminary flags or indicators identified by other services.
        session_context: Optional dictionary containing context from the current session,
                         such as previous analyses or conversation history.

    Returns:
        A dictionary containing the structured analysis from Gemini, or an error dictionary
        if the API call fails, the API key is missing/invalid, or the response is malformed.
    """
    # Check if the API key is missing or is the placeholder key
    if not GEMINI_API_KEY or GEMINI_API_KEY == PLACEHOLDER_GEMINI_API_KEY:
        logger.error("Missing or placeholder Gemini API key. Cannot query Gemini with audio.")
        return {"error": "Missing or placeholder Gemini API key"}

    try:
        # Read audio file in binary mode
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        # Encode audio data to base64 string
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Determine the MIME type of the audio file based on its extension
        file_ext = os.path.splitext(audio_path)[1].lower()
        mime_type_map = {  # Mapping of common audio extensions to MIME types
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg', 
            '.m4a': 'audio/mp4', # Covers .m4a, .aac
            '.ogg': 'audio/ogg',
            '.webm': 'audio/webm',
            '.flac': 'audio/flac'
        }
        mime_type = mime_type_map.get(file_ext, 'audio/wav') # Default to WAV if unknown
        
        # Base prompt for Gemini, instructing it on the analysis task
        base_prompt = f"""
        Analyze the provided audio file for deception, stress, vocal patterns, and speaker characteristics.
        
        You have access to both the audio file and its transcription. Use the audio to analyze:
        - Vocal stress indicators (pitch variations, speaking rate changes)
        - Hesitation patterns and pause analysis
        - Voice quality and emotional undertones
        - Vocal authenticity vs. performance
        - Micro-expressions in speech
        - Breathing patterns and vocal tension
        
        TRANSCRIPT FOR REFERENCE:
        {transcript}

        INITIAL DECEPTION FLAGS DETECTED (from other analyses):
        {json.dumps(flags, indent=2)}
        """

        # If session context is available, append it to the prompt
        if session_context and session_context.get("previous_analyses", 0) > 0:
            # Constructing the contextual part of the prompt
            context_prompt = f"""

        CONVERSATION CONTEXT (This is Analysis #{session_context.get('previous_analyses', 0) + 1} in the current session):
        - Current Session Duration: {session_context.get('session_duration', 0):.1f} minutes
        - Number of Previous Analyses in this Session: {session_context.get('previous_analyses', 0)}

        RECENT CONVERSATION HISTORY (Transcripts from this session):
        {json.dumps(session_context.get('recent_transcripts', []), indent=2)}

        AGGREGATED PATTERN ANALYSIS FROM THIS SESSION:
        - Recurring Deception Flags Observed: {json.dumps(session_context.get('recent_patterns', {}).get('recurring_deception_flags', {}), indent=2)}
        - Emotional Trends Observed: {json.dumps(session_context.get('recent_patterns', {}).get('emotion_trends', {}), indent=2)}
        - Credibility Score Trend in Session: {session_context.get('recent_patterns', {}).get('credibility_trend', [])}

        INSTRUCTIONS FOR CONTEXTUAL ANALYSIS (Leverage Audio and History):
        - Compare current vocal patterns (pitch, rate, stress) with previous recordings in this session if applicable.
        - Identify consistency or inconsistency in vocal delivery and statements across the conversation.
        - Note any escalation or de-escalation in vocal stress indicators compared to earlier in the session.
        - Assess if the speaker's vocal characteristics suggest increasing or decreasing authenticity over time.
        - Determine if current vocal patterns support or contradict previous statements made in this session.
        """
            base_prompt += context_prompt # Append context to the base prompt

        # The final part of the prompt, specifying the desired JSON output structure
        full_prompt = base_prompt + """

        Perform a comprehensive audio-based lie detection analysis and return a valid JSON response with the following EXACT structure:

        {
            "speaker_transcripts": {"Speaker 1": "text content for this speaker"},
            "red_flags_per_speaker": {"Speaker 1": ["specific vocal and behavioral deception indicators found"]},
            "credibility_score": 75,
            "confidence_level": "high",
            "gemini_summary": {
                "tone": "detailed analysis of speaker's vocal tone, pitch, and delivery",
                "motivation": "assessment of underlying motivations based on vocal cues and content",
                "credibility": "vocal authenticity assessment with specific reasoning",
                "emotional_state": "emotional consistency between voice and words",
                "communication_style": "vocal patterns, rhythm, and speaking style analysis",
                "key_concerns": "main vocal stress and deception indicators identified",
                "strengths": "vocal aspects that support credibility and authenticity"
            },
            "recommendations": [
                "specific actionable recommendation based on vocal analysis",
                "follow-up questions or verification steps"
            ],
            "linguistic_analysis": {
                "speech_patterns": "analysis of vocal rhythm, pace, pauses, hesitations",
                "word_choice": "vocabulary analysis combined with vocal delivery", 
                "emotional_consistency": "alignment between vocal emotion and content",
                "detail_level": "vocal confidence in details vs. vague responses"
            },
            "risk_assessment": {
                "overall_risk": "low/medium/high",
                "risk_factors": ["specific vocal risk indicators", "behavioral concerns from audio"],
                "mitigation_suggestions": ["verification steps", "follow-up recommendations"]
            },
            "audio_analysis": {
                "vocal_stress_indicators": "specific vocal stress patterns detected",
                "speaking_rate_variations": "changes in speaking speed and fluency",
                "pitch_analysis": "pitch variations and emotional undertones",
                "pause_patterns": "significant pauses, hesitations, or interruptions",
                "voice_quality": "overall voice quality and authenticity assessment"
            },
            "manipulation_assessment": {
                "manipulation_score": 0,
                "manipulation_tactics": ["e.g., gaslighting, guilt-tripping"],
                "manipulation_explanation": "explanation of manipulative tactics used",
                "example_phrases": ["specific phrases indicating manipulation"]
            },
            "argument_analysis": {
                "argument_strengths": ["speaker's strong points"],
                "argument_weaknesses": ["speaker's weak points"],
                "overall_argument_coherence_score": 0
            },
            "speaker_attitude": {
                "respect_level_score": 0,
                "sarcasm_detected": false,
                "sarcasm_confidence_score": 0,
                "tone_indicators_respect_sarcasm": ["words/phrases indicating respect/sarcasm"]
            },
            "enhanced_understanding": {
                "key_inconsistencies": ["list of contradictions"],
                "areas_of_evasiveness": ["topics speaker avoided"],
                "suggested_follow_up_questions": ["questions to ask for clarity"],
                "unverified_claims": ["claims needing fact-checking"]
            }
        }

        DETAILED INSTRUCTIONS FOR NEW SECTIONS:
        - Manipulation Assessment: Analyze for manipulative language. Provide a score (0-100 for manipulation likelihood), list identified tactics (e.g., gaslighting, guilt-tripping), explain why, and list example phrases.
        - Argument Analysis: Assess the strengths and weaknesses of the speaker's arguments. Provide lists for strengths and weaknesses, and an overall coherence score (0-100).
        - Speaker Attitude: Evaluate the speaker's tone for respect and sarcasm. Provide a respect score (0-100, high is respectful), indicate if sarcasm is detected (true/false) with a confidence score (0-100 if true), and list contributing tone indicators. Use audio cues heavily for this.
        - Enhanced Understanding: Identify elements for deeper insight. List key inconsistencies, areas of evasiveness, 2-3 suggested follow-up questions, and any unverified claims made by the speaker.

        CRITICAL REQUIREMENTS:
        - Return ONLY valid JSON, no markdown formatting, no ```json blocks
        - Use the audio file to enhance all analysis beyond just the transcript
        - All string values must be meaningful and based on actual audio analysis
        - credibility_score, manipulation_score, overall_argument_coherence_score, respect_level_score, sarcasm_confidence_score must be integers 0-100
        - confidence_level must be: "very_low", "low", "medium", "high", "very_high"
        - overall_risk must be: "low", "medium", "high"
        - sarcasm_detected must be boolean (true/false)
        - Include specific vocal observations in all analysis sections
        - All arrays must contain at least 1 meaningful item (use an empty array [] if no items apply, but ensure the field is present)
        - All new fields (manipulation_assessment, argument_analysis, speaker_attitude, enhanced_understanding) and their sub-fields are MANDATORY and must be correctly formatted.
        """

        # Gemini API endpoint for the gemini-1.5-flash model (supports audio)
        gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

        headers = {"Content-Type": "application/json"}
        # Construct the payload for the Gemini API request
        payload = {
            "contents": [{
                "parts": [
                    {"text": full_prompt}, # The detailed text prompt
                    {
                        "inline_data": { # The audio data
                            "mime_type": mime_type, # MIME type of the audio
                            "data": audio_base64    # Base64-encoded audio string
                        }
                    }
                ]
            }],
            "generationConfig": { # Configuration for the generation process
                "temperature": 0.7,       # Controls randomness
                "topK": 1,                # Considers the top K tokens
                "topP": 1,                # Uses nucleus sampling
                "maxOutputTokens": 4096   # Maximum number of tokens in the response
            }
        }

        logger.info(f"Sending multi-modal (audio + text) analysis request to Gemini. Audio size: {len(audio_data)} bytes. Mime-type: {mime_type}.")
        # Make the POST request to the Gemini API
        response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200: # Successful API call
            gemini_response = response.json()
            logger.info("Gemini multi-modal analysis response received successfully.")
            
            # Validate the structure of the Gemini response
            if 'candidates' not in gemini_response or not gemini_response['candidates']:
                logger.error("No 'candidates' field in Gemini response.", extra={"gemini_raw_response": gemini_response})
                return {"error": "No candidates in Gemini response", "gemini_raw_response": gemini_response}

            candidate = gemini_response['candidates'][0]
            if 'content' not in candidate or 'parts' not in candidate['content'] or not candidate['content']['parts']:
                logger.error("Invalid content structure in Gemini candidate.", extra={"gemini_raw_response": gemini_response})
                return {"error": "Invalid content structure in Gemini candidate", "gemini_raw_response": gemini_response}

            # Extract the text part of the response, which should be the JSON string
            text_response_part = candidate['content']['parts'][0].get('text', '')

            # Clean the response: remove markdown ```json ... ``` or ``` ... ``` if present
            if text_response_part.strip().startswith('```json'):
                text_response_part = text_response_part.strip()[7:-3].strip()
            elif text_response_part.strip().startswith('```'):
                text_response_part = text_response_part.strip()[3:-3].strip()

            try:
                # Attempt to parse the cleaned text as JSON
                result = json.loads(text_response_part)
                logger.info("Successfully parsed Gemini multi-modal analysis JSON response.")
                return result
            except json.JSONDecodeError as e:
                # Log error if JSON parsing fails
                logger.error(f"Failed to parse Gemini JSON response from multi-modal query: {str(e)}. Raw text (first 500 chars): {text_response_part[:500]}...")
                return {"error": f"Failed to parse Gemini JSON response: {str(e)}", "gemini_text_response": text_response_part}
        else:
            # Log error if API call was not successful
            logger.error(f"Gemini API error (multi-modal query): {response.status_code} - {response.text}")
            return {"error": f"Gemini API error: {response.status_code} - {response.text}"}
            
    except Exception as e:
        # Log any other exceptions that occur during the process
        logger.error(f"Exception in query_gemini_with_audio: {str(e)}", exc_info=True)
        return {"error": f"Gemini audio analysis error: {str(e)}"}


def query_gemini(transcript: str, flags: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Queries the Google Gemini Pro model (text-only) with a transcript for analysis.

    This function is similar to `query_gemini_with_audio` but sends only text data.
    It constructs a detailed prompt including the transcript, pre-identified flags,
    and optional session context. The response is expected to be a JSON object
    matching a specific structure defined in the prompt.

    Args:
        transcript: The text transcript to be analyzed.
        flags: A dictionary of preliminary flags or indicators identified by other services.
        session_context: Optional dictionary containing context from the current session.

    Returns:
        A dictionary containing the structured analysis from Gemini, or an error dictionary
        if the API call fails, the API key is missing/invalid, or the response is malformed.
    """
    # Check if the API key is missing or is the placeholder key
    if not GEMINI_API_KEY or GEMINI_API_KEY == PLACEHOLDER_GEMINI_API_KEY:
        logger.error("Missing or placeholder Gemini API key. Cannot query Gemini (text-only).")
        return {"error": "Missing or placeholder Gemini API key"}

    # Base prompt for Gemini, focused on text-based analysis
    base_prompt = f"""
    Analyze the transcript for deception, stress, and speaker separation.

    CURRENT TRANSCRIPT:
    {transcript}

    RED FLAGS FROM PRIMARY ANALYSIS:
    {json.dumps(flags, indent=2)}
    """

    if session_context and session_context.get("previous_analyses", 0) > 0:
        context_prompt = f"""

    CONVERSATION CONTEXT (Session Analysis #{session_context.get('previous_analyses', 0) + 1}):
    - Session Duration: {session_context.get('session_duration', 0):.1f} minutes
    - Previous Analyses: {session_context.get('previous_analyses', 0)}

    RECENT CONVERSATION HISTORY:
    {json.dumps(session_context.get('recent_transcripts', []), indent=2)}

    PATTERN ANALYSIS FROM SESSION:
    - Recurring Deception Patterns: {json.dumps(session_context.get('recent_patterns', {}).get('recurring_deception_flags', {}), indent=2)}
    - Emotional Trends: {json.dumps(session_context.get('recent_patterns', {}).get('emotion_trends', {}), indent=2)}
    - Credibility Score Trend: {session_context.get('recent_patterns', {}).get('credibility_trend', [])}

    INSTRUCTIONS FOR CONTEXTUAL ANALYSIS:
    - Compare current statement with previous statements in this session
    - Look for consistency/inconsistency patterns across the conversation
    - Note any escalation or de-escalation in deception indicators
        - Consider if the speaker is becoming more or less credible over time
    - Identify if they are reinforcing previous statements or contradicting them.
    - Note that audio cues are NOT available for this analysis; rely solely on text.
    """
        base_prompt += context_prompt # Append context to the base prompt

    # The final part of the prompt, specifying the desired JSON output structure for text-only analysis
    full_prompt = base_prompt + """

    You MUST return a valid JSON response with the following EXACT structure. Do not include any text before or after the JSON:

    {
        "speaker_transcripts": {"Speaker 1": "text content for this speaker"},
        "red_flags_per_speaker": {"Speaker 1": ["specific deception indicators found"]},
        "credibility_score": 75,
        "confidence_level": "high",
        "gemini_summary": {
            "tone": "detailed analysis of speaker's tone and manner",
            "motivation": "assessment of underlying motivations and intent",
            "credibility": "specific credibility assessment with reasoning",
            "emotional_state": "emotional consistency and authenticity analysis",
            "communication_style": "communication patterns and verbal behaviors",
            "key_concerns": "main red flags or concerns identified",
            "strengths": "aspects that support credibility"
        },
        "recommendations": [
            "specific actionable recommendation 1",
            "specific actionable recommendation 2"
        ],
        "linguistic_analysis": {
            "speech_patterns": "analysis of speech rhythm, pace, pauses",
            "word_choice": "analysis of vocabulary and phrasing choices",
            "emotional_consistency": "consistency between claimed emotions and expression",
            "detail_level": "appropriate level of detail vs vagueness"
        },
        "risk_assessment": {
            "overall_risk": "low/medium/high",
            "risk_factors": ["specific risk factor 1", "specific risk factor 2"],
            "mitigation_suggestions": ["suggestion 1", "suggestion 2"]
        },
        "manipulation_assessment": {
            "manipulation_score": 0,
            "manipulation_tactics": ["e.g., gaslighting, guilt-tripping"],
            "manipulation_explanation": "explanation of manipulative tactics used",
            "example_phrases": ["specific phrases indicating manipulation"]
        },
        "argument_analysis": {
            "argument_strengths": ["speaker's strong points"],
            "argument_weaknesses": ["speaker's weak points"],
            "overall_argument_coherence_score": 0
        },
        "speaker_attitude": {
            "respect_level_score": 0,
            "sarcasm_detected": false,
            "sarcasm_confidence_score": 0,
            "tone_indicators_respect_sarcasm": ["words/phrases indicating respect/sarcasm"]
        },
        "enhanced_understanding": {
            "key_inconsistencies": ["list of contradictions"],
            "areas_of_evasiveness": ["topics speaker avoided"],
            "suggested_follow_up_questions": ["questions to ask for clarity"],
            "unverified_claims": ["claims needing fact-checking"]
        }
    }

    DETAILED INSTRUCTIONS FOR NEW SECTIONS (TEXT-ONLY ANALYSIS):
    - Manipulation Assessment: Analyze for manipulative language based on text. Provide a score (0-100 for manipulation likelihood), list identified tactics (e.g., gaslighting, guilt-tripping), explain why, and list example phrases.
    - Argument Analysis: Assess the strengths and weaknesses of the speaker's arguments from text. Provide lists for strengths and weaknesses, and an overall coherence score (0-100).
    - Speaker Attitude: Evaluate the speaker's tone for respect and sarcasm based on text. Provide a respect score (0-100, high is respectful), indicate if sarcasm is detected (true/false) with a confidence score (0-100 if true), and list contributing tone indicators. Acknowledge that text-only analysis for sarcasm is challenging.
    - Enhanced Understanding: Identify elements for deeper insight from text. List key inconsistencies, areas of evasiveness, 2-3 suggested follow-up questions, and any unverified claims made by the speaker.

    CRITICAL REQUIREMENTS:
    - Return ONLY valid JSON, no markdown formatting, no ```json blocks
    - All string values must be meaningful, not placeholder text
    - credibility_score, manipulation_score, overall_argument_coherence_score, respect_level_score, sarcasm_confidence_score must be integers 0-100
    - confidence_level must be: "very_low", "low", "medium", "high", "very_high"
    - overall_risk must be: "low", "medium", "high"
    - sarcasm_detected must be boolean (true/false)
    - All arrays must contain at least 1 meaningful item (use an empty array [] if no items apply, but ensure the field is present)
    - All object fields must be present and non-empty, including all new fields (manipulation_assessment, argument_analysis, speaker_attitude, enhanced_understanding) and their sub-fields.
    """
    # Gemini API endpoint for the gemini-1.5-flash model (can also be used for text-only)
    gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    # Construct the payload for the Gemini API request (text-only)
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}], # Only text part is included
        "generationConfig": { # Configuration for the generation process
            "temperature": 0.7,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 3072 # Max tokens for the response
        }
    }

    try:
        logger.info("Sending text-only analysis request to Gemini.")
        # Make the POST request to the Gemini API
        response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200: # Successful API call
            gemini_response = response.json()
            logger.info("Gemini text-only analysis response received successfully.")
            # Log a snippet of the response structure for debugging
            logger.debug(f"Gemini API response structure (text-only): {json.dumps(gemini_response, indent=2)[:500]}...")

            # Validate the structure of the Gemini response
            if 'candidates' not in gemini_response or not gemini_response['candidates']:
                logger.error("No 'candidates' field in Gemini response (text-only).", extra={"gemini_raw_response": gemini_response})
                return {"error": "No candidates in Gemini response", "gemini_raw_response": gemini_response}

            candidate = gemini_response['candidates'][0]
            if 'content' not in candidate or 'parts' not in candidate['content'] or not candidate['content']['parts']:
                logger.error("Invalid content structure in Gemini candidate (text-only).", extra={"gemini_raw_response": gemini_response})
                return {"error": "Invalid content structure in Gemini candidate", "gemini_raw_response": gemini_response}

            # Extract the text part of the response
            text_response_part = candidate['content']['parts'][0].get('text', '')

            # Clean the response: remove markdown ```json ... ``` or ``` ... ``` if present
            if text_response_part.strip().startswith('```json'):
                text_response_part = text_response_part.strip()[7:-3].strip()
            elif text_response_part.strip().startswith('```'):
                 text_response_part = text_response_part.strip()[3:-3].strip()

            try:
                # Attempt to parse the cleaned text as JSON
                return json.loads(text_response_part)
            except json.JSONDecodeError as e:
                # Log error if JSON parsing fails
                logger.error(f"Failed to parse Gemini JSON response from text-only query: {str(e)}. Raw text (first 500 chars): {text_response_part[:500]}...")
                return {"error": f"Failed to parse Gemini JSON response: {str(e)}", "gemini_text_response": text_response_part}
        else:
            # Log error if API call was not successful
            logger.error(f"Gemini API error (text-only query): {response.status_code} - {response.text}")
            return {"error": f"Gemini API error: {response.status_code} - {response.text}"}
    except Exception as e:
        # Log any other exceptions
        logger.error(f"Exception in query_gemini (text-only): {str(e)}", exc_info=True)
        return {"error": f"Gemini request error: {str(e)}"}

def validate_and_structure_gemini_response(raw_response: Dict[str, Any], transcript: str, quantitative_linguistic: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validates the raw JSON response from Gemini against a predefined structure and
    fills in missing fields with default values.

    This function ensures that the application receives a consistently structured
    dictionary, even if the Gemini API response is incomplete, malformed, or
    if an error occurred during the API call. It logs warnings for missing
    or improperly formatted fields.

    Args:
        raw_response: The dictionary parsed from Gemini's JSON response.
                      This could also be an error dictionary if the API call failed.
        transcript: The original transcript that was analyzed. Used as a fallback
                    for speaker_transcripts if not provided by Gemini.
        quantitative_linguistic: Optional dictionary containing pre-calculated
                                 quantitative linguistic features. If provided,
                                 this will be used for the 'linguistic_analysis'
                                 field; otherwise, a default structure is used.

    Returns:
        A dictionary conforming to the application's expected analysis structure.
        This includes all fields from the `default_structure`, with values
        populated from `raw_response` where available and valid, or defaults otherwise.
    """
    # Import here to avoid circular import with linguistic_service
    from services.linguistic_service import get_default_linguistic_analysis
    
    # Use provided quantitative linguistic analysis or get a default structure
    # This ensures 'linguistic_analysis' is always populated.
    current_linguistic_analysis = quantitative_linguistic if quantitative_linguistic is not None else get_default_linguistic_analysis()
    
    # Define the comprehensive default structure for the analysis response.
    # This acts as a template and provides fallbacks for all expected fields.
    default_structure = {
        "speaker_transcripts": {"Speaker 1": transcript}, # Fallback speaker transcript
        "red_flags_per_speaker": {"Speaker 1": []}, # Default empty list of red flags
        "credibility_score": 50, # Default credibility score (neutral)
        "confidence_level": "medium", # Default confidence level
        "gemini_summary": { # Default summary structure with placeholder text
            "tone": "Analysis pending - technical issue encountered",
            "motivation": "Unable to determine - requires manual review",
            "credibility": "Inconclusive - technical analysis limitation",
            "emotional_state": "Analysis incomplete",
            "communication_style": "Requires further analysis",
            "key_concerns": "Technical analysis limitation",
            "strengths": "Unable to assess automatically"
        },
        "recommendations": [ # Default recommendations
            "Manual review recommended due to technical analysis limitations",
            "Consider re-running analysis with different audio quality or transcript"
        ],
        "linguistic_analysis": current_linguistic_analysis, # Use current (either passed in or default)
        "risk_assessment": { # Default risk assessment
            "overall_risk": "medium",
            "risk_factors": ["Technical analysis limitation"],
            "mitigation_suggestions": ["Manual review recommended"]
        },
        # Default structures for newer analysis sections, ensuring they are always present
        "manipulation_assessment": {
            "manipulation_score": 0,
            "manipulation_tactics": [],
            "manipulation_explanation": "N/A - Analysis potentially incomplete or encountered an issue.",
            "example_phrases": []
        },
        "argument_analysis": {
            "argument_strengths": [],
            "argument_weaknesses": [],
            "overall_argument_coherence_score": 0
        },
        "speaker_attitude": {
            "respect_level_score": 50, # Neutral respect
            "sarcasm_detected": False,
            "sarcasm_confidence_score": 0,
            "tone_indicators_respect_sarcasm": []
        },
        "enhanced_understanding": {
            "key_inconsistencies": [],
            "areas_of_evasiveness": [],
            "suggested_follow_up_questions": [],
            "unverified_claims": []
        },
        "audio_analysis": { # Default audio_analysis (relevant for audio queries, but good to have a default)
            "vocal_stress_indicators": "N/A",
            "speaking_rate_variations": "N/A",
            "pitch_analysis": "N/A",
            "pause_patterns": "N/A",
            "voice_quality": "N/A"
        }
    }

    # Handle cases where raw_response indicates an error or is not a dictionary
    if not isinstance(raw_response, dict) or raw_response.get('error'):
        error_message = raw_response.get('error') if isinstance(raw_response, dict) else 'Invalid raw_response type'
        logger.warning(f"Gemini API error or invalid raw_response ('{error_message}'), using default structure with original transcript and linguistic analysis.")
        # Return a copy of the default structure, ensuring the original transcript and linguistic analysis are preserved.
        complete_default = default_structure.copy()
        complete_default["speaker_transcripts"] = {"Speaker 1": transcript} # Ensure original transcript is used
        complete_default["linguistic_analysis"] = current_linguistic_analysis # Ensure passed or fresh default linguistic data
        return complete_default

    # Initialize validated_response by deep copying default_structure to avoid modifying it directly
    validated_response = default_structure.copy()

    # List of all top-level fields expected in the response
    # This includes original fields and newly added ones for comprehensive validation.
    all_expected_top_level_fields = [
        'speaker_transcripts', 'red_flags_per_speaker', 'credibility_score',
        'confidence_level', 'gemini_summary', 'recommendations',
        'linguistic_analysis', 'risk_assessment', 'audio_analysis', # audio_analysis added here
        'manipulation_assessment', 'argument_analysis',
        'speaker_attitude', 'enhanced_understanding'
    ]

    # Iterate over all expected top-level fields to populate validated_response
    for field in all_expected_top_level_fields:
        if field in raw_response:
            # If the field exists in raw_response, use its value.
            # Special handling for nested dictionaries to ensure they are dicts.
            if isinstance(default_structure.get(field), dict):
                if isinstance(raw_response[field], dict):
                    # If both default and raw are dicts, merge them (raw takes precedence for existing keys)
                    validated_response[field] = {**default_structure[field], **raw_response[field]}
                else:
                    # If raw value is not a dict, but default is, log warning and use default for this field.
                    logger.warning(f"Field '{field}' in Gemini response was type {type(raw_response[field])}, expected dict. Using default for this field.")
                    validated_response[field] = default_structure[field] # Fallback to default's sub-structure
            else:
                # For non-dictionary fields, directly assign the value from raw_response.
                validated_response[field] = raw_response[field]
        else:
            # If field is missing in raw_response, it's already set from default_structure copy.
            logger.warning(f"Missing top-level field '{field}' in Gemini response. Using default value/structure for it.")
            # No explicit assignment needed here as validated_response started as a copy of default_structure.

    # === Detailed Validation and Normalization for specific fields ===

    # Validate and normalize 'credibility_score' (integer, 0-100)
    try:
        score = int(validated_response.get('credibility_score', default_structure['credibility_score']))
        validated_response['credibility_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning(f"Invalid credibility_score '{validated_response.get('credibility_score')}', defaulting to {default_structure['credibility_score']}.")
        validated_response['credibility_score'] = default_structure['credibility_score']

    # Validate 'confidence_level' (specific string values)
    valid_confidence_levels = ["very_low", "low", "medium", "high", "very_high"]
    if validated_response.get('confidence_level') not in valid_confidence_levels:
        logger.warning(f"Invalid confidence_level '{validated_response.get('confidence_level')}', defaulting to '{default_structure['confidence_level']}'.")
        validated_response['confidence_level'] = default_structure['confidence_level']

    # Helper function to validate fields that should be a list of strings
    def _validate_list_of_strings(parent_dict: Dict, key: str, default_list: List[str]) -> None:
        """Ensures parent_dict[key] is a list of strings, defaulting if not."""
        value = parent_dict.get(key)
        if not isinstance(value, list):
            logger.warning(f"Invalid type for '{key}', expected list, got {type(value)}. Defaulting to: {default_list}.")
            parent_dict[key] = list(default_list) # Ensure it's a copy
            return
        # Ensure all items in the list are strings
        parent_dict[key] = [str(item) for item in value]

    # Validate 'gemini_summary' sub-fields (ensure they are strings)
    # validated_response['gemini_summary'] is already a dict due to earlier logic
    for key, default_val_str in default_structure['gemini_summary'].items():
        val = validated_response['gemini_summary'].get(key, default_val_str)
        if isinstance(val, list): # Common issue: Gemini might return a list for a string field
            logger.warning(f"gemini_summary.{key} was a list, converting to string: {val}")
            validated_response['gemini_summary'][key] = '; '.join(map(str, val)) if val else default_val_str
        elif not isinstance(val, str):
            logger.warning(f"gemini_summary.{key} was not a string ({type(val)}), coercing to string or using default: {val}")
            validated_response['gemini_summary'][key] = str(val) if val is not None else default_val_str
        elif not val and default_val_str: # If empty string and default is not empty
             validated_response['gemini_summary'][key] = default_val_str


    # Validate 'linguistic_analysis' - ensure all sub-fields from default are present
    # This primarily handles numeric fields that might be missing or None.
    # validated_response['linguistic_analysis'] is already a dict.
    for key, default_val in default_structure['linguistic_analysis'].items():
        if key not in validated_response['linguistic_analysis'] or validated_response['linguistic_analysis'][key] is None:
            validated_response['linguistic_analysis'][key] = default_val

    # Validate 'risk_assessment' sub-fields
    # validated_response['risk_assessment'] is already a dict.
    if validated_response['risk_assessment'].get('overall_risk') not in ["low", "medium", "high"]:
        logger.warning(f"Invalid overall_risk '{validated_response['risk_assessment'].get('overall_risk')}', defaulting.")
        validated_response['risk_assessment']['overall_risk'] = default_structure['risk_assessment']['overall_risk']
    _validate_list_of_strings(validated_response['risk_assessment'], 'risk_factors', default_structure['risk_assessment']['risk_factors'])
    _validate_list_of_strings(validated_response['risk_assessment'], 'mitigation_suggestions', default_structure['risk_assessment']['mitigation_suggestions'])

    # Validate 'recommendations' (list of strings)
    _validate_list_of_strings(validated_response, 'recommendations', default_structure['recommendations'])

    # Validate 'audio_analysis' sub-fields (ensure they are strings)
    # validated_response['audio_analysis'] is already a dict.
    for key, default_val_str in default_structure['audio_analysis'].items():
        val = validated_response['audio_analysis'].get(key, default_val_str)
        if not isinstance(val, str):
            logger.warning(f"audio_analysis.{key} was not a string ({type(val)}), coercing or using default: {val}")
            validated_response['audio_analysis'][key] = str(val) if val is not None else default_val_str
        elif not val and default_val_str: # If empty string and default is not empty
             validated_response['audio_analysis'][key] = default_val_str


    # --- Validation for "Newer" Sections (Manipulation, Argument, Attitude, Enhanced Understanding) ---
    # These sections follow a similar pattern: ensure dict, validate scores, validate lists of strings.

    # ManipulationAssessment
    # validated_response['manipulation_assessment'] is already a dict.
    try:
        score = int(validated_response['manipulation_assessment'].get('manipulation_score', default_structure['manipulation_assessment']['manipulation_score']))
        validated_response['manipulation_assessment']['manipulation_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid manipulation_score, defaulting.")
        validated_response['manipulation_assessment']['manipulation_score'] = default_structure['manipulation_assessment']['manipulation_score']
    _validate_list_of_strings(validated_response['manipulation_assessment'], 'manipulation_tactics', default_structure['manipulation_assessment']['manipulation_tactics'])
    validated_response['manipulation_assessment']['manipulation_explanation'] = str(validated_response['manipulation_assessment'].get('manipulation_explanation', "") or default_structure['manipulation_assessment']['manipulation_explanation'])
    _validate_list_of_strings(validated_response['manipulation_assessment'], 'example_phrases', default_structure['manipulation_assessment']['example_phrases'])

    # ArgumentAnalysis
    # validated_response['argument_analysis'] is already a dict.
    _validate_list_of_strings(validated_response['argument_analysis'], 'argument_strengths', default_structure['argument_analysis']['argument_strengths'])
    _validate_list_of_strings(validated_response['argument_analysis'], 'argument_weaknesses', default_structure['argument_analysis']['argument_weaknesses'])
    try:
        score = int(validated_response['argument_analysis'].get('overall_argument_coherence_score', default_structure['argument_analysis']['overall_argument_coherence_score']))
        validated_response['argument_analysis']['overall_argument_coherence_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid overall_argument_coherence_score, defaulting.")
        validated_response['argument_analysis']['overall_argument_coherence_score'] = default_structure['argument_analysis']['overall_argument_coherence_score']

    # SpeakerAttitude
    # validated_response['speaker_attitude'] is already a dict.
    try:
        score = int(validated_response['speaker_attitude'].get('respect_level_score', default_structure['speaker_attitude']['respect_level_score']))
        validated_response['speaker_attitude']['respect_level_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid respect_level_score, defaulting.")
        validated_response['speaker_attitude']['respect_level_score'] = default_structure['speaker_attitude']['respect_level_score']

    sarcasm_detected_val = validated_response['speaker_attitude'].get('sarcasm_detected', default_structure['speaker_attitude']['sarcasm_detected'])
    if not isinstance(sarcasm_detected_val, bool):
        logger.warning(f"Invalid sarcasm_detected type ({type(sarcasm_detected_val)}), defaulting.")
        validated_response['speaker_attitude']['sarcasm_detected'] = default_structure['speaker_attitude']['sarcasm_detected']

    try:
        score = int(validated_response['speaker_attitude'].get('sarcasm_confidence_score', default_structure['speaker_attitude']['sarcasm_confidence_score']))
        validated_response['speaker_attitude']['sarcasm_confidence_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid sarcasm_confidence_score, defaulting.")
        validated_response['speaker_attitude']['sarcasm_confidence_score'] = default_structure['speaker_attitude']['sarcasm_confidence_score']
    _validate_list_of_strings(validated_response['speaker_attitude'], 'tone_indicators_respect_sarcasm', default_structure['speaker_attitude']['tone_indicators_respect_sarcasm'])

    # EnhancedUnderstanding
    # validated_response['enhanced_understanding'] is already a dict.
    _validate_list_of_strings(validated_response['enhanced_understanding'], 'key_inconsistencies', default_structure['enhanced_understanding']['key_inconsistencies'])
    _validate_list_of_strings(validated_response['enhanced_understanding'], 'areas_of_evasiveness', default_structure['enhanced_understanding']['areas_of_evasiveness'])
    _validate_list_of_strings(validated_response['enhanced_understanding'], 'suggested_follow_up_questions', default_structure['enhanced_understanding']['suggested_follow_up_questions'])
    _validate_list_of_strings(validated_response['enhanced_understanding'], 'unverified_claims', default_structure['enhanced_understanding']['unverified_claims'])

    # Final check: ensure speaker_transcripts is populated, defaulting to the input transcript if necessary.
    if not validated_response.get('speaker_transcripts') or not isinstance(validated_response.get('speaker_transcripts'), dict):
        logger.warning("speaker_transcripts was missing or not a dict in Gemini response, setting to default with input transcript.")
        validated_response['speaker_transcripts'] = {"Speaker 1": transcript}
    elif not validated_response['speaker_transcripts'].get("Speaker 1"): # Or if "Speaker 1" is missing/empty
        logger.info("speaker_transcripts did not contain 'Speaker 1' or it was empty, ensuring input transcript is present.")
        # This assumes single speaker for now or that Gemini should provide "Speaker 1"
        validated_response['speaker_transcripts']["Speaker 1"] = validated_response['speaker_transcripts'].get("Speaker 1") or transcript


    logger.info("Gemini response validation and structuring complete.")
    return validated_response
