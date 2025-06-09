"""
Application Configuration Module

This file centralizes the configuration for the application, including:
1.  API Keys: Securely loads API keys (e.g., for Google Gemini) from environment variables.
2.  Model Initialization: Initializes machine learning models, such as the Hugging Face
    emotion classification pipeline, making them available as global resources.

It's crucial to handle sensitive information like API keys securely, preferably through
environment variables, rather than hardcoding them.
"""
import os
import logging # For logging informational messages and errors
from transformers import pipeline

# Get a logger for this module
logger = logging.getLogger(__name__)

# --- Gemini API Key Configuration ---
# IMPORTANT: It is highly recommended to set your actual Google Gemini API key as an
# environment variable named "GEMINI_API_KEY" for security and flexibility.
# Avoid hardcoding the API key directly in the code, especially in production environments.
# The fallback key provided below is a placeholder and WILL NOT WORK.
# If the GEMINI_API_KEY environment variable is not set, Gemini API calls will fail.
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "AIzaSyB5KbPaVXPYkUeShTEE82fgpZiLiLl7YyM" # Placeholder default key
)

if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSyB5KbPaVXPYkUeShTEE82fgpZiLiLl7YyM":
    # This warning is crucial for developers to ensure the API key is correctly set up.
    logger.warning(
        "GEMINI_API_KEY is not set or is using the default placeholder value. "
        "Calls to the Gemini API will likely fail. Please set the GEMINI_API_KEY environment variable."
    )

# --- Hugging Face Emotion Classifier Pipeline Initialization ---
# Configuration for the emotion classification pipeline.
# Model: "j-hartmann/emotion-english-distilroberta-base" is a RoBERTa-based model
# fine-tuned for emotion classification in English text. It typically identifies 7 emotions:
# anger, disgust, fear, joy, neutral, sadness, surprise.
# - `return_all_scores=True`: Ensures scores for all 7 emotions are returned.
# - `top_k=7`: When `return_all_scores=True`, `top_k` might seem redundant if the model
#   only has 7 classes. However, it was present in the original configuration.
#   If the model had more classes than `top_k`, `top_k` would limit the output.
#   For this specific model with 7 emotions, `return_all_scores=True` is the key parameter
#   to get all emotion scores. `top_k=7` is kept for consistency with original setup
#   but `return_all_scores=True` is the more direct way to get all scores for this model.
EMOTION_CLASSIFIER_CONFIG = {
    "task": "text-classification", # Renamed from "pipeline_task" for clarity with `pipeline` function
    "model": "j-hartmann/emotion-english-distilroberta-base",
    "top_k": 7, # Return up to 7 top results (effectively all for this model)
    "return_all_scores": True # Ensure all scores are returned
}

EMOTION_CLASSIFIER = None # Initialize as None
try:
    # Initialize the pipeline using the defined configuration.
    # The `**` operator unpacks the dictionary into keyword arguments.
    EMOTION_CLASSIFIER = pipeline(**EMOTION_CLASSIFIER_CONFIG)
    logger.info(f"Hugging Face emotion classifier pipeline initialized successfully with model: {EMOTION_CLASSIFIER_CONFIG['model']}")
except Exception as e:
    # Log the error and set the classifier to None if initialization fails.
    # This allows the application to start but with emotion analysis functionality disabled.
    logger.error(
        f"Error initializing Hugging Face emotion classifier (model: {EMOTION_CLASSIFIER_CONFIG['model']}): {e}",
        exc_info=True # Include exception info for debugging
    )
    logger.warning(
        "Emotion analysis will not be available. "
        "Please ensure the model is accessible and the Hugging Face transformers library is correctly installed."
    )
    EMOTION_CLASSIFIER = None # Explicitly set to None on failure
