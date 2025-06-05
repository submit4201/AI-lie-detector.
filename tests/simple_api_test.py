#!/usr/bin/env python3
"""
Simple test script to check API response
"""
import requests
import json

def test_api():
    url = "http://localhost:8000/analyze"
    
    try:
        with open("Recording.wav", "rb") as audio_file:
            files = {"audio": ("Recording.wav", audio_file, "audio/wav")}
            data = {"session_id": "test_session"}
            
            print("🚀 Testing API...")
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                
                # Check linguistic analysis
                if "linguistic_analysis" in result:
                    ling = result["linguistic_analysis"]
                    print(f"\n📊 Linguistic Analysis Found:")
                    print(f"  Word Count: {ling.get('word_count', 'N/A')}")
                    print(f"  Hesitation Count: {ling.get('hesitation_count', 'N/A')}")
                    print(f"  Filler Count: {ling.get('filler_count', 'N/A')}")
                    print(f"  Speech Rate: {ling.get('speech_rate_wpm', 'N/A')} WPM")
                    print(f"  Formality Score: {ling.get('formality_score', 'N/A')}")
                    print(f"  Complexity Score: {ling.get('complexity_score', 'N/A')}")
                    
                    # Save for inspection
                    with open("debug_response.json", "w") as f:
                        json.dump(result, f, indent=2)
                    print(f"\n💾 Full response saved to debug_response.json")
                else:
                    print("❌ No linguistic_analysis in response")
                    print(f"Available keys: {list(result.keys())}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
3