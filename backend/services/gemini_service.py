import json
import requests
import logging
import base64
import os
from typing import Dict, Any, Optional

from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

def query_gemini_with_audio(audio_path: str, transcript: str, flags: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Enhanced Gemini query that includes both audio data and transcript for more comprehensive analysis
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSyB5KbPaVXPYkUeShTEE82fgpZiLiLl7YyM":
        logger.error("Missing or placeholder Gemini API key. Cannot query Gemini.")
        return {"error": "Missing or placeholder Gemini API key"}

    try:
        # Read and encode audio file
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Determine audio MIME type based on file extension
        file_ext = os.path.splitext(audio_path)[1].lower()
        mime_type_map = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg', 
            '.m4a': 'audio/mp4',
            '.ogg': 'audio/ogg',
            '.webm': 'audio/webm',
            '.flac': 'audio/flac'
        }
        mime_type = mime_type_map.get(file_ext, 'audio/wav')
        
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

        INITIAL DECEPTION FLAGS DETECTED:
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
        - Compare current vocal patterns with previous recordings in this session
        - Look for consistency/inconsistency patterns across the conversation  
        - Note any escalation or de-escalation in vocal stress indicators
        - Consider if the speaker's voice is becoming more or less authentic over time
        - Identify if vocal patterns support or contradict previous statements
        """
            base_prompt += context_prompt

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

        gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [
                    {"text": full_prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": audio_base64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 4096  # Increased for detailed audio analysis
            }
        }

        logger.info(f"Sending audio analysis request to Gemini with {len(audio_data)} bytes of audio data")
        response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            gemini_response = response.json()
            logger.info(f"Gemini audio analysis response received")
            
            if 'candidates' not in gemini_response or not gemini_response['candidates']:
                return {"error": "No candidates in Gemini response", "gemini_raw_response": gemini_response}

            candidate = gemini_response['candidates'][0]
            if 'content' not in candidate or 'parts' not in candidate['content'] or not candidate['content']['parts']:
                return {"error": "Invalid content structure in Gemini candidate", "gemini_raw_response": gemini_response}

            text = candidate['content']['parts'][0].get('text', '')

            if text.strip().startswith('```json'):
                text = text.strip()[7:-3].strip()
            elif text.strip().startswith('```'):
                text = text.strip()[3:-3].strip()

            try:
                result = json.loads(text)
                logger.info("Successfully parsed Gemini audio analysis response")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini JSON response: {str(e)}. Raw text: {text[:500]}...")
                return {"error": f"Failed to parse Gemini JSON response: {str(e)}", "gemini_text": text}
        else:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return {"error": f"Gemini API error: {response.status_code} - {response.text}"}
            
    except Exception as e:
        logger.error(f"Exception in query_gemini_with_audio: {str(e)}", exc_info=True)
        return {"error": f"Gemini audio analysis error: {str(e)}"}


def query_gemini(transcript: str, flags: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSyB5KbPaVXPYkUeShTEE82fgpZiLiLl7YyM": # Check against placeholder
        logger.error("Missing or placeholder Gemini API key. Cannot query Gemini.")
        return {"error": "Missing or placeholder Gemini API key"}

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
    - Identify if they are reinforcing previous statements or contradicting them    """
        base_prompt += context_prompt

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
    gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 3072
        }
    }

    try:
        response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            gemini_response = response.json()
            logger.info(f"Gemini API response structure: {json.dumps(gemini_response, indent=2)[:500]}...")

            if 'candidates' not in gemini_response or not gemini_response['candidates']:
                return {"error": "No candidates in Gemini response", "gemini_raw_response": gemini_response}

            candidate = gemini_response['candidates'][0]
            if 'content' not in candidate or 'parts' not in candidate['content'] or not candidate['content']['parts']:
                return {"error": "Invalid content structure in Gemini candidate", "gemini_raw_response": gemini_response}

            text = candidate['content']['parts'][0].get('text', '')

            if text.strip().startswith('```json'):
                text = text.strip()[7:-3].strip() # Remove ```json ... ```
            elif text.strip().startswith('```'):
                 text = text.strip()[3:-3].strip() # Remove ``` ... ```

            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini JSON response: {str(e)}. Raw text: {text[:500]}...")
                return {"error": f"Failed to parse Gemini JSON response: {str(e)}", "gemini_text": text}
        else:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return {"error": f"Gemini API error: {response.status_code} - {response.text}"}
    except Exception as e:
        logger.error(f"Exception in query_gemini: {str(e)}", exc_info=True)
        return {"error": f"Gemini request error: {str(e)}"}

def validate_and_structure_gemini_response(raw_response: Dict[str, Any], transcript: str, quantitative_linguistic: Dict[str, Any] = None) -> Dict[str, Any]:
    # Import here to avoid circular import
    from services.linguistic_service import get_default_linguistic_analysis
    
    # Use quantitative linguistic analysis if provided, otherwise get default
    default_linguistic = quantitative_linguistic if quantitative_linguistic else get_default_linguistic_analysis()
    
    default_structure = {
        "speaker_transcripts": {"Speaker 1": transcript},
        "red_flags_per_speaker": {"Speaker 1": []},
        "credibility_score": 50,
        "confidence_level": "medium",
        "gemini_summary": {
            "tone": "Analysis pending - technical issue encountered",
            "motivation": "Unable to determine - requires manual review",
            "credibility": "Inconclusive - technical analysis limitation",
            "emotional_state": "Analysis incomplete",
            "communication_style": "Requires further analysis",
            "key_concerns": "Technical analysis limitation",
            "strengths": "Unable to assess automatically"
        },
        "recommendations": [
            "Manual review recommended due to technical analysis limitations",
            "Consider re-running analysis with different audio quality"
        ],
        "linguistic_analysis": default_linguistic,
        "risk_assessment": {
            "overall_risk": "medium",
            "risk_factors": ["Technical analysis limitation"],
            "mitigation_suggestions": ["Manual review recommended"]
        },
        "manipulation_assessment": {
            "manipulation_score": 0,
            "manipulation_tactics": [],
            "manipulation_explanation": "N/A",
            "example_phrases": []
        },
        "argument_analysis": {
            "argument_strengths": [],
            "argument_weaknesses": [],
            "overall_argument_coherence_score": 0
        },
        "speaker_attitude": {
            "respect_level_score": 50,
            "sarcasm_detected": False,
            "sarcasm_confidence_score": 0,
            "tone_indicators_respect_sarcasm": []
        },
        "enhanced_understanding": {
            "key_inconsistencies": [],
            "areas_of_evasiveness": [],
            "suggested_follow_up_questions": [],
            "unverified_claims": []
        }
    }

    if not isinstance(raw_response, dict) or raw_response.get('error'):
        logger.warning(f"Gemini API error or invalid raw_response, using default structure. Error: {raw_response.get('error') if isinstance(raw_response, dict) else 'Invalid type'}")
        # Ensure all fields, including new ones, are present in the returned default structure
        # by copying the comprehensive default_structure.
        # This is important if raw_response is completely unusable (e.g., not a dict or error reported).
        complete_default = default_structure.copy()
        if quantitative_linguistic: # Ensure linguistic_analysis is updated if it was passed in
            complete_default["linguistic_analysis"] = quantitative_linguistic
        else: # Otherwise, ensure it's a fresh default if not passed (though get_default_linguistic_analysis handles this)
            complete_default["linguistic_analysis"] = get_default_linguistic_analysis()

        # Speaker transcripts should still be based on the input transcript
        complete_default["speaker_transcripts"] = {"Speaker 1": transcript}
        return complete_default


    validated_response = {}
    required_top_level_fields = [
        'speaker_transcripts', 'red_flags_per_speaker', 'credibility_score',
        'confidence_level', 'gemini_summary', 'recommendations',
        'linguistic_analysis', 'risk_assessment',
        'manipulation_assessment', 'argument_analysis',
        'speaker_attitude', 'enhanced_understanding'
    ]

    for field in required_top_level_fields:
        validated_response[field] = raw_response.get(field, default_structure[field])
        if field not in raw_response: # Log if top-level field was missing and defaulted
            logger.warning(f"Missing top-level field '{field}' in Gemini response, using default structure for it.")
        # Ensure nested structures are at least dictionaries if they are supposed to be
        elif isinstance(default_structure.get(field), dict) and not isinstance(validated_response[field], dict):
            logger.warning(f"Field '{field}' in Gemini response was not a dictionary as expected, using default structure for it.")
            validated_response[field] = default_structure[field]


    # Validate and normalize credibility_score
    try:
        score = int(validated_response.get('credibility_score', default_structure['credibility_score']))
        validated_response['credibility_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning(f"Invalid credibility_score '{validated_response.get('credibility_score')}', defaulting.")
        validated_response['credibility_score'] = default_structure['credibility_score']

    # Validate confidence_level
    valid_confidence_levels = ["very_low", "low", "medium", "high", "very_high"]
    if validated_response.get('confidence_level') not in valid_confidence_levels:
        logger.warning(f"Invalid confidence_level '{validated_response.get('confidence_level')}', defaulting.")
        validated_response['confidence_level'] = default_structure['confidence_level']

    # Generic helper to validate list of strings
    def validate_list_of_strings(parent_dict, key, default_list):
        val = parent_dict.get(key, default_list)
        if not isinstance(val, list):
            logger.warning(f"Invalid type for '{key}', expected list, got {type(val)}. Defaulting.")
            parent_dict[key] = default_list
            return
        parent_dict[key] = [str(item) if not isinstance(item, str) else item for item in val]

    # Validate and fix gemini_summary
    gemini_summary_data = validated_response.get('gemini_summary', default_structure['gemini_summary'])
    if not isinstance(gemini_summary_data, dict): # Ensure it's a dict
        gemini_summary_data = default_structure['gemini_summary']
    validated_response['gemini_summary'] = gemini_summary_data
    for key, default_val in default_structure['gemini_summary'].items():
        val = gemini_summary_data.get(key, default_val)
        if isinstance(default_val, str) and not isinstance(val, str):
             # Convert lists to strings if needed (common issue with Gemini responses for string fields)
            if isinstance(val, list):
                gemini_summary_data[key] = '; '.join(str(item) for item in val)
                logger.info(f"Converted list to string for gemini_summary.{key}: {val}")
            else:
                 gemini_summary_data[key] = str(val)
        elif not val: # if empty string, list or other falsey value for a normally non-empty field.
            gemini_summary_data[key] = default_val


    # Validate linguistic_analysis (already somewhat handled by its source)
    linguistic_analysis_data = validated_response.get('linguistic_analysis', default_structure['linguistic_analysis'])
    if not isinstance(linguistic_analysis_data, dict):
        linguistic_analysis_data = default_structure['linguistic_analysis']
    validated_response['linguistic_analysis'] = linguistic_analysis_data
    for key, default_val in default_structure['linguistic_analysis'].items():
        if key not in linguistic_analysis_data or linguistic_analysis_data[key] is None: # Check for None explicitly for numeric fields
             linguistic_analysis_data[key] = default_val


    # Validate risk_assessment
    risk_assessment_data = validated_response.get('risk_assessment', default_structure['risk_assessment'])
    if not isinstance(risk_assessment_data, dict): # Ensure it's a dict
        risk_assessment_data = default_structure['risk_assessment']
    validated_response['risk_assessment'] = risk_assessment_data
    for key, default_val in default_structure['risk_assessment'].items():
        if key == 'overall_risk':
            if risk_assessment_data.get(key) not in ["low", "medium", "high"]:
                logger.warning(f"Invalid overall_risk '{risk_assessment_data.get(key)}', defaulting.")
                risk_assessment_data[key] = default_structure['risk_assessment']['overall_risk']
        elif isinstance(default_val, list):
            validate_list_of_strings(risk_assessment_data, key, default_val)
        elif not risk_assessment_data.get(key):
            risk_assessment_data[key] = default_val

    # Validate recommendations (list of strings)
    validate_list_of_strings(validated_response, 'recommendations', default_structure['recommendations'])


    # --- Start Validation for New Fields ---

    # ManipulationAssessment
    manip_assess_data = validated_response.get('manipulation_assessment', default_structure['manipulation_assessment'])
    if not isinstance(manip_assess_data, dict): manip_assess_data = default_structure['manipulation_assessment'] # Ensure dict
    validated_response['manipulation_assessment'] = manip_assess_data
    try:
        score = int(manip_assess_data.get('manipulation_score', default_structure['manipulation_assessment']['manipulation_score']))
        manip_assess_data['manipulation_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid manipulation_score, defaulting.")
        manip_assess_data['manipulation_score'] = default_structure['manipulation_assessment']['manipulation_score']
    validate_list_of_strings(manip_assess_data, 'manipulation_tactics', default_structure['manipulation_assessment']['manipulation_tactics'])
    manip_assess_data['manipulation_explanation'] = str(manip_assess_data.get('manipulation_explanation', default_structure['manipulation_assessment']['manipulation_explanation']) or default_structure['manipulation_assessment']['manipulation_explanation'])
    validate_list_of_strings(manip_assess_data, 'example_phrases', default_structure['manipulation_assessment']['example_phrases'])

    # ArgumentAnalysis
    arg_analysis_data = validated_response.get('argument_analysis', default_structure['argument_analysis'])
    if not isinstance(arg_analysis_data, dict): arg_analysis_data = default_structure['argument_analysis']
    validated_response['argument_analysis'] = arg_analysis_data
    validate_list_of_strings(arg_analysis_data, 'argument_strengths', default_structure['argument_analysis']['argument_strengths'])
    validate_list_of_strings(arg_analysis_data, 'argument_weaknesses', default_structure['argument_analysis']['argument_weaknesses'])
    try:
        score = int(arg_analysis_data.get('overall_argument_coherence_score', default_structure['argument_analysis']['overall_argument_coherence_score']))
        arg_analysis_data['overall_argument_coherence_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid overall_argument_coherence_score, defaulting.")
        arg_analysis_data['overall_argument_coherence_score'] = default_structure['argument_analysis']['overall_argument_coherence_score']

    # SpeakerAttitude
    speaker_attitude_data = validated_response.get('speaker_attitude', default_structure['speaker_attitude'])
    if not isinstance(speaker_attitude_data, dict): speaker_attitude_data = default_structure['speaker_attitude']
    validated_response['speaker_attitude'] = speaker_attitude_data
    try:
        score = int(speaker_attitude_data.get('respect_level_score', default_structure['speaker_attitude']['respect_level_score']))
        speaker_attitude_data['respect_level_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid respect_level_score, defaulting.")
        speaker_attitude_data['respect_level_score'] = default_structure['speaker_attitude']['respect_level_score']

    sarcasm_detected_val = speaker_attitude_data.get('sarcasm_detected', default_structure['speaker_attitude']['sarcasm_detected'])
    if not isinstance(sarcasm_detected_val, bool):
        logger.warning(f"Invalid sarcasm_detected type, defaulting. Got: {sarcasm_detected_val}")
        speaker_attitude_data['sarcasm_detected'] = default_structure['speaker_attitude']['sarcasm_detected']
    else:
        speaker_attitude_data['sarcasm_detected'] = sarcasm_detected_val

    try:
        score = int(speaker_attitude_data.get('sarcasm_confidence_score', default_structure['speaker_attitude']['sarcasm_confidence_score']))
        speaker_attitude_data['sarcasm_confidence_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid sarcasm_confidence_score, defaulting.")
        speaker_attitude_data['sarcasm_confidence_score'] = default_structure['speaker_attitude']['sarcasm_confidence_score']
    validate_list_of_strings(speaker_attitude_data, 'tone_indicators_respect_sarcasm', default_structure['speaker_attitude']['tone_indicators_respect_sarcasm'])

    # EnhancedUnderstanding
    enhanced_und_data = validated_response.get('enhanced_understanding', default_structure['enhanced_understanding'])
    if not isinstance(enhanced_und_data, dict): enhanced_und_data = default_structure['enhanced_understanding']
    validated_response['enhanced_understanding'] = enhanced_und_data
    validate_list_of_strings(enhanced_und_data, 'key_inconsistencies', default_structure['enhanced_understanding']['key_inconsistencies'])
    validate_list_of_strings(enhanced_und_data, 'areas_of_evasiveness', default_structure['enhanced_understanding']['areas_of_evasiveness'])
    validate_list_of_strings(enhanced_und_data, 'suggested_follow_up_questions', default_structure['enhanced_understanding']['suggested_follow_up_questions'])
    validate_list_of_strings(enhanced_und_data, 'unverified_claims', default_structure['enhanced_understanding']['unverified_claims'])

    # --- End Validation for New Fields ---

    return validated_response
