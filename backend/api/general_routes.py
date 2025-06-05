from fastapi import APIRouter

router = APIRouter()

@router.get(
    "/",
    tags=["General"],
    summary="API Root/Health Check",
    description="Basic health check endpoint to confirm the API is running."
)
async def root():
    # In main.py, this used app.version.
    # If app instance is not easily available here, a static message or version from elsewhere is fine.
    # For simplicity, returning a static message. If version is needed, it might require passing app or config.
    return {"message": "AI Lie Detector API is running"}
