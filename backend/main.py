"""
Main application file for the AI Lie Detector API.

This file initializes the FastAPI application, sets up logging,
configures Cross-Origin Resource Sharing (CORS) middleware,
and includes the API routers for different functionalities such as
analysis, session management, and general endpoints.

The application metadata (title, version, description, contact, license)
is also defined here for the OpenAPI documentation.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import routers from the api module
from api.analysis_routes import router as analysis_router
from api.session_routes import router as session_router  
from api.general_routes import router as general_router

# --- Logging Setup ---
# Configure basic logging for the application.
# INFO level and above will be logged.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Logger for this main module

# --- API Description ---
# Detailed description for the OpenAPI documentation.
app_description = """
The AI Lie Detector API provides endpoints for analyzing audio content to detect potential deception.
It offers features like speech-to-text transcription, emotion analysis, and advanced AI-driven insights using Google Gemini.
Session management is included to maintain conversation context.

**Key Features**:
- Audio analysis with deception indicators and detailed speech pattern insights.
- Session-based conversation history and contextual analysis to track consistency and evolution.
- Comprehensive results including emotion scores, credibility assessments, linguistic patterns, and risk factors.
- Mock data endpoint for frontend testing and integration.
"""

# --- FastAPI Application Instantiation ---
# Initialize the FastAPI application with metadata for the OpenAPI documentation.
app = FastAPI(
    title="AI Lie Detector API",
    version="1.0.1", # API version
    description=app_description, # Detailed description from above
    contact={ # Contact information for API support
        "name": "API Support Team",
        "email": "support@example-liedetector.com", # Placeholder email
    },
    license_info={ # License information
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT", # Link to the license text
    }
)

# --- CORS Middleware Configuration ---
# Configure CORS (Cross-Origin Resource Sharing) to allow requests from any origin.
# This is common for APIs that are intended to be used by web applications hosted on different domains.
# For production, it's recommended to restrict `allow_origins` to specific domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Change to a list of specific domains for production.
    allow_credentials=True,  # Allows cookies to be included in cross-origin requests.
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.).
    allow_headers=["*"],  # Allows all headers.
)

# --- API Router Inclusion ---
# Include the routers defined in other modules to organize the API endpoints.
# Each router handles a specific aspect of the API.

# General routes (e.g., health check, test endpoints)
app.include_router(general_router, tags=["General"])

# Analysis routes (e.g., /analyze endpoint)
app.include_router(analysis_router, tags=["Analysis"]) # No prefix, /analyze will be directly under root.

# Session management routes (e.g., /session/new, /session/{id}/history)
# These routes are prefixed with "/session".
app.include_router(session_router, prefix="/session", tags=["Session Management"])

# --- Main Execution Block ---
# This block runs when the script is executed directly (e.g., `python main.py`).
# It starts the Uvicorn ASGI server to serve the FastAPI application.
# Useful for development and testing. For production, a more robust setup (e.g., Gunicorn with Uvicorn workers) is typical.
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn development server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000) # Runs the app on all available network interfaces on port 8000.
