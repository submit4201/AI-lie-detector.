"""
Linguistic Analysis Service
Provides quantitative linguistic analysis for transcribed text.
This module uses regular expressions and statistical calculations to extract
features from text that may be indicative of various speech patterns,
formality, complexity, and confidence levels.
"""
import re
import logging
from typing import Dict, Any, List, Optional # Optional added for clarity

logger = logging.getLogger(__name__) # Logger for this module

def analyze_linguistic_patterns(transcript: str, duration: Optional[float] = None) -> Dict[str, Any]:
    """
    Analyzes linguistic patterns in the provided transcript to generate quantitative metrics.
    These metrics can support deception detection, behavioral analysis, and general
    understanding of the speaker's communication style.

    The analysis includes counts of various word types (hesitations, qualifiers, certainty),
    scores for formality and complexity, rates of speech and hesitation (if duration is provided),
    and other statistical measures.

    Args:
        transcript: The transcribed text to be analyzed.
        duration: Optional. The duration of the audio in seconds, used for calculating
                  speech rate (WPM) and hesitation rate. If None, these rates will not be calculated.

    Returns:
        A dictionary containing various linguistic analysis metrics.
        If the transcript is empty or None, returns a default analysis structure.
    """
    # Return default structure if transcript is empty or whitespace only
    if not transcript or not transcript.strip():
        logger.warning("Linguistic analysis called with empty transcript. Returning default analysis.")
        return get_default_linguistic_analysis()
    
    try:
        # Basic text statistics: split transcript into words and count them.
        words = transcript.split()
        word_count = len(words)

        # --- Word Category Counts using Regex ---
        # Regex `\b` ensures whole word matching. `re.IGNORECASE` for case-insensitivity.

        # Hesitation patterns: Common words or phrases indicating hesitation or thinking.
        # Includes filler words like "um", "uh", and discourse markers like "you know", "like".
        hesitation_words_list = re.findall(
            r'\b(um|uh|er|ah|like|you know|well|so|actually|basically|literally|totally|really|just|i mean|you see|let me think|how do i say|what\'s the word|you understand|if you will|sort of speak)\b',
            transcript, re.IGNORECASE
        )
        hesitation_count = len(hesitation_words_list)

        # Qualifier usage: Words that express uncertainty or soften a statement.
        qualifiers_list = re.findall(
            r'\b(maybe|perhaps|might|could|possibly|probably|sort of|kind of|i think|i guess|i believe|i suppose|somewhat|rather|fairly|quite|seems like|appears to|tends to|usually|sometimes|often|occasionally|potentially|presumably|allegedly|supposedly|apparently)\b',
            transcript, re.IGNORECASE
        )
        qualifier_count = len(qualifiers_list)

        # Certainty indicators: Words that express high confidence or definitiveness.
        certainty_words_list = re.findall(
            r'\b(definitely|certainly|absolutely|sure|confident|know|always|never|exactly|clearly|obviously|undoubtedly|unquestionably|positively|guaranteed|without doubt|for certain|no doubt|100 percent|completely|totally|entirely|perfectly)\b',
            transcript, re.IGNORECASE
        )
        certainty_count = len(certainty_words_list)

        # --- Formality Score Calculation ---
        # Formality is assessed by identifying formal and informal language markers.

        # Formal transitions and conjunctions often found in professional or academic writing.
        formal_transitions_list = re.findall(r'\b(furthermore|however|nevertheless|therefore|consequently|moreover|additionally|subsequently|accordingly|thus|hence|whereas|albeit|notwithstanding|indeed|inasmuch as|insofar as|heretofore|henceforth)\b', transcript, re.IGNORECASE)
        
        # Professional courtesy and politeness terms.
        formal_courtesy_list = re.findall(r'\b(sir|madam|please|thank you|kindly|respectfully|sincerely|cordially|graciously|humbly|your honor|your excellency|distinguished|esteemed)\b', transcript, re.IGNORECASE)
        
        # Legal/Business formal language terms.
        formal_legal_list = re.findall(r'\b(pursuant to|in accordance with|with regard to|concerning|regarding|herein|thereof|whereby|wherein|whereof|heretofore|aforementioned|subsequent to|prior to|in lieu of)\b', transcript, re.IGNORECASE) # Removed notwithstanding as it's in transitions
        
        # Academic/Professional qualifiers that lend a formal tone.
        formal_academic_list = re.findall(r'\b(substantially|significantly|predominantly|fundamentally|essentially|particularly|specifically|generally|typically|consistently|primarily|principally|ultimately|comprehensively)\b', transcript, re.IGNORECASE)
        
        # Formal expressions and phrases.
        formal_expressions_list = re.findall(r'\b(allow me to|permit me to|if I may|with your permission|I would like to express|I wish to convey|it is my understanding|it has come to my attention|I am compelled to|I feel obligated to)\b', transcript, re.IGNORECASE)
        
        # Aggregate all identified formal words.
        formal_words_list = formal_transitions_list + formal_courtesy_list + formal_legal_list + formal_academic_list + formal_expressions_list
        
        # Informal indicators:
        # Casual responses and interjections.
        informal_casual_interjections_list = re.findall(r'\b(yeah|yep|nah|yup|uh-huh|mm-hmm|nope|sure thing|no way|for real|totally|whatever|awesome|cool|sweet|nice|dude|buddy|man|bro|sis)\b', transcript, re.IGNORECASE)
        
        # Common informal contractions (e.g., "gonna", "wanna").
        informal_contractions_spoken_list = re.findall(r'\b(gonna|wanna|gotta|kinda|sorta|dunno|shoulda|woulda|coulda|lemme|gimme|betcha|whatcha|lookin|doin|nothin|somethin|anythin|everythin)\b', transcript, re.IGNORECASE)
        
        # Standard English contractions (e.g., "can't", "won't"). These are common but reduce strict formality.
        standard_contractions_list = re.findall(r'\b(ain\'t|can\'t|won\'t|shouldn\'t|wouldn\'t|couldn\'t|isn\'t|aren\'t|wasn\'t|weren\'t|haven\'t|hasn\'t|hadn\'t|don\'t|doesn\'t|didn\'t|I\'m|you\'re|he\'s|she\'s|it\'s|we\'re|they\'re|I\'ve|you\'ve|we\'ve|they\'ve|I\'ll|you\'ll|he\'ll|she\'ll|we\'ll|they\'ll|I\'d|you\'d|he\'d|she\'d|we\'d|they\'d)\b', transcript, re.IGNORECASE)
        
        # Slang and very informal expressions.
        informal_slang_expressions_list = re.findall(r'\b(ok|okay|alright|right on|no biggie|no prob|my bad|oh well|so what|big deal|kinda like|sorta like|you know what I mean|if you know what I mean)\b', transcript, re.IGNORECASE)
        
        # Aggregate highly casual/slang informal words.
        casual_informal_words_list = informal_casual_interjections_list + informal_contractions_spoken_list + informal_slang_expressions_list
        
        # Calculate formality score (0-100):
        # Ratios of formal/informal words to total word count.
        formal_ratio = len(formal_words_list) / max(word_count, 1)
        casual_penalty_ratio = len(casual_informal_words_list) / max(word_count, 1)
        standard_contraction_penalty_ratio = len(standard_contractions_list) / max(word_count, 1)
        
        # Formality scoring logic:
        # - Start with a neutral baseline (e.g., 50).
        # - Boost score based on formal word ratio (strong positive impact).
        # - Penalize score based on casual/slang ratio (moderate negative impact).
        # - Slightly penalize score based on standard contraction ratio (light negative impact).
        baseline_formality = 50
        formal_boost_factor = 500  # Multiplier for formal words' positive impact
        casual_penalty_factor = 250 # Multiplier for casual/slang words' negative impact
        standard_contraction_penalty_factor = 100 # Multiplier for standard contractions' negative impact
        
        formality_score = max(0, min(100, # Clamp score between 0 and 100
            baseline_formality +
            (formal_ratio * formal_boost_factor) -
            (casual_penalty_ratio * casual_penalty_factor) -
            (standard_contraction_penalty_ratio * standard_contraction_penalty_factor)
        ))
        
        # Filler words (subset of hesitations, specifically vocalizations like "um", "uh").
        filler_words_list = re.findall(r'\b(um|uh|er|ah)\b', transcript, re.IGNORECASE)
        filler_count = len(filler_words_list)

        # Word repetitions (can indicate stress or attempts to control narrative).
        # Immediate repetitions (e.g., "I I think").
        immediate_repetitions_list = re.findall(r'\b(\w+)\s+\1\b', transcript, re.IGNORECASE)
        
        # Phrase repetitions (repeating a sequence of 2-4 words).
        phrase_repetitions_list = []
        words_cleaned_for_phrase_match = [word.lower().strip('.,!?') for word in words] # Normalize for matching
        for i in range(len(words_cleaned_for_phrase_match) - 1):
            for phrase_len in range(2, min(5, len(words_cleaned_for_phrase_match) - i + 1)): # Phrases of length 2 to 4
                current_phrase = ' '.join(words_cleaned_for_phrase_match[i : i + phrase_len])
                # Search for this phrase in the subsequent text
                remaining_text = ' '.join(words_cleaned_for_phrase_match[i + phrase_len :]).lower()
                if current_phrase in remaining_text and len(current_phrase.split()) >= 2: # Ensure it's a multi-word phrase
                    phrase_repetitions_list.append(current_phrase)
                    break # Avoid multiple counts for overlapping phrases starting at the same point
        
        repetition_count = len(immediate_repetitions_list) + len(phrase_repetitions_list)
        
        # Average word length (an indicator of vocabulary complexity).
        # Strips common punctuation before calculating length.
        avg_word_length = sum(len(word.strip('.,!?')) for word in words) / max(word_count, 1)
        
        # Sentence count and average words per sentence (indicators of syntactic complexity).
        sentences_list = re.split(r'[.!?]+', transcript) # Split by common sentence terminators
        sentence_count = len([s for s in sentences_list if s.strip()]) # Count non-empty sentences
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        
        # Calculate rates if audio duration is provided and valid.
        speech_rate_wpm = None
        hesitation_rate_hpm = None # Hesitations per minute
        if duration is not None and duration > 0:
            speech_rate_wpm = (word_count / duration) * 60 # Words per minute
            hesitation_rate_hpm = (hesitation_count / duration) * 60  # Hesitations per minute
        
        # --- Complexity Score Calculation (0-100) ---
        # Combines factors like word length, sentence length, vocabulary diversity,
        # and penalizes for high hesitation.

        # Factor 1: Average word length (longer words suggest higher complexity). Scaled.
        word_length_complexity_factor = min(100, avg_word_length * 15) # Max contribution of 100
        
        # Factor 2: Sentence length (longer sentences suggest higher syntactic complexity). Scaled.
        sentence_length_complexity_factor = min(100, avg_words_per_sentence * 3) # Max contribution of 100
        
        # Factor 3: Vocabulary diversity (ratio of unique words to total words). Score 0-100.
        unique_words_count = len(set(word.lower().strip('.,!?') for word in words))
        vocabulary_diversity_score = (unique_words_count / max(word_count, 1)) * 100
        
        # Penalty Factor 1: Hesitation frequency (high hesitations can reduce perceived complexity).
        # Scaled: e.g., 10% hesitation frequency (hesitations/word_count) could lead to a 100 point penalty, capped at 50.
        hesitation_penalty_factor = min(50, (hesitation_count / max(word_count, 1)) * 1000)
        
        # Penalty Factor 2: Imbalance between certainty and qualifier words.
        # A large imbalance might indicate simpler or overly assertive/passive rhetoric, capped.
        # This factor is experimental for complexity.
        # Using `certainty_balance` from before, but renaming for clarity in this context.
        certainty_qualifier_imbalance_penalty = min(25, abs(certainty_count - qualifier_count) * 2) # Max penalty of 25. (Adjusted multiplier from 5 to 2)

        # Calculate overall complexity score:
        # Average of positive complexity contributors.
        positive_complexity_factors = [
            word_length_complexity_factor,
            sentence_length_complexity_factor,
            vocabulary_diversity_score
        ]
        average_positive_complexity = sum(positive_complexity_factors) / len(positive_complexity_factors)
        # Apply penalties and clamp score between 0 and 100.
        complexity_score = max(0, min(100, average_positive_complexity - hesitation_penalty_factor - certainty_qualifier_imbalance_penalty))
        
        # Confidence ratio: Ratio of certainty words to the sum of certainty and qualifier words.
        # Ranges from 0 (all qualifiers) to 1 (all certainty). Value of 0.5 is balanced.
        # Add 1 to denominator to avoid division by zero if both counts are 0.
        confidence_ratio = certainty_count / max(qualifier_count + certainty_count, 1)
        
        # Log calculated metrics for debugging or monitoring
        logger.debug(f"Linguistic analysis for transcript (first 50 chars: '{transcript[:50]}...'): "
                     f"WordCount={word_count}, Hesitations={hesitation_count}, Qualifiers={qualifier_count}, "
                     f"Certainty={certainty_count}, Formality={formality_score:.1f}, Complexity={complexity_score:.1f}, "
                     f"ConfidenceRatio={confidence_ratio:.2f}")

        return {
            "word_count": word_count,
            "hesitation_count": hesitation_count,
            "qualifier_count": qualifier_count,
            "certainty_count": certainty_count,
            "filler_count": filler_count,
            "repetition_count": repetition_count,
            "formality_score": round(formality_score, 1), # Rounded for cleaner output
            "complexity_score": round(complexity_score, 1), # Rounded
            "avg_word_length": round(avg_word_length, 1), # Rounded
            "avg_words_per_sentence": round(avg_words_per_sentence, 1), # Rounded
            "sentence_count": sentence_count,
            "speech_rate_wpm": round(speech_rate_wpm, 1) if speech_rate_wpm is not None else None, # Rounded
            "hesitation_rate_hpm": round(hesitation_rate_hpm, 1) if hesitation_rate_hpm is not None else None, # Renamed and rounded
            "confidence_ratio": round(confidence_ratio, 2), # Rounded
            
            # The following fields generate descriptive text based on the quantitative metrics.
            # They are included for direct use or for compatibility with systems expecting textual summaries.
            "speech_patterns": generate_speech_patterns_description(
                word_count, hesitation_count, speech_rate_wpm, complexity_score
            ),
            "word_choice": generate_word_choice_description(
                avg_word_length, formality_score, qualifier_count, certainty_count
            ),
            "emotional_consistency": generate_emotional_consistency_description( # Note: This is an interpretation based on linguistic cues
                hesitation_count, qualifier_count, confidence_ratio
            ),
            "detail_level": generate_detail_level_description(
                avg_words_per_sentence, complexity_score, word_count
            )
        }
        
    except Exception as e:
        # Log any unexpected errors during analysis and return default structure.
        logger.error(f"Error during linguistic analysis for transcript (first 50 chars: '{transcript[:50]}...'): {e}", exc_info=True)
        return get_default_linguistic_analysis()

def generate_speech_patterns_description(word_count: int, hesitation_count: int, 
                                       speech_rate_wpm: Optional[float] = None, complexity_score: float = 50.0) -> str:
    """
    Generates a human-readable description of speech patterns based on quantitative metrics.

    Args:
        word_count: Total number of words in the transcript.
        hesitation_count: Total number of hesitation markers found.
        speech_rate_wpm: Optional. Speaker's speech rate in words per minute.
        complexity_score: Calculated linguistic complexity score (0-100).

    Returns:
        A string describing the speech patterns.
    """
    
    # Determine speech rate description
    if speech_rate_wpm is not None:
        if speech_rate_wpm > 160:
            rate_desc = "a very rapid speech pace"
        elif speech_rate_wpm > 130: # Adjusted threshold for 'fast'
            rate_desc = "a fast speech pace"
        elif speech_rate_wpm > 100: # Adjusted threshold for 'normal'
            rate_desc = "a normal speech pace"
        elif speech_rate_wpm > 70:
            rate_desc = "a slow speech pace"
        else:
            rate_desc = "a very slow, deliberate speech pace"
    else:
        rate_desc = "an undetermined speech pace (duration not provided)" # More informative default
    
    # Determine hesitation level description
    # Based on occurrences per, say, 100 words for better context if word_count is available
    hesitation_frequency = (hesitation_count / max(word_count,1)) * 100 if word_count > 0 else 0
    if hesitation_frequency > 7: # e.g., >7 hesitations per 100 words
        hesitation_level_desc = "a high frequency of hesitation"
    elif hesitation_frequency > 3: # e.g., >3 hesitations per 100 words
        hesitation_level_desc = "a moderate frequency of hesitation"
    else:
        hesitation_level_desc = "a low frequency of hesitation"

    # Determine complexity level description
    if complexity_score > 70:
        complexity_level_desc = "high linguistic complexity"
    elif complexity_score > 40:
        complexity_level_desc = "moderate linguistic complexity"
    else:
        complexity_level_desc = "low linguistic complexity"
    
    # Construct the overall description
    description = (
        f"The speaker demonstrates {rate_desc}, characterized by {hesitation_level_desc} "
        f"and {complexity_level_desc}. The speech contains {hesitation_count} hesitation markers "
        f"within {word_count} words. This pattern may suggest "
        f"{'confident and fluid expression' if hesitation_frequency <= 3 and complexity_score > 40 else 'some degree of uncertainty, cognitive load, or careful articulation'}."
    )
    logger.debug(f"Generated speech patterns description: {description}")
    return description

def generate_word_choice_description(avg_word_length: float, formality_score: float, 
                                   qualifier_count: int, certainty_count: int) -> str:
    """
    Generates a human-readable description of word choice patterns.

    Args:
        avg_word_length: Average length of words used.
        formality_score: Calculated formality score (0-100).
        qualifier_count: Total number of qualifier words found.
        certainty_count: Total number of certainty words found.

    Returns:
        A string describing the word choice patterns.
    """
    
    # Determine vocabulary complexity description based on average word length
    if avg_word_length > 5.5: # Adjusted threshold
        vocab_complexity_desc = "a sophisticated vocabulary"
    elif avg_word_length > 4.5: # Adjusted threshold
        vocab_complexity_desc = "a moderate vocabulary complexity"
    else:
        vocab_complexity_desc = "a relatively simple vocabulary"

    # Determine formality level description based on formality score
    if formality_score > 65: # Adjusted threshold
        formality_level_desc = "a formal register"
    elif formality_score > 35: # Adjusted threshold
        formality_level_desc = "a moderately formal register"
    else:
        formality_level_desc = "a casual or informal register"
    
    # Describe the balance between qualifiers and certainty markers
    if qualifier_count > certainty_count * 1.5: # Significantly more qualifiers
        certainty_balance_desc = "a predominant use of qualifying language, suggesting potential uncertainty or cautiousness"
    elif certainty_count > qualifier_count * 1.5: # Significantly more certainty
        certainty_balance_desc = "a tendency towards confident and definitive language"
    else:
        certainty_balance_desc = "a balanced use of certain and uncertain language"
    
    description = (
        f"Word choice reflects {vocab_complexity_desc}, typically employed in {formality_level_desc}. "
        f"The analysis reveals {certainty_balance_desc}, with {qualifier_count} qualifiers "
        f"versus {certainty_count} certainty markers identified."
    )
    logger.debug(f"Generated word choice description: {description}")
    return description

def generate_emotional_consistency_description(hesitation_count: int, qualifier_count: int, 
                                             confidence_ratio: float) -> str:
    """
    Generates a human-readable description related to linguistic cues that might infer
    emotional consistency or pressure. This is an interpretation and not a direct emotion detection.

    Args:
        hesitation_count: Total number of hesitation markers.
        qualifier_count: Total number of qualifier words.
        confidence_ratio: Calculated ratio of certainty to (certainty + qualifier) words.

    Returns:
        A string describing linguistic cues related to emotional state.
    """
    
    # Describe consistency based on confidence ratio
    if confidence_ratio > 0.65: # Adjusted threshold
        consistency_desc = "linguistic patterns suggesting high internal consistency and confident expression"
    elif confidence_ratio > 0.35: # Adjusted threshold
        consistency_desc = "linguistic patterns suggesting moderate internal consistency with some indicators of uncertainty"
    else:
        consistency_desc = "linguistic patterns suggesting lower internal consistency, with frequent uncertainty markers"
    
    # Sum of hesitations and qualifiers as potential stress/pressure indicators
    linguistic_stress_indicators = hesitation_count + qualifier_count
    # Define stress level based on a threshold (e.g., per 100 words, assuming an average word count if not available)
    # This is a heuristic. For a more robust measure, it should be normalized by word count.
    # For simplicity here, using raw counts with arbitrary thresholds.
    if linguistic_stress_indicators > 10: # Example threshold
        stress_level_desc = "elevated levels of linguistic stress indicators"
    elif linguistic_stress_indicators > 5: # Example threshold
        stress_level_desc = "moderate levels of linguistic stress indicators"
    else:
        stress_level_desc = "low levels of linguistic stress indicators"
    
    description = (
        f"The speaker's language shows {consistency_desc}. Analysis of linguistic stress cues "
        f"(hesitations, qualifiers) indicates {stress_level_desc}. These patterns might suggest "
        f"{'potential cognitive load, anxiety, or deception concerns' if linguistic_stress_indicators > 10 else 'relatively typical communication patterns under the circumstances'}."
    )
    logger.debug(f"Generated emotional consistency description: {description}")
    return description

def generate_detail_level_description(avg_words_per_sentence: float, complexity_score: float, 
                                    word_count: int) -> str:
    """
    Generates a human-readable description of the detail level and structure of the response.

    Args:
        avg_words_per_sentence: Average number of words per sentence.
        complexity_score: Calculated linguistic complexity score (0-100).
        word_count: Total number of words in the transcript.

    Returns:
        A string describing the detail level and structure.
    """
    
    # Describe sentence structure based on average words per sentence
    if avg_words_per_sentence > 25: # Adjusted threshold
        sentence_structure_desc = "highly complex and detailed sentence structures"
    elif avg_words_per_sentence > 15: # Adjusted threshold
        sentence_structure_desc = "moderately complex sentence structures"
    else:
        sentence_structure_desc = "relatively simple and direct sentence structures"
    
    # Describe overall detail level based on word count
    if word_count > 250: # Adjusted threshold
        overall_detail_desc = "a comprehensive and extensive level of detail"
    elif word_count > 100: # Adjusted threshold
        overall_detail_desc = "a moderate level of detail"
    else:
        overall_detail_desc = "a brief or concise level of detail"
    
    # Describe communication style based on complexity score
    if complexity_score > 70:
        comm_style_desc = "a sophisticated and nuanced"
    elif complexity_score > 40:
        comm_style_desc = "an appropriate and clear"
    else:
        comm_style_desc = "a simple and straightforward"

    description = (
        f"The response provides {overall_detail_desc}, utilizing {sentence_structure_desc}. "
        f"The overall complexity score of {complexity_score:.1f}/100 suggests {comm_style_desc} "
        f"communication style, with an average of {avg_words_per_sentence:.1f} words per sentence."
    )
    logger.debug(f"Generated detail level description: {description}")
    return description

def get_default_linguistic_analysis() -> Dict[str, Any]:
    """
    Returns a default structure for linguistic analysis, typically used in cases of
    empty input or errors during analysis. All quantitative fields are set to 0 or None,
    and descriptive fields indicate that analysis was unavailable.

    Returns:
        A dictionary with default values for all linguistic analysis metrics.
    """
    logger.debug("Returning default linguistic analysis structure.")
    return {
        "word_count": 0,
        "hesitation_count": 0,
        "qualifier_count": 0,
        "certainty_count": 0,
        "filler_count": 0,
        "repetition_count": 0,
        "formality_score": 0.0, # Use float for scores
        "complexity_score": 0.0, # Use float for scores
        "avg_word_length": 0.0, # Use float
        "avg_words_per_sentence": 0.0, # Use float
        "sentence_count": 0,
        "speech_rate_wpm": None, # Remains None if not calculable
        "hesitation_rate_hpm": None, # Renamed, remains None if not calculable
        "confidence_ratio": 0.0, # Use float
        "speech_patterns": "Linguistic speech pattern analysis unavailable - insufficient data or error.",
        "word_choice": "Linguistic word choice analysis unavailable - insufficient data or error.",
        "emotional_consistency": "Linguistic emotional consistency cues analysis unavailable - insufficient data or error.",
        "detail_level": "Linguistic detail level analysis unavailable - insufficient data or error."
    }
