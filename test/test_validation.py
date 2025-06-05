#!/usr/bin/env python3

import requests
import json

def test_analyze_with_mock_transcript():
    """Test the structured output validation by mocking a successful transcript"""
    
    # We'll create a quick test by temporarily modifying the query_gemini function
    # to return a test response without calling the actual Gemini API
    
    print("🔍 Testing structured output validation system...")
    print("📊 Creating mock Gemini response to test validation...")
    print("=" * 60)
    
    # Test with mock data that has the list-to-string conversion issue
    mock_gemini_response = {
        "speaker_transcripts": {"Speaker 1": "This is a test transcript"},
        "red_flags_per_speaker": {"Speaker 1": ["Inconsistent details", "Vague responses"]},
        "credibility_score": 75,
        "confidence_level": "high",
        "gemini_summary": {
            "tone": "The speaker appears nervous and hesitant",
            "motivation": "Appears to be withholding information",
            "credibility": "Moderate credibility with some concerns",
            "emotional_state": "Anxious and defensive",
            "communication_style": "Evasive and indirect",
            "key_concerns": ["Lack of specific details", "Inconsistent timeline"],  # This is a list!
            "strengths": ["Clear speech", "Responsive to questions"]  # This is also a list!
        },
        "recommendations": [
            "Follow up with specific questions about timeline",
            "Request documentation to verify claims"
        ],
        "linguistic_analysis": {
            "speech_patterns": "Frequent pauses and hesitations",
            "word_choice": "Uses qualifiers and uncertain language",
            "emotional_consistency": "Emotions match claimed stress level",
            "detail_level": "Lacks specific details in key areas"
        },
        "risk_assessment": {
            "overall_risk": "medium",
            "risk_factors": ["Information gaps", "Inconsistent details"],
            "mitigation_suggestions": ["Verify claims", "Follow up interview"]
        }
    }
      # Test the validation function directly
    import sys
    sys.path.append('backend')
    from services.gemini_service import validate_and_structure_gemini_response
    
    test_transcript = "This is a test transcript for validation"
    validated_response = validate_and_structure_gemini_response(mock_gemini_response, test_transcript)
    
    print("✅ Validation completed! Checking results...")
    print("=" * 60)
    
    # Check if list-to-string conversion worked
    key_concerns = validated_response.get('gemini_summary', {}).get('key_concerns', '')
    strengths = validated_response.get('gemini_summary', {}).get('strengths', '')
    
    print(f"🔧 List-to-String Conversion Test:")
    print(f"   Original key_concerns type: {type(mock_gemini_response['gemini_summary']['key_concerns'])}")
    print(f"   Validated key_concerns type: {type(key_concerns)}")
    print(f"   Validated key_concerns value: {key_concerns}")
    print()
    print(f"   Original strengths type: {type(mock_gemini_response['gemini_summary']['strengths'])}")
    print(f"   Validated strengths type: {type(strengths)}")
    print(f"   Validated strengths value: {strengths}")
    print()
    
    # Check all required fields
    required_fields = [
        'speaker_transcripts', 'red_flags_per_speaker', 'credibility_score',
        'confidence_level', 'gemini_summary', 'recommendations', 
        'linguistic_analysis', 'risk_assessment'
    ]
    
    print("📋 Required Fields Validation:")
    all_present = True
    for field in required_fields:
        status = "✅" if field in validated_response else "❌"
        if field not in validated_response:
            all_present = False
        print(f"   {status} {field}")
    
    print()
    print(f"🎯 Credibility Score: {validated_response.get('credibility_score')} (type: {type(validated_response.get('credibility_score'))})")
    print(f"📊 Confidence Level: {validated_response.get('confidence_level')}")
    print(f"⚠️  Risk Level: {validated_response.get('risk_assessment', {}).get('overall_risk')}")
    
    if all_present and isinstance(key_concerns, str) and isinstance(strengths, str):
        print("\n🎉 SUCCESS: Structured output validation system working correctly!")
        print("✅ All required fields present")
        print("✅ List-to-string conversion working")
        print("✅ Data types validated")
    else:
        print("\n❌ ISSUES DETECTED in validation system")
    
    print("\n📖 Complete Validated Response:")
    print(json.dumps(validated_response, indent=2))

if __name__ == "__main__":
    test_analyze_with_mock_transcript()
