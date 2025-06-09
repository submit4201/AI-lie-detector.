"""
Linguistic Analysis Service
Provides quantitative linguistic analysis for transcribed text
"""
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def analyze_linguistic_patterns(transcript: str, duration: float = None) -> Dict[str, Any]:
    """
    Analyze linguistic patterns in the transcript to provide quantitative metrics
    that support deception detection and behavioral analysis.
    
    Args:
        transcript (str): The transcribed text to analyze
        duration (float, optional): Audio duration in seconds for rate calculations
    
    Returns:
        Dict containing linguistic analysis metrics
    """
    if not transcript or not transcript.strip():
        return get_default_linguistic_analysis()
    
    try:
        # Basic text statistics
        words = transcript.split()
        word_count = len(words)
          # Hesitation patterns - Enhanced detection
        hesitation_words = re.findall(r'\b(um|uh|er|ah|like|you know|well|so|actually|basically|literally|totally|really|just|i mean|you see|let me think|how do i say|what\'s the word|you understand|if you will|sort of speak)\b', transcript, re.IGNORECASE)
        hesitation_count = len(hesitation_words)
          # Qualifier usage (uncertainty indicators) - Enhanced patterns
        qualifiers = re.findall(r'\b(maybe|perhaps|might|could|possibly|probably|sort of|kind of|i think|i guess|i believe|i suppose|somewhat|rather|fairly|quite|seems like|appears to|tends to|usually|sometimes|often|occasionally|potentially|presumably|allegedly|supposedly|apparently)\b', transcript, re.IGNORECASE)
        qualifier_count = len(qualifiers)
        
        # Certainty indicators - Enhanced patterns
        certainty_words = re.findall(r'\b(definitely|certainly|absolutely|sure|confident|know|always|never|exactly|clearly|obviously|undoubtedly|unquestionably|positively|guaranteed|without doubt|for certain|no doubt|100 percent|completely|totally|entirely|perfectly)\b', transcript, re.IGNORECASE)
        certainty_count = len(certainty_words)        # Formality indicators - Comprehensive Enhanced patterns
        # Professional/Academic transitions and conjunctions
        formal_transitions = re.findall(r'\b(furthermore|however|nevertheless|therefore|consequently|moreover|additionally|subsequently|accordingly|thus|hence|whereas|albeit|notwithstanding|indeed|inasmuch as|insofar as|heretofore|henceforth|notwithstanding)\b', transcript, re.IGNORECASE)
        
        # Professional courtesy and politeness
        formal_courtesy = re.findall(r'\b(sir|madam|please|thank you|kindly|respectfully|sincerely|cordially|graciously|humbly|your honor|your excellency|distinguished|esteemed)\b', transcript, re.IGNORECASE)
        
        # Legal/Business formal language
        formal_legal = re.findall(r'\b(pursuant to|in accordance with|with regard to|concerning|regarding|herein|thereof|whereby|wherein|whereof|heretofore|aforementioned|subsequent to|prior to|in lieu of|notwithstanding)\b', transcript, re.IGNORECASE)
        
        # Academic/Professional qualifiers
        formal_academic = re.findall(r'\b(substantially|significantly|predominantly|fundamentally|essentially|particularly|specifically|generally|typically|consistently|primarily|principally|ultimately|comprehensively)\b', transcript, re.IGNORECASE)
        
        # Formal expressions and phrases
        formal_expressions = re.findall(r'\b(allow me to|permit me to|if I may|with your permission|I would like to express|I wish to convey|it is my understanding|it has come to my attention|I am compelled to|I feel obligated to)\b', transcript, re.IGNORECASE)
        
        # Total formal words
        formal_words = formal_transitions + formal_courtesy + formal_legal + formal_academic + formal_expressions
        
        # Informal indicators - Enhanced patterns
        # Casual responses and interjections
        informal_casual = re.findall(r'\b(yeah|yep|nah|yup|uh-huh|mm-hmm|nope|yep|sure thing|no way|for real|totally|whatever|awesome|cool|sweet|nice|dude|buddy|man|bro|sis)\b', transcript, re.IGNORECASE)
        
        # Contractions and casual language
        informal_contractions = re.findall(r'\b(gonna|wanna|gotta|kinda|sorta|dunno|shoulda|woulda|coulda|lemme|gimme|betcha|whatcha|lookin|doin|nothin|somethin|anythin|everythin)\b', transcript, re.IGNORECASE)
        
        # Standard contractions (common but reduce formality)
        standard_contractions = re.findall(r'\b(ain\'t|can\'t|won\'t|shouldn\'t|wouldn\'t|couldn\'t|isn\'t|aren\'t|wasn\'t|weren\'t|haven\'t|hasn\'t|hadn\'t|don\'t|doesn\'t|didn\'t|I\'m|you\'re|he\'s|she\'s|it\'s|we\'re|they\'re|I\'ve|you\'ve|we\'ve|they\'ve|I\'ll|you\'ll|he\'ll|she\'ll|we\'ll|they\'ll|I\'d|you\'d|he\'d|she\'d|we\'d|they\'d)\b', transcript, re.IGNORECASE)
        
        # Slang and very informal expressions
        informal_slang = re.findall(r'\b(ok|okay|alright|right on|no biggie|no prob|my bad|oh well|so what|big deal|kinda like|sorta like|you know what I mean|if you know what I mean)\b', transcript, re.IGNORECASE)
        
        # Total informal words with different weights
        casual_informal = informal_casual + informal_contractions + informal_slang
        standard_informal = standard_contractions        # Balanced formality calculation with realistic scaling
        formal_ratio = len(formal_words) / max(word_count, 1)
        casual_penalty = len(casual_informal) / max(word_count, 1)
        standard_penalty = len(standard_informal) / max(word_count, 1)
        
        # Realistic calculation with baseline adjustment:
        # - Start with baseline of 50 (neutral)
        # - Formal words: add 500x weight (strong positive impact)
        # - Casual/slang: subtract 250x penalty (moderate negative impact)  
        # - Standard contractions: subtract 100x penalty (light negative impact)
        baseline = 50
        formal_boost = formal_ratio * 500
        casual_reduction = casual_penalty * 250
        standard_reduction = standard_penalty * 100
        
        formality_score = max(0, min(100, 
            baseline + formal_boost - casual_reduction - standard_reduction
        ))
        
        # Filler words (stress indicators)
        filler_words = re.findall(r'\b(um|uh|er|ah)\b', transcript, re.IGNORECASE)
        filler_count = len(filler_words)
          # Word repetitions (possible stress/deception indicator)
        # Check for immediate word repetitions
        immediate_repetitions = re.findall(r'\b(\w+)\s+\1\b', transcript, re.IGNORECASE)
        
        # Check for phrase repetitions (2-4 words)
        phrase_repetitions = []
        words_clean = [word.strip('.,!?') for word in words]
        for i in range(len(words_clean) - 1):
            for phrase_len in range(2, min(5, len(words_clean) - i + 1)):
                phrase = ' '.join(words_clean[i:i+phrase_len]).lower()
                rest_text = ' '.join(words_clean[i+phrase_len:]).lower()
                if phrase in rest_text and len(phrase.split()) >= 2:
                    phrase_repetitions.append(phrase)
                    break
        
        repetition_count = len(immediate_repetitions) + len(phrase_repetitions)
        
        # Average word length (complexity indicator)
        avg_word_length = sum(len(word.strip('.,!?')) for word in words) / max(word_count, 1)
        
        # Sentence count (complexity indicator)
        sentences = re.split(r'[.!?]+', transcript)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        
        # Calculate rates if duration is provided
        speech_rate_wpm = None
        hesitation_rate = None
        if duration and duration > 0:
            speech_rate_wpm = (word_count / duration) * 60
            hesitation_rate = (hesitation_count / duration) * 60  # hesitations per minute
          # Complexity score (0-100 based on various factors)
        # Factor 1: Average word length (longer words = more complex)
        word_length_factor = min(100, avg_word_length * 15)
        
        # Factor 2: Sentence structure (longer sentences = more complex)
        sentence_length_factor = min(100, avg_words_per_sentence * 3)
        
        # Factor 3: Vocabulary diversity (unique words ratio)
        unique_words = len(set(word.lower().strip('.,!?') for word in words))
        vocabulary_diversity = (unique_words / max(word_count, 1)) * 100
        
        # Factor 4: Hesitation penalty (more hesitations = less complexity)
        hesitation_penalty = min(50, (hesitation_count / max(word_count, 1)) * 1000)
        
        # Factor 5: Qualifier/certainty balance (balanced = more complex)
        certainty_balance = min(25, abs(certainty_count - qualifier_count) * 5)
        
        complexity_factors = [
            word_length_factor,
            sentence_length_factor, 
            vocabulary_diversity,
            certainty_balance
        ]
        complexity_base = sum(complexity_factors) / len(complexity_factors)
        complexity_score = max(0, complexity_base - hesitation_penalty)
        
        # Confidence indicators ratio
        confidence_ratio = certainty_count / max(qualifier_count + certainty_count, 1)
        
        return {
            "word_count": word_count,
            "hesitation_count": hesitation_count,
            "qualifier_count": qualifier_count,
            "certainty_count": certainty_count,
            "filler_count": filler_count,
            "repetition_count": repetition_count,
            "formality_score": round(formality_score, 1),
            "complexity_score": round(complexity_score, 1),
            "avg_word_length": round(avg_word_length, 1),
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "sentence_count": sentence_count,
            "speech_rate_wpm": round(speech_rate_wpm, 1) if speech_rate_wpm else None,
            "hesitation_rate": round(hesitation_rate, 1) if hesitation_rate else None,
            "confidence_ratio": round(confidence_ratio, 2),
            
            # Descriptive analysis for backwards compatibility
            "speech_patterns": generate_speech_patterns_description(
                word_count, hesitation_count, speech_rate_wpm, complexity_score
            ),
            "word_choice": generate_word_choice_description(
                avg_word_length, formality_score, qualifier_count, certainty_count
            ),
            "emotional_consistency": generate_emotional_consistency_description(
                hesitation_count, qualifier_count, confidence_ratio
            ),
            "detail_level": generate_detail_level_description(
                avg_words_per_sentence, complexity_score, word_count
            )
        }
        
    except Exception as e:
        logger.error(f"Error in linguistic analysis: {e}")
        return get_default_linguistic_analysis()

def generate_speech_patterns_description(word_count: int, hesitation_count: int, 
                                       speech_rate_wpm: float = None, complexity_score: float = 50) -> str:
    """Generate descriptive text for speech patterns based on metrics"""
    
    if speech_rate_wpm:
        if speech_rate_wpm > 160:
            rate_desc = "very rapid speech pace"
        elif speech_rate_wpm > 120:
            rate_desc = "moderate to fast speech pace"
        elif speech_rate_wpm > 80:
            rate_desc = "normal speech pace"
        else:
            rate_desc = "slow, deliberate speech pace"
    else:
        rate_desc = "speech pace analysis pending"
    
    hesitation_level = "high" if hesitation_count > 5 else "moderate" if hesitation_count > 2 else "low"
    complexity_level = "high" if complexity_score > 70 else "moderate" if complexity_score > 40 else "low"
    
    return f"Speaker demonstrates {rate_desc} with {hesitation_level} hesitation frequency and {complexity_level} linguistic complexity. " \
           f"Speech contains {hesitation_count} hesitation markers across {word_count} words, " \
           f"suggesting {'confident expression' if hesitation_count < 3 else 'some uncertainty or processing time'}."

def generate_word_choice_description(avg_word_length: float, formality_score: float, 
                                   qualifier_count: int, certainty_count: int) -> str:
    """Generate descriptive text for word choice patterns"""
    
    complexity_level = "sophisticated" if avg_word_length > 5 else "moderate" if avg_word_length > 4 else "simple"
    formality_level = "formal" if formality_score > 20 else "moderately formal" if formality_score > 5 else "casual"
    
    if qualifier_count > certainty_count:
        certainty_desc = "frequent use of qualifying language suggesting uncertainty"
    elif certainty_count > qualifier_count * 2:
        certainty_desc = "confident, definitive language patterns"
    else:
        certainty_desc = "balanced use of certain and uncertain language"
    
    return f"Word choice reflects {complexity_level} vocabulary in a {formality_level} register. " \
           f"Analysis reveals {certainty_desc}, with {qualifier_count} qualifiers versus {certainty_count} certainty markers."

def generate_emotional_consistency_description(hesitation_count: int, qualifier_count: int, 
                                             confidence_ratio: float) -> str:
    """Generate descriptive text for emotional consistency analysis"""
    
    if confidence_ratio > 0.7:
        consistency_desc = "high emotional consistency with confident expression"
    elif confidence_ratio > 0.4:
        consistency_desc = "moderate emotional consistency with some uncertainty"
    else:
        consistency_desc = "lower emotional consistency with frequent uncertainty markers"
    
    stress_indicators = hesitation_count + qualifier_count
    stress_level = "elevated" if stress_indicators > 8 else "moderate" if stress_indicators > 4 else "low"
    
    return f"Speaker demonstrates {consistency_desc}. Stress indicator analysis shows {stress_level} levels " \
           f"based on {stress_indicators} total uncertainty/hesitation markers, suggesting " \
           f"{'potential anxiety or deception concerns' if stress_level == 'elevated' else 'normal communication patterns'}."

def generate_detail_level_description(avg_words_per_sentence: float, complexity_score: float, 
                                    word_count: int) -> str:
    """Generate descriptive text for detail level analysis"""
    
    if avg_words_per_sentence > 20:
        structure_desc = "complex, detailed sentence structures"
    elif avg_words_per_sentence > 12:
        structure_desc = "moderately complex sentence structures"
    else:
        structure_desc = "simple, direct sentence structures"
    
    detail_level = "comprehensive" if word_count > 200 else "moderate" if word_count > 100 else "brief"
    
    return f"Response provides {detail_level} detail level using {structure_desc}. " \
           f"Complexity score of {complexity_score:.1f}/100 indicates " \
           f"{'sophisticated' if complexity_score > 70 else 'appropriate' if complexity_score > 40 else 'simple'} " \
           f"communication style with average {avg_words_per_sentence:.1f} words per sentence."

def get_default_linguistic_analysis() -> Dict[str, Any]:
    """Return default linguistic analysis structure for error cases"""
    return {
        "word_count": 0,
        "hesitation_count": 0,
        "qualifier_count": 0,
        "certainty_count": 0,
        "filler_count": 0,
        "repetition_count": 0,
        "formality_score": 0,
        "complexity_score": 0,
        "avg_word_length": 0,
        "avg_words_per_sentence": 0,
        "sentence_count": 0,
        "speech_rate_wpm": None,
        "hesitation_rate": None,
        "confidence_ratio": 0,
        "speech_patterns": "Analysis unavailable - insufficient data",
        "word_choice": "Analysis unavailable - insufficient data", 
        "emotional_consistency": "Analysis unavailable - insufficient data",
        "detail_level": "Analysis unavailable - insufficient data"
    }

def linguistic_analysis_pipeline(transcript: str, duration: float = None) -> Dict[str, Any]:
    """
    Main linguistic analysis pipeline that uses Gemini for transcription, emotion analysis, and audio analysis.
    """
    try:
        linguistic_analysis = analyze_linguistic_patterns(transcript, duration)
        detail_level = generate_detail_level_description(linguistic_analysis['avg_words_per_sentence'], linguistic_analysis['complexity_score'], linguistic_analysis['word_count'])
        word_choice = generate_word_choice_description(linguistic_analysis['avg_word_length'], linguistic_analysis['formality_score'], linguistic_analysis['qualifier_count'], linguistic_analysis['certainty_count'])
        emotional_consistency = generate_emotional_consistency_description(linguistic_analysis['hesitation_count'], linguistic_analysis['qualifier_count'], linguistic_analysis['confidence_ratio'])
        speech_patterns = generate_speech_patterns_description(linguistic_analysis['word_count'], linguistic_analysis['hesitation_count'], linguistic_analysis['speech_rate_wpm'], linguistic_analysis['complexity_score'])
        resp = {
            "detail_level": detail_level,
            "word_choice": word_choice,
            "emotional_consistency": emotional_consistency,
            "speech_patterns": speech_patterns,
        }
        return linguistic_analysis
    except Exception as e:
        logger.error(f"Exception in linguistic analysis pipeline: {str(e)}", exc_info=True)
