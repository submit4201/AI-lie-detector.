"""
API Routes for Session Management

This module defines FastAPI routes related to creating, retrieving,
and managing conversation sessions. It uses the `conversation_history_service`
to interact with session data.
"""
from fastapi import APIRouter, HTTPException, Path, Depends
import logging

from models import (
    NewSessionResponse,
    SessionHistoryResponse,
    SessionHistoryItem, # Needed for constructing the list of history items in the response.
    DeleteSessionResponse,
    ErrorResponse # Used in response definitions for error cases.
)
from services.session_service import conversation_history_service # Singleton instance

# Logger for this module
logger = logging.getLogger(__name__)

# Router for session-related endpoints, will be included in the main FastAPI app.
router = APIRouter()

@router.post(
    "/new",
    response_model=NewSessionResponse,
    tags=["Session Management"],
    summary="Create a New Conversation Session",
    description="Initializes a new conversation session and returns a unique session ID, which can be used for subsequent analysis calls to maintain context.",
    responses={
        200: {"description": "Session created successfully."},
        500: {"model": ErrorResponse, "description": "Internal server error occurred during session creation."}
    }
)
async def create_new_session_endpoint():
    """
    Creates a new conversation session.

    Invokes the `conversation_history_service` to generate a new session ID
    and initialize the session structure.

    Returns:
        NewSessionResponse: Contains the newly created session ID and a success message.

    Raises:
        HTTPException: If any error occurs during session creation.
    """
    try:
        # Get or create a session. Since no ID is passed, it will always create a new one.
        session_id = conversation_history_service.get_or_create_session()
        logger.info(f"New session created successfully with ID: {session_id}")
        return NewSessionResponse(session_id=session_id, message="New session created successfully.")
    except Exception as e:
        logger.error(f"Failed to create new session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create a new session due to an internal error: {str(e)}")

@router.get(
    "/{session_id}/history",
    response_model=SessionHistoryResponse,
    tags=["Session Management"],
    summary="Retrieve Session Conversation History",
    description="Retrieves the summarized conversation and analysis history for a given session ID. This history includes timestamps, transcripts, and key analysis takeaways for each segment analyzed within the session.",
    responses={
        200: {"description": "Session history retrieved successfully."},
        404: {"model": ErrorResponse, "description": "Session ID not found."},
        500: {"model": ErrorResponse, "description": "Internal server error retrieving session history."}
    }
)
async def get_session_history_endpoint(
    session_id: str = Path(..., description="The unique identifier of the session whose history is to be retrieved.")
):
    """
    Retrieves the analysis history for a specific session.

    Args:
        session_id: The ID of the session, passed as a URL path parameter.

    Returns:
        SessionHistoryResponse: Contains the session ID and a list of its history items.

    Raises:
        HTTPException:
            - 404 if the session ID is not found.
            - 500 if any other error occurs.
    """
    try:
        # First, check if the session actually exists to provide a specific 404 error.
        if session_id not in conversation_history_service.sessions:
            logger.warning(f"Attempt to retrieve history for non-existent session ID: {session_id}")
            raise HTTPException(status_code=404, detail=f"Session ID '{session_id}' not found.")

        # Retrieve history data using the service; this data is already summarized for API responses.
        history_items_data = conversation_history_service.get_session_history_for_api(session_id)

        # Convert the raw data for each history item into a Pydantic model instance.
        # This ensures the response conforms to the defined `SessionHistoryItem` schema.
        history_items = [SessionHistoryItem(**item) for item in history_items_data]
        logger.info(f"Retrieved {len(history_items)} history items for session ID: {session_id}")

        return SessionHistoryResponse(session_id=session_id, history=history_items)
    except HTTPException:
        raise # Re-raise HTTPExceptions (like the 404) directly.
    except Exception as e:
        logger.error(f"Failed to retrieve session history for ID '{session_id}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session history due to an internal error: {str(e)}")


@router.delete(
    "/{session_id}",
    response_model=DeleteSessionResponse,
    tags=["Session Management"],
    summary="Delete a Conversation Session",
    description="Deletes all data associated with a given session ID, including its conversation history. This action is irreversible.",
    responses={
        200: {"description": "Session deleted successfully."},
        404: {"model": ErrorResponse, "description": "Session ID not found or already deleted."},
        500: {"model": ErrorResponse, "description": "Internal server error during session deletion."}
    }
)
async def delete_session_endpoint(
    session_id: str = Path(..., description="The unique identifier of the session to be deleted.")
):
    """
    Deletes a specific conversation session and its history.

    Args:
        session_id: The ID of the session to delete, passed as a URL path parameter.

    Returns:
        DeleteSessionResponse: Contains the ID of the deleted session and a success message.

    Raises:
        HTTPException:
            - 404 if the session ID is not found.
            - 500 if any other error occurs.
    """
    try:
        # Attempt to delete the session using the service.
        # The service method returns True on success, False if the session didn't exist.
        if not conversation_history_service.delete_session(session_id):
            logger.warning(f"Attempt to delete non-existent session ID: {session_id}")
            raise HTTPException(status_code=404, detail=f"Session ID '{session_id}' not found or was already deleted.")

        logger.info(f"Session ID '{session_id}' deleted successfully.")
        return DeleteSessionResponse(session_id=session_id, message="Session deleted successfully.")
    except HTTPException:
        raise # Re-raise HTTPExceptions (like the 404) directly.
    except Exception as e:
        logger.error(f"Failed to delete session ID '{session_id}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete session due to an internal error: {str(e)}")
