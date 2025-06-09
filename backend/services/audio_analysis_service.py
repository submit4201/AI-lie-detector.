from backend.models import AudioAnalysis
from backend.services.gemini_service import GeminiService # Assuming GeminiService will be here or accessible
import json
import re
from typing import Optional

class AudioAnalysisService:
    def __init__(self, gemini_service: GeminiService = None):
        self.gemini_service = gemini_service if gemini_service else GeminiService()

    async def analyze(self, text: str, audio_file_path: Optional[str] = None) -> AudioAnalysis:
        if not text:
            return AudioAnalysis() # Return default if no text

        prompt = f'''Analyze the following transcript to infer audio characteristics.
Based *only* on the textual content, assess the likely:
1.  Speech Clarity Score (0.0 to 1.0): How clear does the speech seem? Consider factors like coherent sentences, well-formed words, vs. jumbled text or indications of mumbling.
2.  Background Noise Level (Low, Medium, High): Are there any textual cues suggesting background noise (e.g., mentions of sounds, interruptions described)? If no cues, assume Low.
3.  Speech Rate (WPM): Estimate words per minute. A typical conversational rate is 130-170 WPM. If the text seems rushed or very slow, adjust accordingly.
4.  Pauses and Fillers (count of different types): Identify and count textual representations of pauses (e.g., "...", long silences implied by context) and common fillers (e.g., "um", "uh", "er", "like", "you know").
5.  Intonation Patterns: Describe any inferred intonation patterns (e.g., monotonous, questioning, empathetic, agitated) based on punctuation, word choice, and emotional content in the text.
6.  Audio Quality Assessment: Overall assessment of the likely audio quality based on the inferred clarity, noise, etc.

Transcript:
"{text}"

Provide your analysis as a JSON object matching the structure of the AudioAnalysis model:
{{
  "speech_clarity_score": float (0.0-1.0),
  "background_noise_level": str ("Low", "Medium", "High"),
  "speech_rate_wpm": int,
  "pauses_and_fillers": {{ "type1": count, "type2": count }},
  "intonation_patterns": str,
  "audio_quality_assessment": str
}}
If specific details cannot be reliably inferred from the text, use appropriate defaults like 0.0, "Analysis not available", or empty dictionaries.
'''
        
        try:
            # This assumes GeminiService will have a method like this:
            # get_structured_response(prompt: str, response_model: BaseModel) -> Optional[BaseModel]
            # For now, let's assume it returns a dict that we then parse.
            raw_analysis = await self.gemini_service.query_gemini_for_raw_json(prompt) # Placeholder for actual method
            
            if raw_analysis:
                # Basic parsing and validation, should be more robust
                analysis_data = json.loads(raw_analysis)
                # Ensure all keys are present, falling back to defaults from the model if not
                return AudioAnalysis(
                    speech_clarity_score=analysis_data.get("speech_clarity_score", 0.0),
                    background_noise_level=analysis_data.get("background_noise_level", "Analysis not available"),
                    speech_rate_wpm=analysis_data.get("speech_rate_wpm", 0),
                    pauses_and_fillers=analysis_data.get("pauses_and_fillers", {}),
                    intonation_patterns=analysis_data.get("intonation_patterns", "Analysis not available"),
                    audio_quality_assessment=analysis_data.get("audio_quality_assessment", "Analysis not available")
                )
            else:
                # Fallback to text-based estimation if LLM fails or returns nothing
                return self._fallback_text_analysis(text)
        except Exception as e:
            print(f"Error during LLM audio analysis: {e}")
            # Fallback to text-based estimation in case of any error
            return self._fallback_text_analysis(text)

    def _fallback_text_analysis(self, text: str) -> AudioAnalysis:
        # Existing placeholder logic as a fallback
        clarity = 0.0
        noise = "Low"
        wpm = 0
        pauses_data = {}
        intonation = "Analysis not available (fallback)."
        quality = "Analysis not available (fallback)."

        if text:
            words = text.split()
            word_count = len(words)
            if word_count > 0:
                # Simplified WPM calculation (assuming average reading speed for estimation)
                estimated_duration_minutes = word_count / 150.0 
                wpm = int(word_count / estimated_duration_minutes) if estimated_duration_minutes > 0 else 0

            fillers = len(re.findall(r'\\b(um|uh|er|ah|like|you know)\\b', text, re.IGNORECASE))
            text_pauses = text.count("...") + text.count("---") # Simple textual pause markers
            pauses_data = {"fillers": fillers, "textual_pauses": text_pauses}
            
            if word_count > 100:
                clarity = 0.65
                quality = "Fair (fallback)"
            elif word_count > 20:
                clarity = 0.5
                quality = "Potentially Acceptable (fallback)"
            else:
                clarity = 0.3
                quality = "Likely Poor (fallback)"
        
        return AudioAnalysis(
            speech_clarity_score=clarity,
            background_noise_level=noise,
            speech_rate_wpm=wpm,
            pauses_and_fillers=pauses_data,
            intonation_patterns=intonation,
            audio_quality_assessment=quality
        )
