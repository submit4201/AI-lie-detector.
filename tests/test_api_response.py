#!/usr/bin/env python3
"""
Test script to check actual API response structure
"""
import requests
import json

def test_api_response():
    # Test with an actual audio file
    url = "http://localhost:8000/analyze"
    try:        # Use the Recording.wav file
        with open("Recording.wav", "rb") as audio_file:
            files = {"audio": ("Recording.wav", audio_file, "audio/wav")}
            data = {"session_id": "test_session"}
            
            print("[LAUNCH] Sending request to API...")
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("[PASS] API Response received successfully!")
                print("\n[DATA] Checking linguistic_analysis structure:")
                
                if "linguistic_analysis" in result:
                    ling_analysis = result["linguistic_analysis"]
                    print(f"  ✓ linguistic_analysis present: {type(ling_analysis)}")
                    
                    # Check quantitative metrics
                    quantitative_fields = [
                        "word_count", "hesitation_count", "qualifier_count", 
                        "certainty_count", "filler_count", "repetition_count",
                        "formality_score", "complexity_score", "avg_word_length",
                        "avg_words_per_sentence", "sentence_count", "speech_rate_wpm",
                        "hesitation_rate", "confidence_ratio"
                    ]
                    
                    print("\n[PROGRESS] Quantitative Metrics:")
                    for field in quantitative_fields:
                        value = ling_analysis.get(field, "MISSING")
                        print(f"    {field}: {value}")
                    
                    print("\n[NOTE] Descriptive Fields:")
                    descriptive_fields = ["speech_patterns", "word_choice", "emotional_consistency", "detail_level"]
                    for field in descriptive_fields:
                        value = ling_analysis.get(field, "MISSING")
                        print(f"    {field}: {value[:100]}..." if isinstance(value, str) and len(value) > 100 else f"    {field}: {value}")
                
                else:
                    print("  [FAIL] linguistic_analysis field missing from response!")
                    print(f"  Available fields: {list(result.keys())}")
                
                # Save full response for inspection
                with open("api_response_debug.json", "w") as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Full response saved to api_response_debug.json")
                
            else:
                print(f"[FAIL] API request failed with status {response.status_code}")
                print(f"Error: {response.text}")
                
    except FileNotFoundError:
        print("[FAIL] Recording.wav not found! Please ensure the audio file exists.")
    except Exception as e:
        print(f"[FAIL] Error testing API: {e}")

if __name__ == "__main__":
    test_api_response()
