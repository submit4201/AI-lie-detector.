# layer2_feature_extraction.py

import parselmouth
import numpy as np
import whisper
import spacy
from typing import Dict, Any, List
import io # Added for BytesIO
from faster_whisper import WhisperModel
from parselmouth.praat import call

model_size = "tiny"

# Run on GPU with FP16
model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, info = model.transcribe("audio.mp3", beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

nlp = spacy.load("en_core_web_sm")
def calculate_pause_metrics(intensity, snd, threshold=50.0):
    """Calculate pause-related metrics from intensity and sound objects."""
    pause_durations = []
    frame_len = intensity.get_frame_count()
    
    in_pause = False
    pause_start = 0.0
    pause_duration_total = 0.0
    pause_count = 0
    
    for i in range(frame_len):
        time = intensity.xs()[i]
        val = intensity.values[0][i]
        if val < threshold:
            if not in_pause:
                in_pause = True
                pause_start = time
        else:
            if in_pause:
                in_pause = False
                pause_durations.append(time - pause_start)  
                pause_count += 1
                pause_duration_total += time - pause_start
                
    if in_pause:  # If ends in pause
        pause_duration_total += snd.get_total_duration() - pause_start
        pause_count += 1
        
    return pause_duration_total, pause_count


def transcribe_audio_with_timestamps(audio_path: str) -> List[Dict[str, Any]]:
    """Transcribe audio file and return word-level timestamps."""
    transcription_seg_with_timestamps = []
    segments, _ = model.transcribe(audio_path, word_timestamps=True)

    for segment in segments:
        for word in segment.words:
            word_data = {
                "start": word.start,
                "end": word.end,
                "text": word.word
            }
            transcription_seg_with_timestamps.append(word_data)
            print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))
    
    return transcription_seg_with_timestamps
TRANSCRIPTION_SEG_WITH_TIMESTAMPS = []
def extract_acoustic_features_from_data(audio_data: bytes, sample_rate: int, channels: int) -> Dict[str, Any]:
    """Extracts acoustic features from in-memory audio data."""
    # parselmouth.Sound can load from a file path or directly from a numpy array.
    # We need to convert bytes to a numpy array first.
    # Assuming int16 PCM data as common from layer_1_input
    TRANSCRIPTION_SEG_WITH_TIMESTAMPS.append(transcribe_audio_with_timestamps("audio.mp3"))
    
    # Convert bytes to NumPy array
    # Determine dtype based on typical output of sounddevice 'int16', 'float32' etc.
    # For 'int16', the values range from -32768 to 32767.
    # Parselmouth expects float64 normalized between -1 and 1.
    
    # Assuming data from layer_1_input is 'int16'
    # If layer_1_input.dtype changes, this needs to be adjusted
    numpy_array = np.frombuffer(audio_data, dtype=np.int16)
    
    # Normalize to float64 between -1 and 1
    # Max possible value for int16 is 32767
    numpy_array_float = numpy_array.astype(np.float64) / 32767.0 
    
    # Ensure it's a 1D array if mono, or handle channels appropriately
    # Parselmouth Sound constructor expects a 1D array for mono, or 2D for stereo (samples, channels)
    # Assuming mono for now as per typical layer_1_input default
    if channels > 1:
        # Reshape or take the first channel if stereo, Parselmouth handles mono better for some funcs
        # This might need more sophisticated handling for multi-channel
        numpy_array_float = numpy_array_float[::channels] # Example: take first channel if interleaved
    
    snd = parselmouth.Sound(numpy_array_float, sampling_frequency=sample_rate)
    
    intensity = snd.to_intensity()
    pitch = snd.to_pitch()
    formant = snd.to_formant()
    point_process = snd.to_point_process_cc() # For jitter/shimmer
    hnr = snd.to_harmonics_to_noise_ratio()
    loudness = snd.to_loudness()
    energy = snd.to_energy()
    # Intensity-based pause analysis    
    pause_duration_total, pause_count = calculate_pause_metrics(intensity, snd)          

    # Pitch-related features
    pitch_values = pitch.selected_array['frequency']
    pitch_values_voiced = pitch_values[pitch_values != 0]  # remove unvoiced

    pitch_std = 0.0
    pitch_range = 0.0
    if len(pitch_values_voiced) > 1: # Need at least 2 voiced points for std/range
        pitch_std = np.std(pitch_values_voiced)
        pitch_range = np.max(pitch_values_voiced) - np.min(pitch_values_voiced)
    elif len(pitch_values_voiced) == 1:
        pitch_range = 0.0 # Or consider it undefined/NaN
        # pitch_std is 0 by default
    # Formant features
    formant_values = formant.selected_array['frequency']
    formant_std = np.std(formant_values)
    formant_range = np.max(formant_values) - np.min(formant_values)
    
    # HNR features
    hnr_values = hnr.selected_array['hnr']
    hnr_std = np.std(hnr_values)
    hnr_range = np.max(hnr_values) - np.min(hnr_values)
    
    # Loudness features
    loudness_values = loudness.selected_array['loudness']
    loudness_std = np.std(loudness_values)
    loudness_range = np.max(loudness_values) - np.min(loudness_values)
    

    # Energy features
    energy_values = energy.selected_array['energy']
    energy_std = np.std(energy_values)
    energy_range = np.max(energy_values) - np.min(energy_values)
    
    # Intensity features
    intensity_values = intensity.selected_array['intensity']
    intensity_std = np.std(intensity_values)
    intensity_range = np.max(intensity_values) - np.min(intensity_values)

    # Point process features
    point_process_values = point_process.selected_array['point_process']
    point_process_std = np.std(point_process_values)
    point_process_range = np.max(point_process_values) - np.min(point_process_values)
    
    # Jitter and Shimmer
    jitter = 0.0
    shimmer = 0.0
    if snd.get_total_duration() >= 0.1:
        try:
            jitter = call(snd, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
            shimmer = call(snd, "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        except Exception as e:
            
            # print(f"Could not calculate jitter/shimmer: {e}") # Or log this
            pass # Keep default 0.0        
    
    


    # Jitter and Shimmer
    # Praat's default arguments for jitter/shimmer might need tuning.
    # Using common defaults here.
    # Ensure the sound segment is long enough for these measures.
    # Praat might error on very short segments.
    min_duration_for_jitter_shimmer = 0.1 # seconds, example threshold
    jitter = 0.0
    shimmer = 0.0

    if snd.get_total_duration() >= min_duration_for_jitter_shimmer:
        try:
            jitter = call(snd, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3) # Adjusted defaults
            shimmer = call(snd, "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6) # Adjusted defaults
        except Exception as e:
            # print(f"Could not calculate jitter/shimmer: {e}") # Or log this
            pass # Keep default 0.0

    # Loudness variability
    loudness_variability = 0.0
    if intensity.get_number_of_frames() > 0 and len(intensity.values.flatten()) > 1:
         loudness_variability = np.std(intensity.values.flatten())

    # Intensity-based pause analysis
    pause_duration_total, pause_count = calculate_pause_metrics(intensity, snd)
    print("Pause duration: ", pause_duration_total)
    print("Pause count: ", pause_count)
    print("Pause duration total: ", pause_duration_total)
    print("Pause count: ", pause_count)

    return {
        "pitch_jitter": jitter if isinstance(jitter, float) else 0.0,
        "pitch_shimmer": shimmer if isinstance(shimmer, float) else 0.0,
        "pitch_range": pitch_range,
        "pitch_std": pitch_std,
        "pause_duration": pause_duration_total,
        "pause_count": pause_count,
        "loudness_variability": loudness_variability,
        "formant_range": formant_range,
        "formant_std": formant_std,
        "hnr_range": hnr_range,
        "hnr_std": hnr_std,
        "loudness_range": loudness_range,
        "loudness_std": loudness_std,
        "energy_range": energy_range,
        "energy_std": energy_std,
        "intensity_range": intensity_range,
        "intensity_std": intensity_std,
        "point_process_range": point_process_range,
        "point_process_std": point_process_std,
        "transcript_segment": TRANSCRIPTION_SEG_WITH_TIMESTAMPS # Include the transcribed text segment
    }

def extract_linguistic_features_from_data(audio_data: bytes, sample_rate: int, channels: int, start_time: float, end_time: float, transcription_seg_with_timestamps: List[Dict[str, Any]] =None) -> Dict[str, Any]:
    """Extracts linguistic features from in-memory audio data using Whisper."""
    # Whisper expects a file path or a NumPy array.
    # Convert bytes to NumPy array (float32 for Whisper)
    if not transcription_seg_with_timestamps:
        transcription_seg_with_timestamps = transcribe_audio_with_timestamps("audio.mp3")
    # Assuming audio_data is raw PCM (e.g. int16)
    # Convert to float32, normalized
    numpy_array_int16 = np.frombuffer(audio_data, dtype=np.int16)
    numpy_array_float32 = numpy_array_int16.astype(np.float32) / 32768.0

    # Transcribe
    # Whisper's transcribe function can take a numpy array directly.
    # It expects a mono float32 NumPy array.
    if numpy_array_float32.ndim > 1 and numpy_array_float32.shape[1] > 1: # If stereo
        numpy_array_float32 = np.mean(numpy_array_float32, axis=1) # Convert to mono by averaging channels
    text = ""
    nouns=[]
    verbs=[]
    adjectives=[]
    adverbs=[]
    
    for segment in transcription_seg_with_timestamps:
        if segment['start'] >= start_time and segment['end'] <= end_time:
            text += segment['text'] + " "
            doc = nlp(segment['text'])
            for token in doc:
                if token.pos_ == 'NOUN':
                    nouns.append(token.text)
                elif token.pos_ == 'VERB':
                    verbs.append(token.text)
                elif token.pos_ == 'ADJ':
                    adjectives.append(token.text)
                elif token.pos_ == 'ADV':
                    adverbs.append(token.text)
    word_count = 0
    sent_count = 0
    pronouns = 0
    articles = 0
    duration = 1.0 # Default duration to avoid division by zero
    for segment in transcription_seg_with_timestamps:
        if segment['start'] >= start_time and segment['end'] <= end_time:
            word_count += 1
            sent_count += 1
            if text:
                doc = nlp(text)
                pronouns = sum(1 for token in doc if token.pos_ == 'PRON')
                articles = sum(1 for token in doc if token.pos_ == 'DET')
                word_count = len([token for token in doc if token.is_alpha])
                sent_count = len(list(doc.sents))
        # calculate duration from TRANSCRIPTION_SEG_WITH_TIMESTAMPS
        duration = end_time - start_time
        print("Duration: ", duration)

    return {
        "pronoun_ratio": pronouns / word_count if word_count > 0 else 0.0,
        "article_usage": articles / word_count if word_count > 0 else 0.0,
        "speech_rate": word_count / duration if duration > 0 else 0.0,
        "sentence_length_avg": word_count / sent_count if sent_count > 0 else 0.0,
        "transcript_segment": text, # Include the transcribed text segment
        "nouns": nouns,
        "verbs": verbs,
        "adjectives": adjectives,
        "adverbs": adverbs
        # TODO: Add more linguistic features here
        # TODO: Add part of speech tagging
        # TODO: Add named entity recognition
        # TODO: Add sentiment analysis
        # TODO: Add emotion analysis
        # TODO: Add topic modeling
        # TODO: Add more complex analysis like syntax parsing, dependency parsing, etc.
    }

def extract_features_from_data(audio_data: bytes, sample_rate: int, channels: int) -> Dict[str, Any]:
    """Extracts features from in-memory audio data."""
    acoustic = extract_acoustic_features_from_data(audio_data, sample_rate, channels)
    linguistic = extract_linguistic_features_from_data(audio_data, sample_rate) # Whisper handles mono
    return {**acoustic, **linguistic}
