from backend.models import QuantitativeMetrics
from typing import List, Dict, Optional, Any
from backend.services.gemini_service import GeminiService # Assuming GeminiService will be here or accessible
import json

class QuantitativeMetricsService:
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini_service = gemini_service if gemini_service else GeminiService()

    async def analyze(self, text: str, speaker_diarization: Optional[List[Dict[str, Any]]] = None, sentiment_trend_data_input: Optional[List[Dict[str, float]]] = None) -> QuantitativeMetrics:
        if not text:
            return QuantitativeMetrics() # Return default if no text

        # Prepare context from speaker_diarization if available
        diarization_summary = "Speaker diarization not available."
        if speaker_diarization:
            try:
                diarization_summary = f"Speaker diarization data: {json.dumps(speaker_diarization)}"
            except TypeError:
                diarization_summary = "Speaker diarization data is not JSON serializable."
        
        sentiment_summary = "Sentiment trend data not available."
        if sentiment_trend_data_input:
            try:
                sentiment_summary = f"Sentiment trend data: {json.dumps(sentiment_trend_data_input)}"
            except TypeError:
                sentiment_summary = "Sentiment trend data is not JSON serializable."

        prompt = f"""Analyze the following transcript and associated data to determine quantitative communication metrics.
Transcript:
"{text}"

{diarization_summary}
{sentiment_summary}

Based on the provided information, calculate or infer the following:
1.  Talk-to-Listen Ratio (float): If multiple speakers are implied or detailed in diarization, estimate this. If only one speaker or unclear, default to 0.0 or a representative value if the context suggests a monologue.
2.  Speaker Turn Duration Average (float, in seconds): Average duration of speaker turns. If diarization is available, use it. Otherwise, estimate based on text structure if possible, or default to 0.0.
3.  Interruptions Count (int): Number of interruptions detected. This is hard to infer from text alone without clear markers. If diarization provides overlap information or text contains cues (e.g., "--"), estimate. Otherwise, default to 0.
4.  Sentiment Trend (List[Dict[str, float]]): If sentiment_trend_data_input is provided, use it. Otherwise, try to infer a basic trend (e.g., positive start, negative end) from the text, or default to an empty list. Example: [{{"time": 10.5, "sentiment": 0.7}}].
5.  Word Count (int): Total number of words in the transcript.
6.  Vocabulary Richness Score (float, e.g., Type-Token Ratio - TTR): Calculate TTR (unique words / total words).

Provide your analysis as a JSON object matching the structure of the QuantitativeMetrics model:
{{
  "talk_to_listen_ratio": float,
  "speaker_turn_duration_avg": float,
  "interruptions_count": int,
  "sentiment_trend": [],
  "word_count": int,
  "vocabulary_richness_score": float
}}
If specific details cannot be reliably inferred, use appropriate defaults like 0.0, 0, or empty lists.
"""
        
        try:
            # This assumes GeminiService will have a method like this:
            # query_gemini_for_raw_json(prompt: str) -> Optional[str]
            raw_analysis = await self.gemini_service.query_gemini_for_raw_json(prompt) 
            
            if raw_analysis:
                analysis_data = json.loads(raw_analysis)
                # Ensure all keys are present, falling back to defaults from the model if not
                return QuantitativeMetrics(
                    talk_to_listen_ratio=analysis_data.get("talk_to_listen_ratio", 0.0),
                    speaker_turn_duration_avg=analysis_data.get("speaker_turn_duration_avg", 0.0),
                    interruptions_count=analysis_data.get("interruptions_count", 0),
                    sentiment_trend=analysis_data.get("sentiment_trend", []),
                    word_count=analysis_data.get("word_count", len(text.split())), # Fallback for word_count
                    vocabulary_richness_score=analysis_data.get("vocabulary_richness_score", 0.0)
                )
            else:
                return self._fallback_text_analysis(text, speaker_diarization, sentiment_trend_data_input)
        except Exception as e:
            print(f"Error during LLM quantitative metrics analysis: {e}")
            return self._fallback_text_analysis(text, speaker_diarization, sentiment_trend_data_input)

    def _fallback_text_analysis(self, text: str, speaker_diarization: Optional[List[Dict[str, Any]]] = None, sentiment_trend_data_input: Optional[List[Dict[str, float]]] = None) -> QuantitativeMetrics:
        # Existing placeholder logic as a fallback
        word_count = len(text.split())
        talk_ratio = 0.0
        avg_turn_duration = 0.0
        interruptions = 0

        if speaker_diarization and len(speaker_diarization) > 0:
            total_duration = 0
            num_turns = len(speaker_diarization)
            # Basic speaker time calculation for a crude talk_ratio if multiple speakers
            speaker_times: Dict[str, float] = {}
            total_speech_time_diarized = 0.0

            for segment in speaker_diarization:
                start = segment.get('start_time')
                end = segment.get('end_time')
                speaker = segment.get('speaker_label', 'Unknown')
                if start is not None and end is not None:
                    duration = end - start
                    total_duration += duration
                    speaker_times[speaker] = speaker_times.get(speaker, 0.0) + duration
                    total_speech_time_diarized += duration
            
            avg_turn_duration = total_duration / num_turns if num_turns > 0 else 0.0
            if num_turns > 5: # Arbitrary
                interruptions = num_turns // 5 # Very simplistic

            if len(speaker_times) > 1 and total_speech_time_diarized > 0:
                # Example: ratio of time for the most dominant speaker to others
                # This is not a standard talk-to-listen ratio but a placeholder
                max_time = max(speaker_times.values()) if speaker_times else 0.0
                talk_ratio = round(max_time / total_speech_time_diarized, 2) if total_speech_time_diarized else 0.0
            elif len(speaker_times) == 1 and total_speech_time_diarized > 0:
                talk_ratio = 1.0 # Single speaker detected


        # Use provided sentiment trend or simulate if not
        simulated_sentiment_trend_data = sentiment_trend_data_input if sentiment_trend_data_input is not None else []
        if not simulated_sentiment_trend_data and word_count > 0:
            # Estimate duration based on average speaking rate (150 WPM)
            estimated_total_seconds = (word_count / 150.0) * 60
            if estimated_total_seconds > 0:
                simulated_sentiment_trend_data = [
                    {'time': round(0.2 * estimated_total_seconds, 1), 'sentiment': 0.1},
                    {'time': round(0.8 * estimated_total_seconds, 1), 'sentiment': -0.2}
                ]
            else: # Handle case with very few words, avoid division by zero
                 simulated_sentiment_trend_data = [{'time': 0.0, 'sentiment': 0.0}]


        vocab_richness = 0.0
        if word_count > 0:
            # Ensure words are actual words and handle potential errors for robustness
            actual_words = [word for word in text.lower().split() if word.isalpha()]
            unique_words_count = len(set(actual_words))
            actual_word_count = len(actual_words)
            vocab_richness = unique_words_count / actual_word_count if actual_word_count > 0 else 0.0

        return QuantitativeMetrics(
            talk_to_listen_ratio=talk_ratio,
            speaker_turn_duration_avg=round(avg_turn_duration, 2),
            interruptions_count=interruptions,
            sentiment_trend=simulated_sentiment_trend_data,
            word_count=word_count,
            vocabulary_richness_score=round(vocab_richness, 3)
        )
