from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
import speech_recognition as sr
from transformers import pipeline
import tempfile
import os
import requests
import json
import logging
import time
from datetime import datetime
import uuid
from typing import Optional, Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Lie Detector API", version="1.0.0")

# Session management for conversation history
session_store: Dict[str, Dict] = {}

class ConversationHistory:
    def __init__(self):
        self.sessions = {}
    
    def get_or_create_session(self, session_id: str = None) -> str:
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now(),
                "history": [],
                "analysis_count": 0,
                "context": {}
            }
        
        return session_id
    
    def add_analysis(self, session_id: str, transcript: str, analysis_result: dict):
        if session_id not in self.sessions:
            self.get_or_create_session(session_id)
        
        session = self.sessions[session_id]
        session["analysis_count"] += 1
        session["history"].append({
            "timestamp": datetime.now(),
            "transcript": transcript,
            "analysis": analysis_result,
            "analysis_number": session["analysis_count"]
        })
        
        # Keep only last 10 analyses to prevent memory bloat
        if len(session["history"]) > 10:
            session["history"] = session["history"][-10:]
    
    def get_session_context(self, session_id: str) -> Dict:
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        return {
            "previous_analyses": len(session["history"]),
            "session_duration": (datetime.now() - session["created_at"]).total_seconds() / 60,  # minutes
            "recent_transcripts": [h["transcript"] for h in session["history"][-3:]],  # Last 3
            "recent_patterns": self._extract_patterns(session["history"][-5:])  # Last 5
        }
    
    def _extract_patterns(self, history: List[Dict]) -> Dict:
        patterns = {
            "recurring_deception_flags": {},
            "emotion_trends": {},
            "credibility_trend": []
        }
        
        for entry in history:
            analysis = entry.get("analysis", {})
            
            # Track recurring deception flags
            flags = analysis.get("deception_flags", [])
            for flag in flags:
                flag_type = flag.split(":")[0] if ":" in flag else flag
                patterns["recurring_deception_flags"][flag_type] = patterns["recurring_deception_flags"].get(flag_type, 0) + 1
            
            # Track emotion trends
            emotions = analysis.get("emotion_analysis", [])
            if emotions and isinstance(emotions, list) and len(emotions) > 0:
                emotion_data = emotions[0] if isinstance(emotions[0], list) else emotions
                if emotion_data:
                    top_emotion = max(emotion_data, key=lambda x: x.get("score", 0))
                    emotion_name = top_emotion.get("label", "unknown")
                    patterns["emotion_trends"][emotion_name] = patterns["emotion_trends"].get(emotion_name, 0) + 1
            
            # Track credibility scores
            gemini_analysis = analysis.get("gemini_analysis", {})
            if isinstance(gemini_analysis, dict) and "credibility_score" in gemini_analysis:
                patterns["credibility_trend"].append(gemini_analysis["credibility_score"])
        
        return patterns

# Global conversation history manager
conversation_history = ConversationHistory()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=7, return_all_scores=True)
gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyB5KbPaVXPYkUeShTEE82fgpZiLiLl7YyM")  # fallback key

def query_gemini(transcript, flags, session_id: str = None):
    if not gemini_api_key:
        return {"error": "Missing Gemini API key"}

    # Get session context for conversation continuity
    session_context = conversation_history.get_session_context(session_id) if session_id else {}
    
    # Build enhanced prompt with conversation history
    base_prompt = f"""
    Analyze the transcript for deception, stress, and speaker separation. 

    CURRENT TRANSCRIPT:
    {transcript}

    RED FLAGS FROM PRIMARY ANALYSIS:
    {json.dumps(flags, indent=2)}
    """
    
    # Add conversation context if available
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
    """# Correct Gemini API URL and authentication
    gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 3072  # Increased for more detailed contextual analysis
        }
    }
    try:
        response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            gemini_response = response.json()
            logger.info(f"Gemini API response structure: {json.dumps(gemini_response, indent=2)[:500]}...")
            
            # Safely navigate the response structure
            if 'candidates' not in gemini_response:
                return {"error": "No candidates in Gemini response", "gemini_raw_response": gemini_response}
            
            candidates = gemini_response['candidates']
            if not isinstance(candidates, list) or len(candidates) == 0:
                return {"error": "Invalid candidates structure in Gemini response", "gemini_raw_response": gemini_response}
            
            candidate = candidates[0]
            if 'content' not in candidate:
                return {"error": "No content in Gemini candidate", "gemini_raw_response": gemini_response}
            
            content = candidate['content']
            if 'parts' not in content:
                return {"error": "No parts in Gemini content", "gemini_raw_response": gemini_response}
            
            parts = content['parts']
            if not isinstance(parts, list) or len(parts) == 0:
                return {"error": "Invalid parts structure in Gemini content", "gemini_raw_response": gemini_response}
            
            part = parts[0]
            if 'text' not in part:
                return {"error": "No text in Gemini part", "gemini_raw_response": gemini_response}
            
            text = part['text']
            
            # Remove markdown code block formatting if present
            if text.strip().startswith('```json'):
                text = text.strip()
                # Find the JSON content between ```json and ```
                start = text.find('```json') + 7
                end = text.rfind('```')
                if end > start:
                    text = text[start:end].strip()
            elif text.strip().startswith('```'):
                text = text.strip()
                # Handle generic code blocks
                start = text.find('```') + 3
                end = text.rfind('```')
                if end > start:
                    text = text[start:end].strip()
            
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                return {
                    "error": f"Failed to parse Gemini JSON response: {str(e)}",
                    "gemini_text": text,
                    "gemini_raw_response": gemini_response
                }
        else:
            return {"error": f"Gemini API error: {response.status_code} - {response.text}"}
    except Exception as e:
        logger.error(f"Exception in query_gemini: {str(e)}")
        return {"error": f"Gemini request error: {str(e)}"}

def validate_and_structure_gemini_response(raw_response, transcript, session_context=None):
    """
    Validate and ensure structured response from Gemini API with fallbacks
    """
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
    
    # If raw_response has an error, return structured default
    if isinstance(raw_response, dict) and raw_response.get('error'):
        logger.warning(f"Gemini API error, using default structure: {raw_response.get('error')}")
        return default_structure
    
    # Validate required top-level fields
    required_fields = ['speaker_transcripts', 'red_flags_per_speaker', 'credibility_score', 
                      'gemini_summary', 'recommendations', 'linguistic_analysis', 'risk_assessment']
    
    validated_response = {}
    
    for field in required_fields:
        if field in raw_response:
            validated_response[field] = raw_response[field]
        else:
            validated_response[field] = default_structure[field]
            logger.warning(f"Missing field '{field}' in Gemini response, using default")
    
    # Validate and fix credibility_score
    try:
        score = int(validated_response['credibility_score'])
        validated_response['credibility_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        validated_response['credibility_score'] = 50
        logger.warning("Invalid credibility_score, defaulting to 50")
    
    # Validate confidence_level
    valid_confidence_levels = ["very_low", "low", "medium", "high", "very_high"]
    if validated_response.get('confidence_level') not in valid_confidence_levels:
        validated_response['confidence_level'] = "medium"
    
    # Validate gemini_summary structure
    required_summary_fields = ['tone', 'motivation', 'credibility', 'emotional_state', 
                              'communication_style', 'key_concerns', 'strengths']
    
    if not isinstance(validated_response['gemini_summary'], dict):
        validated_response['gemini_summary'] = default_structure['gemini_summary']
    else:
        for summary_field in required_summary_fields:
            if summary_field not in validated_response['gemini_summary'] or not validated_response['gemini_summary'][summary_field]:
                validated_response['gemini_summary'][summary_field] = default_structure['gemini_summary'][summary_field]
    
    # Validate risk_assessment
    if not isinstance(validated_response['risk_assessment'], dict):
        validated_response['risk_assessment'] = default_structure['risk_assessment']
    else:
        valid_risk_levels = ["low", "medium", "high"]
        if validated_response['risk_assessment'].get('overall_risk') not in valid_risk_levels:
            validated_response['risk_assessment']['overall_risk'] = "medium"
        
        if not isinstance(validated_response['risk_assessment'].get('risk_factors'), list):
            validated_response['risk_assessment']['risk_factors'] = default_structure['risk_assessment']['risk_factors']
        
        if not isinstance(validated_response['risk_assessment'].get('mitigation_suggestions'), list):
            validated_response['risk_assessment']['mitigation_suggestions'] = default_structure['risk_assessment']['mitigation_suggestions']
    
    # Ensure arrays are not empty
    if not isinstance(validated_response['recommendations'], list) or len(validated_response['recommendations']) == 0:
        validated_response['recommendations'] = default_structure['recommendations']
    
    # Add session insights if session context is available
    if session_context and len(session_context.get('previous_analyses', [])) > 0:
        validated_response['session_insights'] = raw_response.get('session_insights', {
            "consistency_analysis": "Multiple analyses available for comparison",
            "behavioral_evolution": "Tracking patterns across conversation",
            "risk_trajectory": "Monitoring risk changes over time",
            "conversation_dynamics": "Analyzing ongoing conversation patterns"
        })
    
    return validated_response

# Audio quality assessment function
def assess_audio_quality(audio_segment):
    """Assess the quality of the audio for better analysis"""
    quality_metrics = {
        "duration": len(audio_segment) / 1000.0,  # seconds
        "sample_rate": audio_segment.frame_rate,
        "channels": audio_segment.channels,
        "loudness": audio_segment.dBFS,
        "quality_score": 0
    }
    
    # Calculate quality score
    if quality_metrics["duration"] >= 1.0:  # At least 1 second
        quality_metrics["quality_score"] += 25
    if quality_metrics["sample_rate"] >= 16000:  # Good sample rate
        quality_metrics["quality_score"] += 25
    if quality_metrics["loudness"] > -30:  # Not too quiet
        quality_metrics["quality_score"] += 25
    if quality_metrics["channels"] >= 1:  # Has audio channels
        quality_metrics["quality_score"] += 25
    
    return quality_metrics

# Main analyze endpoint
@app.post("/analyze")
async def analyze_audio(audio: UploadFile = File(...), session_id: Optional[str] = Form(None)):
    """Main endpoint for audio analysis with structured output validation"""
    try:
        logger.info(f"Starting analysis for session: {session_id}")
        
        # Validate file type
        if not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Get or create session
        if not session_id:
            session_id = conversation_history.get_or_create_session()
        else:
            conversation_history.get_or_create_session(session_id)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            audio_content = await audio.read()
            temp_audio.write(audio_content)
            temp_audio_path = temp_audio.name

        try:
            # Convert audio to a standard format using pydub
            audio_segment = AudioSegment.from_file(temp_audio_path)
            
            # Assess audio quality
            audio_quality = assess_audio_quality(audio_segment)
            logger.info(f"Audio quality metrics: {audio_quality}")
            
            # Convert to WAV for speech recognition
            wav_path = temp_audio_path.replace('.wav', '_converted.wav')
            audio_segment.export(wav_path, format="wav")
            
            # Speech recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                try:
                    transcript = recognizer.recognize_google(audio_data)
                    logger.info(f"Transcript: {transcript}")
                except sr.UnknownValueError:
                    return {"error": "Could not understand the audio. Please ensure clear speech and good audio quality."}
                except sr.RequestError as e:
                    return {"error": f"Speech recognition service error: {e}"}

            if not transcript or len(transcript.strip()) < 10:
                return {"error": "Transcript too short or empty. Please provide longer audio with clear speech."}

            # Emotion analysis
            try:
                emotions = emotion_classifier(transcript)
                if isinstance(emotions, list) and len(emotions) > 0:
                    emotion_scores = emotions[0] if isinstance(emotions[0], list) else emotions
                else:
                    emotion_scores = [{"label": "neutral", "score": 0.5}]
            except Exception as e:
                logger.warning(f"Emotion analysis failed: {e}")
                emotion_scores = [{"label": "neutral", "score": 0.5}]

            # Get session context for Gemini analysis
            session_context = conversation_history.get_session_context(session_id)
            
            # Query Gemini for comprehensive analysis
            logger.info("Querying Gemini for analysis...")
            gemini_response = query_gemini(transcript, session_context)
            
            # Validate and structure the Gemini response
            validated_analysis = validate_and_structure_gemini_response(gemini_response, session_context)
            
            logger.info("Analysis completed successfully")

            # Prepare final response
            result = {
                "session_id": session_id,
                "transcript": transcript,
                "audio_quality": audio_quality,
                "emotion_analysis": emotion_scores,
                **validated_analysis  # Include all validated structured fields
            }

            # Add to conversation history
            conversation_history.add_analysis(session_id, transcript, result)
            
            return result

        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_audio_path)
                if 'wav_path' in locals():
                    os.unlink(wav_path)
            except OSError:
                pass

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analysis: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}"}

# Session management endpoints
@app.post("/session/new")
async def create_session():
    """Create a new conversation session"""
    session_id = conversation_history.get_or_create_session()
    return {"session_id": session_id, "message": "New session created"}

@app.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session"""
    try:
        history = conversation_history.get_session_history(session_id)
        return {"session_id": session_id, "history": history}
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/")
async def root():
    return {"message": "AI Lie Detector API is running", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)