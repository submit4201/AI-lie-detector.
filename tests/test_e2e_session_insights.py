#!/usr/bin/env python3
"""
End-to-end test for Session Insights with real API calls
"""

import requests
import time
import json

# Test configuration
BACKEND_URL = "http://localhost:8000"
TEST_AUDIO_FILE = "test_audio.wav"

def test_session_insights_e2e():
    print("🧪 Starting End-to-End Session Insights Test")
    print("=" * 50)
      # Step 1: Create a new session
    print("📋 Step 1: Creating new session...")
    session_response = requests.post(f"{BACKEND_URL}/session/new")
    if session_response.status_code == 200:
        session_data = session_response.json()
        session_id = session_data["session_id"]
        print(f"✅ Session created: {session_id}")
    else:
        print(f"❌ Failed to create session: {session_response.status_code}")
        return
    
    # Step 2: Upload multiple audio files to build session history
    analyses = []
    
    print(f"\n📁 Step 2: Uploading audio files to session {session_id}...")
    
    # Check if test audio file exists
    import os
    if not os.path.exists(TEST_AUDIO_FILE):
        print(f"⚠️  Test audio file '{TEST_AUDIO_FILE}' not found. Using 'Recording.wav' instead.")
        TEST_AUDIO_FILE = "Recording.wav"
        if not os.path.exists(TEST_AUDIO_FILE):
            print("❌ No test audio files found. Cannot proceed with test.")
            return
    
    # Simulate multiple analyses in the same session
    for i in range(3):
        print(f"\n🔍 Analysis #{i+1}...")
        
        try:
            with open(TEST_AUDIO_FILE, 'rb') as audio_file:
                # Include session_id in the request
                files = {'audio': audio_file}
                data = {'session_id': session_id}
                
                response = requests.post(
                    f"{BACKEND_URL}/analyze", 
                    files=files,
                    data=data,
                    timeout=120  # 2 minute timeout for analysis
                )
                
                if response.status_code == 200:
                    analysis_result = response.json()
                    analyses.append(analysis_result)
                    
                    print(f"  ✅ Analysis #{i+1} completed")
                    print(f"  📊 Credibility Score: {analysis_result.get('credibility_score', 'N/A')}")
                    print(f"  🎯 Confidence Level: {analysis_result.get('confidence_level', 'N/A')}")
                    
                    # Check for session insights (should appear from analysis #2 onwards)
                    if 'session_insights' in analysis_result:
                        print(f"  🔍 Session Insights Available: YES")
                        insights = analysis_result['session_insights']
                        print(f"    - Consistency Analysis: {'✓' if insights.get('consistency_analysis') else '✗'}")
                        print(f"    - Behavioral Evolution: {'✓' if insights.get('behavioral_evolution') else '✗'}")
                        print(f"    - Risk Trajectory: {'✓' if insights.get('risk_trajectory') else '✗'}")
                        print(f"    - Conversation Dynamics: {'✓' if insights.get('conversation_dynamics') else '✗'}")
                    else:
                        print(f"  🔍 Session Insights Available: NO")
                
                else:
                    print(f"  ❌ Analysis #{i+1} failed: {response.status_code}")
                    print(f"  Error: {response.text}")
                    
        except FileNotFoundError:
            print(f"  ❌ Audio file not found: {TEST_AUDIO_FILE}")
            return
        except Exception as e:
            print(f"  ❌ Error during analysis #{i+1}: {str(e)}")
            return
        
        # Small delay between analyses
        time.sleep(2)
    
    # Step 3: Get session history
    print(f"\n📚 Step 3: Retrieving session history...")
    history_response = requests.get(f"{BACKEND_URL}/session/{session_id}/history")
    if history_response.status_code == 200:
        history_data = history_response.json()
        print(f"✅ Session history retrieved: {len(history_data['history'])} entries")
    else:
        print(f"❌ Failed to get session history: {history_response.status_code}")
    
    # Step 4: Display detailed session insights from the last analysis
    print(f"\n🎯 Step 4: Session Insights Summary")
    print("=" * 50)
    
    if len(analyses) >= 2:  # Should have insights from 2nd analysis onwards
        last_analysis = analyses[-1]
        
        if 'session_insights' in last_analysis:
            insights = last_analysis['session_insights']
            
            print("🔍 CONSISTENCY ANALYSIS:")
            print(f"   {insights.get('consistency_analysis', 'Not available')}")
            print()
            
            print("📊 BEHAVIORAL EVOLUTION:")
            print(f"   {insights.get('behavioral_evolution', 'Not available')}")
            print()
            
            print("⚠️ RISK TRAJECTORY:")
            print(f"   {insights.get('risk_trajectory', 'Not available')}")
            print()
            
            print("💬 CONVERSATION DYNAMICS:")
            print(f"   {insights.get('conversation_dynamics', 'Not available')}")
            print()
            
            print("✅ SESSION INSIGHTS TEST COMPLETED SUCCESSFULLY!")
            print(f"📈 Generated intelligent insights for session with {len(analyses)} analyses")
            
        else:
            print("❌ No session insights found in the last analysis")
            print("This indicates the session insights generation may not be working properly")
            
    else:
        print("⚠️  Not enough analyses completed to generate session insights")
    
    print("\n" + "=" * 50)
    print("🏁 End-to-End Test Complete")

if __name__ == "__main__":
    test_session_insights_e2e()
