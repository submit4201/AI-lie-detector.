from fastapi import FastAPI, File, UploadFile, HTTPException
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Lie Detector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)
gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyB5KbPaVXPYkUeShTEE82fgpZiLiLl7YyM")  # fallback key

def query_gemini(transcript, flags):
    if not gemini_api_key:
        return {"error": "Missing Gemini API key"}

    prompt = f"""
    Analyze the transcript for deception, stress, and speaker separation. Transcript:
    {transcript}

    Red flags from primary analysis:
    {json.dumps(flags, indent=2)}

    Return a JSON with:
    - speaker_transcripts: separated text per speaker
    - red_flags_per_speaker: breakdown of language indicators
    - credibility_score (0-100)
    - gemini_summary: insights into tone, motivation, and credibility
    - recommendation: advice for next steps (follow-up questions, clarify, etc)
    """

    # Correct Gemini API URL and authentication
    gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 2048
        }
    }   
    response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        gemini_response = response.json()
        try:
            text = gemini_response['candidates'][0]['content']['parts'][0]['text']
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
            
            return json.loads(text)
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse Gemini JSON response: {str(e)}",
                "gemini_raw_response": gemini_response
            }
        except Exception as e:
            return {
                "error": f"Gemini response processing error: {str(e)}",
                "gemini_raw_response": gemini_response
            }
    else:
        return {"error": f"Gemini API error: {response.status_code} - {response.text}"}

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
    
    # Calculate quality score based on various factors
    score = 100
    
    # Duration check
    if quality_metrics["duration"] < 1:
        score -= 30  # Too short
    elif quality_metrics["duration"] > 300:
        score -= 10  # Very long might have noise
    
    # Sample rate check
    if quality_metrics["sample_rate"] < 16000:
        score -= 20  # Low quality
    elif quality_metrics["sample_rate"] >= 44100:
        score += 10  # High quality
    
    # Loudness check
    if quality_metrics["loudness"] < -30:
        score -= 25  # Too quiet
    elif quality_metrics["loudness"] > -10:
        score -= 15  # Too loud, might be clipped
    
    quality_metrics["quality_score"] = max(0, min(100, score))
    return quality_metrics

# Enhanced deception detection with confidence scoring
def advanced_deception_analysis(transcript, emotion_results):
    """Enhanced deception analysis with confidence scoring"""
    analysis_results = {
        "flags": [],
        "confidence_scores": {},
        "linguistic_patterns": {},
        "overall_risk": "low"
    }
    
    transcript_lower = transcript.lower()
    word_count = len(transcript.split())
    
    # Pattern categories with confidence weights
    patterns = {
        "overcompensation": {
            "phrases": [
                "honestly", "trust me", "i swear", "to be honest", "believe me",
                "i'm telling the truth", "on my mother's grave", "hand to god",
                "cross my heart", "i promise you", "you have to believe me",
                "i would never lie", "why would i lie", "do i look like a liar"
            ],
            "weight": 0.8
        },
        "evasive_language": {
            "phrases": [
                "i don't remember", "i can't recall", "i think", "i believe",
                "as far as i know", "to the best of my knowledge", "i'm not sure",
                "maybe", "possibly", "i guess", "sort of", "kind of"
            ],
            "weight": 0.6
        },
        "distancing": {
            "phrases": [
                "that person", "this individual", "someone", "they",
                "it wasn't me", "i wasn't there", "i had nothing to do with"
            ],
            "weight": 0.7
        },
        "deflection": {
            "phrases": [
                "why are you asking", "that's a strange question",
                "what do you mean", "i don't understand", "what's this about",
                "are you accusing me", "this is ridiculous"
            ],
            "weight": 0.9
        }
    }
    
    # Analyze each pattern category
    for category, data in patterns.items():
        matches = []
        confidence = 0
        
        for phrase in data["phrases"]:
            if phrase in transcript_lower:
                matches.append(phrase)
                confidence += data["weight"]
        
        if matches:
            analysis_results["flags"].append(f"{category.title()} detected: {', '.join(matches)}")
            analysis_results["confidence_scores"][category] = min(100, confidence * 20)
            analysis_results["linguistic_patterns"][category] = matches
    
    # Response length analysis
    if word_count > 100:
        analysis_results["flags"].append("Excessive detail - potential fabrication")
        analysis_results["confidence_scores"]["excessive_detail"] = 70
    elif word_count < 5:
        analysis_results["flags"].append("Very brief response - possible evasion")
        analysis_results["confidence_scores"]["brevity"] = 60
    
    # Word repetition analysis
    words = transcript_lower.split()
    word_freq = {}
    for word in words:
        if len(word) > 2:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    repeated_words = [word for word, freq in word_freq.items() if freq > 2]
    if repeated_words:
        analysis_results["flags"].append(f"Repetition detected: {', '.join(repeated_words[:5])}")
        analysis_results["confidence_scores"]["repetition"] = min(80, len(repeated_words) * 15)
    
    # Emotional consistency check
    if emotion_results:
        dominant_emotions = [e for e in emotion_results[:3] if e['score'] > 0.3]
        if len(dominant_emotions) > 2:
            analysis_results["flags"].append("Mixed emotional signals detected")
            analysis_results["confidence_scores"]["emotional_inconsistency"] = 65
    
    # Calculate overall risk
    avg_confidence = sum(analysis_results["confidence_scores"].values()) / max(1, len(analysis_results["confidence_scores"]))
    if avg_confidence > 70:
        analysis_results["overall_risk"] = "high"
    elif avg_confidence > 40:
        analysis_results["overall_risk"] = "medium"
    
    return analysis_results

@app.post("/analyze")
async def analyze_audio(audio: UploadFile = File(...)):
    start_time = time.time()
    analysis_metadata = {
        "timestamp": datetime.now().isoformat(),
        "file_name": audio.filename,
        "file_size": 0
    }
    
    # Validate file
    if not audio.filename.lower().endswith(('.wav', '.mp3', '.ogg', '.m4a', '.webm')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload audio files only.")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        content = await audio.read()
        analysis_metadata["file_size"] = len(content)
        tmp_file.write(content)
        tmp_path = tmp_file.name

    try:
        logger.info(f"Processing audio file: {audio.filename}")
        
        # Load and process audio
        audio_segment = AudioSegment.from_file(tmp_path)
        audio_segment = audio_segment.set_channels(1).set_frame_rate(16000)
        audio_segment.export(tmp_path, format="wav")

        # Assess audio quality
        quality_metrics = assess_audio_quality(audio_segment)
        logger.info(f"Audio quality metrics: {quality_metrics}")
        
        # Check if audio quality is sufficient
        if quality_metrics["quality_score"] < 30:
            logger.warning("Low audio quality detected")

        # Speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)

        logger.info(f"Transcript generated: {len(transcript)} characters")

        # Emotion analysis
        emotion_results = emotion_classifier(transcript)
        
        # Enhanced deception analysis
        deception_analysis = advanced_deception_analysis(transcript, emotion_results)
        
        # Traditional flag extraction for backwards compatibility
        traditional_flags = deception_analysis["flags"]

        # Query Gemini for AI analysis
        gemini_result = query_gemini(transcript, traditional_flags)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Compile comprehensive results
        result = {
            "transcript": transcript,
            "emotion_analysis": emotion_results,
            "deception_flags": traditional_flags,
            "advanced_analysis": {
                "confidence_scores": deception_analysis["confidence_scores"],
                "linguistic_patterns": deception_analysis["linguistic_patterns"],
                "overall_risk": deception_analysis["overall_risk"]
            },
            "audio_quality": quality_metrics,
            "gemini_analysis": gemini_result,
            "metadata": {
                **analysis_metadata,
                "processing_time": round(processing_time, 2),
                "analysis_version": "2.0"
            }
        }
        if gemini_result.get("error"):  # Gemini API error or timeout?
            logger.error(f"Gemini analysis error: {gemini_result['error']}")
        else:  # Gemini analysis completed successfully
            logger.info(f"Analysis completed in {processing_time:.2f} seconds")
        return result

    except sr.UnknownValueError:
        logger.error("Speech recognition failed - could not understand audio")
        return {"error": "Could not understand audio. Please ensure clear speech and good audio quality."}
    except sr.RequestError as e:
        logger.error(f"Speech recognition service error: {e}")
        return {"error": f"Speech recognition service error: {e}"}
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        return {"error": f"Analysis failed: {str(e)}"}
    finally:
        # Clean up temporary file
        try:
            os.remove(tmp_path)
        except:
            pass

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "2.0"
    }

# API info endpoint
@app.get("/")
async def root():
    return {
        "name": "AI Lie Detector API",
        "version": "2.0",
        "description": "Advanced voice analysis with AI-powered deception detection",
        "endpoints": {
            "/analyze": "POST - Upload audio for analysis",
            "/health": "GET - Health check",
            "/": "GET - API information"
        }
    }