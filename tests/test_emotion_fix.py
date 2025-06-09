#!/usr/bin/env python3
"""
Test script to verify emotion analysis functionality and debug the NaN% issue
"""
import requests
import json
import time

def test_emotion_analysis():
    """Test emotion analysis with various inputs"""
    
    # Test with simple text first
    url = "http://localhost:8000/analyze-text"
    
    test_cases = [
        "I am very happy today and everything is going great!",
        "I am extremely sad and disappointed about this situation.",
        "This makes me really angry and frustrated.",
        "I feel nervous and anxious about the upcoming meeting.",
        "That's completely false and I never said that!"
    ]
    
    print("Testing emotion analysis...")
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{test_text[:50]}...'")
        
        try:
            response = requests.post(url, json={"text": test_text})
            if response.status_code == 200:
                result = response.json()
                print(f"Status: Success")
                
                # Check emotion analysis structure
                emotions = result.get('emotion_analysis', [])
                print(f"Emotions count: {len(emotions)}")
                
                if emotions:
                    print("Emotion Analysis:")
                    for emotion in emotions[:3]:  # Show top 3
                        label = emotion.get('label', 'unknown')
                        score = emotion.get('score', 0)
                        print(f"  - {label}: {score:.3f} ({score*100:.1f}%)")
                        
                        # Check for NaN or invalid scores
                        if score != score:  # NaN check
                            print(f"    WARNING: NaN score detected!")
                        elif not isinstance(score, (int, float)):
                            print(f"    WARNING: Invalid score type: {type(score)}")
                else:
                    print("  No emotions detected")
                    
            else:
                print(f"Status: Error {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Status: Exception - {e}")
        
        time.sleep(0.5)  # Small delay between requests

def test_full_audio_analysis():
    """Test with actual audio file to see the full pipeline"""
    
    url = "http://localhost:8000/analyze"
    
    # Try to find a test audio file
    import os
    audio_files = []
    for ext in ['*.wav', '*.mp3', '*.flac']:
        audio_files.extend(glob.glob(f"p:/python/New folder (2)/{ext}"))
    
    if audio_files:
        test_file = audio_files[0]
        print(f"\nTesting full pipeline with: {test_file}")
        
        try:
            with open(test_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(url, files=files)
                
            if response.status_code == 200:
                result = response.json()
                print("Full analysis result:")
                print(f"  Credibility Score: {result.get('credibility_score')}")
                print(f"  Confidence Level: {result.get('confidence_level')}")
                
                emotions = result.get('emotion_analysis', [])
                print(f"  Emotions: {len(emotions)} detected")
                
                for emotion in emotions[:3]:
                    label = emotion.get('label', 'unknown')
                    score = emotion.get('score', 0)
                    print(f"    - {label}: {score:.3f} (valid: {isinstance(score, (int, float)) and score == score})")
                    
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")
    else:
        print("No audio files found for testing")

if __name__ == "__main__":
    import glob
    
    print("Emotion Analysis Debug Test")
    print("=" * 50)
    
    # Test emotion analysis endpoint
    test_emotion_analysis()
    
    # Test full pipeline
    test_full_audio_analysis()
