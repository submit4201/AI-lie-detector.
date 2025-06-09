#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath('.'))

# Test pydantic models directly
from backend.models import LinguisticAnalysis, RiskAssessment, GeminiSummary, SessionInsights, AudioQualityMetrics
from pydantic import ValidationError

def test_model_validation():
    """Test what happens when we try to create models with empty dicts"""
    
    print("Testing LinguisticAnalysis with empty dict...")
    try:
        linguistic = LinguisticAnalysis(**{})
        print("[PASS] LinguisticAnalysis created successfully")
    except ValidationError as e:
        print(f"[FAIL] LinguisticAnalysis validation error:")
        print(f"Number of errors: {len(e.errors())}")
        missing_fields = [error['loc'][0] for error in e.errors() if error['type'] == 'missing']
        print(f"Missing required fields: {missing_fields}")
    
    print("\nTesting RiskAssessment with empty dict...")
    try:
        risk = RiskAssessment(**{})
        print("[PASS] RiskAssessment created successfully")
    except ValidationError as e:
        print(f"[FAIL] RiskAssessment validation error:")
        missing_fields = [error['loc'][0] for error in e.errors() if error['type'] == 'missing']
        print(f"Missing required fields: {missing_fields}")
    
    print("\nTesting GeminiSummary with empty dict...")
    try:
        summary = GeminiSummary(**{})
        print("[PASS] GeminiSummary created successfully")
    except ValidationError as e:
        print(f"[FAIL] GeminiSummary validation error:")
        missing_fields = [error['loc'][0] for error in e.errors() if error['type'] == 'missing']
        print(f"Missing required fields: {missing_fields}")
    
    print("\nTesting SessionInsights with empty dict...")
    try:
        insights = SessionInsights(**{})
        print("[PASS] SessionInsights created successfully")
    except ValidationError as e:
        print(f"[FAIL] SessionInsights validation error:")
        missing_fields = [error['loc'][0] for error in e.errors() if error['type'] == 'missing']
        print(f"Missing required fields: {missing_fields}")
    
    print("\nTesting AudioQualityMetrics with empty dict...")
    try:
        audio_quality = AudioQualityMetrics(**{})
        print("[PASS] AudioQualityMetrics created successfully")
    except ValidationError as e:
        print(f"[FAIL] AudioQualityMetrics validation error:")
        missing_fields = [error['loc'][0] for error in e.errors() if error['type'] == 'missing']
        print(f"Missing required fields: {missing_fields}")

if __name__ == "__main__":
    test_model_validation()
