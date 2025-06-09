import { useState, useCallback } from 'react';

// Base URL for the backend API.
// Consider moving this to an environment variable for better configuration management.
const API_URL = 'http://localhost:8000';

/**
 * @hook useSessionManagement
 * @description Manages the client-side state and interactions for user sessions.
 * This includes creating new sessions, fetching session history, and clearing sessions
 * by making requests to the backend session management endpoints.
 *
 * @returns {object} An object containing:
 *  - `sessionId`: The current active session ID (string|null).
 *  - `sessionHistory`: An array of historical analysis items for the current session.
 *  - `createNewSession`: Async function to request a new session from the backend.
 *  - `loadSessionHistory`: Async function to fetch the history for a given session ID.
 *  - `clearCurrentSession`: Async function to clear the current session locally and request deletion on the backend.
 */
export const useSessionManagement = () => {
  // State for the current session ID. Null if no active session.
  const [sessionId, setSessionId] = useState(null);
  // State for storing the history of analyses for the current session.
  const [sessionHistory, setSessionHistory] = useState([]);

  /**
   * Creates a new session by calling the backend API.
   * On success, updates the `sessionId` state with the new ID.
   * @async
   * @returns {Promise<string|null>} The new session ID if successful, otherwise null.
   */
  const createNewSession = useCallback(async () => {
    try {
      // Make a POST request to the backend's /session/new endpoint.
      const response = await fetch(`${API_URL}/session/new`, { method: 'POST' });
      if (!response.ok) {
        // If the response is not OK (e.g., 4xx, 5xx), throw an error.
        const errorData = await response.json().catch(() => null); // Try to get error detail
        throw new Error(errorData?.detail || 'Failed to create new session from API.');
      }
      const data = await response.json(); // Parse the JSON response.
      setSessionId(data.session_id);      // Update the local sessionId state.
      setSessionHistory([]);              // Reset history for the new session.
      console.log("New session created with ID:", data.session_id);
      return data.session_id;             // Return the new session ID.
    } catch (error) {
      console.error("Error creating new session:", error.message);
      // In a real app, might set an error state here to be displayed in the UI.
      return null; // Indicate failure.
    }
  }, []); // Empty dependency array as this callback doesn't depend on props/state from its own scope.

  /**
   * Loads the analysis history for a given session ID from the backend.
   * Updates the `sessionHistory` state on success.
   * @async
   * @param {string} currentSessionId - The ID of the session whose history is to be loaded.
   */
  const loadSessionHistory = useCallback(async (currentSessionId) => {
    // Do not attempt to load if no session ID is provided.
    if (!currentSessionId) {
      // console.log("loadSessionHistory called without a session ID.");
      setSessionHistory([]); // Ensure history is empty if no session ID
      return;
    }
    try {
      // Make a GET request to /session/{sessionId}/history.
      const response = await fetch(`${API_URL}/session/${currentSessionId}/history`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        // If session not found on backend (404), it's not necessarily a critical client error,
        // but means history is empty. Other errors are more problematic.
        if (response.status === 404) {
          console.warn(`Session history not found for session ${currentSessionId} (404). Setting local history to empty.`);
          setSessionHistory([]);
        } else {
          throw new Error(errorData?.detail || `Failed to load session history for session ${currentSessionId}. Status: ${response.status}`);
        }
      } else {
        const data = await response.json();
        // Backend is expected to return an object like { session_id: "...", history: [...] }.
        setSessionHistory(data.history || []); // Update history state. Default to empty array if history is missing.
        // console.log(`Session history loaded for ${currentSessionId}:`, data.history);
      }
    } catch (error) {
      console.error("Error loading session history:", error.message);
      // Consider setting an error state for UI feedback.
      setSessionHistory([]); // Clear history on error to avoid displaying stale data.
    }
  }, []); // Empty dependency array as `currentSessionId` is an argument.

  /**
   * Clears the current session state locally (sessionId, sessionHistory)
   * and attempts to delete the session on the backend.
   * @async
   */
  const clearCurrentSession = useCallback(async () => {
    const currentSessionIdToDelete = sessionId; // Capture current sessionId before clearing it locally.

    // Optimistically update UI by clearing local session state immediately.
    setSessionId(null);
    setSessionHistory([]);
    console.log("Local session cleared. Attempting backend deletion for ID:", currentSessionIdToDelete);

    if (currentSessionIdToDelete) {
      try {
        // Make a DELETE request to /session/{sessionId}.
        const response = await fetch(`${API_URL}/session/${currentSessionIdToDelete}`, { method: 'DELETE' });
        if (!response.ok) {
          // If backend fails to delete (e.g., already deleted, server error), log it.
          // The UI already reflects the session as cleared, so this is mainly for backend consistency.
          const errorData = await response.json().catch(() => null);
          console.warn(`Failed to delete session ${currentSessionIdToDelete} on backend. Status: ${response.status}. Detail: ${errorData?.detail}`);
        } else {
          console.log(`Session ${currentSessionIdToDelete} successfully deleted on backend.`);
        }
      } catch (error) {
        console.error("Error clearing session on backend for ID " + currentSessionIdToDelete + ":", error.message);
        // UI already reflects session as cleared. This error is for backend cleanup.
      }
    }
    // Note: The main App.jsx component's `appClearCurrentSession` wrapper also handles
    // clearing other app-level states like analysis results and errors.
  }, [sessionId]); // Depends on `sessionId` to know which session to attempt to delete on backend.

  // Expose session state and management functions.
  return {
    sessionId,
    sessionHistory,
    createNewSession,
    loadSessionHistory,
    clearCurrentSession,
  };
};
