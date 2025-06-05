#!/usr/bin/env python3

import requests
import json

def test_analyze_endpoint():
    """Test the /analyze endpoint with the test audio file"""
    
    # API endpoint
    url = "http://localhost:8000/analyze"
    
    # Prepare the file and form data
    try:      
        with open("test_audio.wav", "rb") as audio_file:
            files = {
                "audio": ("test_audio.wav", audio_file, "audio/wav")
            }
            data = {
                "session_id": None  # Let the server create a new session
            }
            
            print("🔍 Testing /analyze endpoint...")
            print(f"📤 Sending request to: {url}")
            print(f"📁 File: test_audio.wav")
            print(f"🔧 Analysis type: comprehensive")
            print("=" * 60)
            
            # Make the request
            response = requests.post(url, files=files, data=data, timeout=60)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS: Analysis completed!")
                result = response.json()
                
                # Pretty print the structured response
                print("\n🏗️  STRUCTURED OUTPUT VALIDATION TEST:")
                print("=" * 60)
                
                # Check all required fields
                required_fields = [
                    'speaker_transcripts', 'red_flags_per_speaker', 'credibility_score',
                    'confidence_level', 'gemini_summary', 'recommendations', 
                    'linguistic_analysis', 'risk_assessment'
                ]
                
                print("📋 Required Fields Check:")
                for field in required_fields:
                    status = "✅" if field in result else "❌"
                    print(f"   {status} {field}")
                
                print(f"\n📈 Credibility Score: {result.get('credibility_score', 'Missing')}")
                print(f"🎯 Confidence Level: {result.get('confidence_level', 'Missing')}")
                print(f"⚠️  Risk Assessment: {result.get('risk_assessment', {}).get('risk_level', 'Missing')}")
                
                # Display summary sections
                gemini_summary = result.get('gemini_summary', {})
                if gemini_summary:
                    print(f"\n🧠 AI Analysis Summary:")
                    for key, value in gemini_summary.items():
                        if value and value != "Not determined":
                            print(f"   • {key.replace('_', ' ').title()}: {value}")
                
                print(f"\n📖 Full Response Structure:")
                print(json.dumps(result, indent=2))
                
            else:
                print(f"❌ ERROR: Request failed with status {response.status_code}")
                print(f"📄 Response: {response.text}")
                
    except FileNotFoundError:
        print("❌ ERROR: test_audio.wav file not found!")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Request failed - {e}")
    except Exception as e:
        print(f"❌ ERROR: Unexpected error - {e}")

if __name__ == "__main__":
    test_analyze_endpoint()
