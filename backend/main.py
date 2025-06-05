from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import routers from the api module
from backend.api import analysis_routes, session_routes, general_routes
# Config might be imported if needed for app settings, but not directly used in this minimal main.py
# from backend.config import SOME_APP_LEVEL_SETTING

# Set up logging (if not already configured elsewhere, e.g. by Uvicorn)
# This basicConfig should ideally be done once. If Uvicorn/Gunicorn handles logging, this might be redundant.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app_description = """
The AI Lie Detector API provides endpoints for analyzing audio content to detect potential deception.
It offers features like speech-to-text transcription, emotion analysis, and advanced AI-driven analysis using Google Gemini.
Session management is included to maintain conversation context.

**Key Features**:
- Audio analysis with deception indicators.
- Session-based conversation history and contextual analysis.
- Detailed breakdown of results including emotion, credibility, and linguistic patterns.
"""

app = FastAPI(
    title="AI Lie Detector API",
    version="1.0.2", # Updated version after refactor
    description=app_description,
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# Include routers from the API modules
# These routers should ideally have prefixes like /api/v1 to avoid clashes if static files are served from root
# For this refactor, keeping them at root to match original behavior.
app.include_router(general_routes.router, tags=["General"]) # Root path /
app.include_router(analysis_routes.router, tags=["Analysis"]) # Path /analyze
app.include_router(session_routes.router, tags=["Session Management"]) # Paths /session/*

# The root endpoint is now in general_routes.py.
# All specific endpoints like /analyze, /session/new etc. are moved to their respective route files.
# All Pydantic models are in models.py
# All service logic (ConversationHistory, audio processing, Gemini calls) is in service files.
# All config (API keys, pipeline init) is in config.py.

if __name__ == "__main__":
    import uvicorn
    # Uvicorn can also be run from the command line: uvicorn backend.main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
