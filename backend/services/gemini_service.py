import json
import requests
import logging
from typing import Dict, Any, Optional

from backend.config import GEMINI_API_KEY
# To avoid circular dependency if gemini_service needs session_context,
# it's better if session_service.conversation_history_service is passed as an argument
# to functions needing it, rather than direct import here if session_service might import gemini_service.
# For now, assuming get_session_context will be passed if needed.

logger = logging.getLogger(__name__)

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
        }
    }

    CRITICAL REQUIREMENTS:
    - Return ONLY valid JSON, no markdown formatting, no ```json blocks
    - All string values must be meaningful, not placeholder text
    - credibility_score must be integer 0-100
    - confidence_level must be: "very_low", "low", "medium", "high", "very_high"
    - overall_risk must be: "low", "medium", "high"
    - All arrays must contain at least 1 meaningful item
    - All object fields must be present and non-empty
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

def validate_and_structure_gemini_response(raw_response: Dict[str, Any], transcript: str) -> Dict[str, Any]:
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
        "linguistic_analysis": {
            "speech_patterns": "Analysis incomplete",
            "word_choice": "Requires manual review",
            "emotional_consistency": "Unable to assess",
            "detail_level": "Analysis pending"
        },
        "risk_assessment": {
            "overall_risk": "medium",
            "risk_factors": ["Technical analysis limitation"],
            "mitigation_suggestions": ["Manual review recommended"]
        }
    }

    if not isinstance(raw_response, dict) or raw_response.get('error'):
        logger.warning(f"Gemini API error or invalid raw_response, using default structure. Error: {raw_response.get('error') if isinstance(raw_response, dict) else 'Invalid type'}")
        return default_structure

    validated_response = {}
    required_top_level_fields = ['speaker_transcripts', 'red_flags_per_speaker', 'credibility_score',
                                 'confidence_level', 'gemini_summary', 'recommendations',
                                 'linguistic_analysis', 'risk_assessment']

    for field in required_top_level_fields:
        validated_response[field] = raw_response.get(field, default_structure[field])
        if field not in raw_response:
            logger.warning(f"Missing field '{field}' in Gemini response, using default.")

    try:
        score = int(validated_response['credibility_score'])
        validated_response['credibility_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning(f"Invalid credibility_score '{validated_response['credibility_score']}', defaulting to 50.")
        validated_response['credibility_score'] = default_structure['credibility_score']

    valid_confidence_levels = ["very_low", "low", "medium", "high", "very_high"]
    if validated_response.get('confidence_level') not in valid_confidence_levels:
        logger.warning(f"Invalid confidence_level '{validated_response.get('confidence_level')}', defaulting to medium.")
        validated_response['confidence_level'] = default_structure['confidence_level']

    required_summary_fields = default_structure['gemini_summary'].keys()
    if not isinstance(validated_response.get('gemini_summary'), dict):
        validated_response['gemini_summary'] = default_structure['gemini_summary']
    else:
        for summary_field in required_summary_fields:
            if summary_field not in validated_response['gemini_summary'] or not validated_response['gemini_summary'][summary_field]:
                validated_response['gemini_summary'][summary_field] = default_structure['gemini_summary'][summary_field]

    required_linguistic_fields = default_structure['linguistic_analysis'].keys()
    if not isinstance(validated_response.get('linguistic_analysis'), dict):
        validated_response['linguistic_analysis'] = default_structure['linguistic_analysis']
    else:
        for linguistic_field in required_linguistic_fields:
            if linguistic_field not in validated_response['linguistic_analysis'] or not validated_response['linguistic_analysis'][linguistic_field]:
                validated_response['linguistic_analysis'][linguistic_field] = default_structure['linguistic_analysis'][linguistic_field]

    required_risk_fields = default_structure['risk_assessment'].keys()
    if not isinstance(validated_response.get('risk_assessment'), dict):
        validated_response['risk_assessment'] = default_structure['risk_assessment']
    else:
        for risk_field in required_risk_fields:
            if risk_field not in validated_response['risk_assessment'] or not validated_response['risk_assessment'][risk_field]:
                validated_response['risk_assessment'][risk_field] = default_structure['risk_assessment'][risk_field]
        valid_risk_levels = ["low", "medium", "high"]
        if validated_response['risk_assessment'].get('overall_risk') not in valid_risk_levels:
            validated_response['risk_assessment']['overall_risk'] = default_structure['risk_assessment']['overall_risk']

    if not isinstance(validated_response.get('recommendations'), list) or not validated_response['recommendations']:
        validated_response['recommendations'] = default_structure['recommendations']

    # The 'session_insights' field is dynamic based on context, so it's not in default_structure.
    # It will be added by the calling function in analysis_routes if session_context exists.
    # Or, if Gemini is expected to return it, it should be part of the prompt and default_structure.
    # For now, it's handled in the /analyze route.

    return validated_response
