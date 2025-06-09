"""
Test the linguistic analysis service directly with sample text
"""
import sys
import os
sys.path.append('p:/python/New folder (2)/backend')

from services.linguistic_service import analyze_linguistic_patterns

def test_linguistic_service_directly():
    """Test the linguistic analysis service with sample text"""
    
    # Sample transcript that would come from speech recognition
    test_transcript = """
    Well, um, I think maybe I was there around, you know, like 8 PM or so. 
    I'm not really sure exactly, but I definitely remember being there. 
    The whole thing was, uh, kind of confusing really. I mean, perhaps it was 
    earlier, but I'm absolutely certain I saw him there. You know what I mean?
    """
    
    # Test with a simulated duration of 15 seconds
    duration = 15.0
    
    print("[BRAIN] Testing Linguistic Analysis Service")
    print("=" * 50)
    print(f"Sample text: {test_transcript.strip()}")
    print(f"Duration: {duration} seconds")
    print("=" * 50)
    
    # Run the analysis
    result = analyze_linguistic_patterns(test_transcript, duration)
    
    # Display results
    print("\n[DATA] Quantitative Metrics:")
    print(f"  Word Count: {result['word_count']}")
    print(f"  Hesitation Count: {result['hesitation_count']}")
    print(f"  Qualifier Count: {result['qualifier_count']}")
    print(f"  Certainty Count: {result['certainty_count']}")
    print(f"  Filler Count: {result['filler_count']}")
    print(f"  Repetition Count: {result['repetition_count']}")
    print(f"  Formality Score: {result['formality_score']}")
    print(f"  Complexity Score: {result['complexity_score']}")
    print(f"  Average Word Length: {result['avg_word_length']}")
    print(f"  Average Words/Sentence: {result['avg_words_per_sentence']}")
    print(f"  Speech Rate (WPM): {result['speech_rate_wpm']}")
    print(f"  Confidence Ratio: {result['confidence_ratio']}")
    
    print("\n[NOTE] Descriptive Analysis:")
    print(f"  Speech Patterns: {result['speech_patterns']}")
    print(f"  Word Choice: {result['word_choice']}")
    print(f"  Emotional Consistency: {result['emotional_consistency']}")
    print(f"  Detail Level: {result['detail_level']}")
    
    # Verify expected patterns
    print("\n[PASS] Verification:")
    print(f"  Expected hesitations (um, uh, like, you know): {result['hesitation_count'] >= 4}")
    print(f"  Expected qualifiers (maybe, think, perhaps, kind of): {result['qualifier_count'] >= 3}")
    print(f"  Expected certainty markers (definitely, absolutely): {result['certainty_count'] >= 2}")
    print(f"  Speech rate calculated: {result['speech_rate_wpm'] is not None}")

if __name__ == "__main__":
    test_linguistic_service_directly()
