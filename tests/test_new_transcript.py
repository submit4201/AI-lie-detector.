#!/usr/bin/env python3
"""
Test the lie detector system with the new transcript provided by the user.
This will demonstrate the enhanced session insights functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.session_insights_service import SessionInsightsGenerator
from services.linguistic_service import LinguisticAnalysisService
import json

def test_new_transcript():
    """Test the new transcript with our enhanced session insights."""
    
    # The transcript provided by the user
    transcript = """You know, go with the. Using the chair, that's fine. I'm cool with that. I'm not gonna be long, just right by my house. So it's there in here, so. OK I'm. OK i'm ready now, so. You guys, we can finally woke up and saw that I was all loaded up and and and not gone yet. So I guess you got that opportunity right. What are you?"""
    
    print("=" * 80)
    print("LIE DETECTOR - ENHANCED SESSION INSIGHTS TEST")
    print("=" * 80)
    print(f"Transcript: {transcript}")
    print("\n" + "=" * 80)
    
    # Initialize services
    linguistic_service = LinguisticAnalysisService()
    insights_generator = SessionInsightsGenerator()
    
    # Perform linguistic analysis
    print("PERFORMING LINGUISTIC ANALYSIS...")
    linguistic_results = linguistic_service.analyze_text(transcript)
    
    print(f"Linguistic Analysis Results:")
    print(f"- Hesitation Count: {linguistic_results.get('hesitation_count', 0)}")
    print(f"- Speech Rate (WPM): {linguistic_results.get('speech_rate_wpm', 0)}")
    print(f"- Formality Score: {linguistic_results.get('formality_score', 0)}")
    print(f"- Deception Flags: {linguistic_results.get('deception_flags', [])}")
    
    # Create mock session data with this analysis
    session_data = [
        {
            'timestamp': '2025-06-05T10:00:00Z',
            'credibility_score': 65,  # Lower due to fragmented speech
            'emotion': 'uncertain',
            'risk_level': 'medium',
            'transcript': transcript,
            'hesitation_count': linguistic_results.get('hesitation_count', 8),
            'speech_rate_wpm': linguistic_results.get('speech_rate_wpm', 120),
            'formality_score': linguistic_results.get('formality_score', 3),
            'deception_flags': linguistic_results.get('deception_flags', ['fragmented_speech', 'hesitation_patterns'])
        }
    ]
    
    print("\n" + "=" * 80)
    print("GENERATING ENHANCED SESSION INSIGHTS...")
    print("=" * 80)
    
    # Generate insights
    insights = insights_generator.generate_insights(session_data)
    
    # Display insights in a formatted way
    for category, analysis in insights.items():
        print(f"\n[SEARCH] {category.upper().replace('_', ' ')}")
        print("-" * 60)
        print(f"[DATA] Analysis: {analysis}")
        print()
    
    print("=" * 80)
    print("SESSION INSIGHTS ANALYSIS COMPLETE")
    print("=" * 80)
    
    return insights

if __name__ == "__main__":
    test_new_transcript()
