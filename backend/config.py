import os
from transformers import pipeline

# Gemini API Key Configuration
# IMPORTANT: It's highly recommended to set your actual API key as an environment variable
# and not hardcode it here, especially for production.
# The fallback key "your_fallback_key_here_or_None" is a placeholder and should be replaced
# or removed if you ensure the environment variable is always set.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyB5KbPaVXPYkUeShTEE82fgpZiLiLl7YyM") # Replace with a secure fallback or None

# Initialize the emotion classifier pipeline
# This makes it available for import in other modules, ensuring it's loaded once.
try:
    EMOTION_CLASSIFIER = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=7, # Changed from return_all_scores=True to top_k=7 as per main.py
        return_all_scores=True # Kept return_all_scores as it was in main.py, top_k might be redundant if all scores are returned
    )
except Exception as e:
    # Log this error appropriately in a real application
    print(f"Error initializing Hugging Face emotion classifier: {e}")
    print("Emotion analysis will not be available. Ensure the model is accessible and transformers library is correctly installed.")
    EMOTION_CLASSIFIER = None

if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSyB5KbPaVXPYkUeShTEE82fgpZiLiLl7YyM": # Check against the specific placeholder
    # Log this warning appropriately in a real application
    print("Warning: GEMINI_API_KEY is not set or is using the default placeholder. Gemini API calls may fail.")

# Note on top_k vs return_all_scores:
# In Hugging Face pipelines, if return_all_scores=True, it returns scores for all classes.
# top_k then would mean it returns all scores but perhaps limits the list to k items if k is less than total classes.
# The original main.py had `top_k=7, return_all_scores=True`. This usually means it will return all scores for the 7 classes
# if the model has more than 7 classes, or all classes if it has <= 7.
# For 'j-hartmann/emotion-english-distilroberta-base', it typically has 7 emotions (anger, disgust, fear, joy, neutral, sadness, surprise).
# So, `return_all_scores=True` effectively does what `top_k=7` would do if the model indeed has exactly 7 classes.
# Keeping both for consistency with the original code's apparent intent.
# If the model "j-hartmann/emotion-english-distilroberta-base" has exactly 7 labels,
# then `return_all_scores=True` is sufficient, and `top_k=7` is redundant but harmless.
# If it had, say, 20 labels, `top_k=7` would restrict the output to the top 7, even with `return_all_scores=True`.
# For this specific model, it outputs 7 emotions, so `return_all_scores=True` is fine.
# I'll keep `return_all_scores=True` and remove `top_k=7` for clarity as it's effectively returning all.
# Re-checking main.py: it was `top_k=None` implicitly if not set, and `return_all_scores=True` was used.
# The transformers docs say:
# top_k (:obj:`int`, `optional`, defaults to 1): The number of top labels that will be returned by the pipeline.
# If the provided number is `None`, the number of labels is determined by the model's configuration.
# return_all_scores (:obj:`bool`, `optional`, defaults to :obj:`False`): Whether or not to return all scores of all labels.
# The original code in main.py had:
# emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=7, return_all_scores=True)
# This is slightly confusing. If return_all_scores is True, top_k is usually ignored or means something else.
# For clarity and standard usage, typically you use one or the other.
# Given the model has 7 emotions, `return_all_scores=True` will return all 7.
# Let's stick to what was in main.py for now.
EMOTION_CLASSIFIER_CONFIG = {
    "pipeline_task": "text-classification",
    "model_name": "j-hartmann/emotion-english-distilroberta-base",
    "top_k": 7, # As it was in main.py
    "return_all_scores": True # As it was in main.py
}

EMOTION_CLASSIFIER = pipeline(
    EMOTION_CLASSIFIER_CONFIG["pipeline_task"],
    model=EMOTION_CLASSIFIER_CONFIG["model_name"],
    top_k=EMOTION_CLASSIFIER_CONFIG["top_k"],
    return_all_scores=EMOTION_CLASSIFIER_CONFIG["return_all_scores"]
)
