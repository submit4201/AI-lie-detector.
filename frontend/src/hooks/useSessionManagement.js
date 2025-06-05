import { useState, useCallback } from 'react';

const API_URL = 'http://localhost:8000';

export const useSessionManagement = () => {
  const [sessionId, setSessionId] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([]);

  const createNewSession = useCallback(async () => {
    try {
      // Corrected endpoint to match backend
      const response = await fetch(`${API_URL}/session/new`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to create new session');
      }
      const data = await response.json();
      setSessionId(data.session_id);
      return data.session_id;
    } catch (error) {
      console.error("Error creating new session:", error);
      // Handle error appropriately in UI
      return null;
    }
  }, []);

  // Modified to accept sessionId and use correct endpoint
  const loadSessionHistory = useCallback(async (currentSessionId) => {
    if (!currentSessionId) return; // Do not attempt to load if no session ID
    try {
      const response = await fetch(`${API_URL}/session/${currentSessionId}/history`);
      if (!response.ok) {
        // Consider how to propagate this error if needed in UI beyond console
        throw new Error(`Failed to load session history for session ${currentSessionId}`);
      }
      const data = await response.json();
      // Assuming backend sends { session_id: "...", history: [...] }
      setSessionHistory(data.history || []); // Set to empty array if history is null/undefined
    } catch (error) {
      console.error("Error loading session history:", error);
      // Handle error appropriately in UI, e.g., by setting an error state if this hook managed one
    }
  }, []); // No dependencies needed as currentSessionId is an argument

  // Modified to call backend DELETE endpoint
  const clearCurrentSession = useCallback(async () => {
    const currentSessionId = sessionId; // Capture sessionId before clearing
    setSessionId(null); // Clear local sessionId immediately for UI responsiveness
    setSessionHistory([]); // Clear history in UI

    if (currentSessionId) {
      try {
        const response = await fetch(`${API_URL}/session/${currentSessionId}`, { method: 'DELETE' });
        if (!response.ok) {
          // Backend failed to delete or session already gone, log it.
          // UI already reflects session as cleared.
          console.warn(`Failed to delete session ${currentSessionId} on backend: ${response.status}`);
        }
        // Successfully deleted on backend or already cleared locally.
      } catch (error) {
        console.error("Error clearing session on backend:", error);
        // UI already reflects session as cleared.
      }
    }
    // Note: App.jsx's appClearCurrentSession also clears results and errors.
  }, [sessionId]); // Depends on sessionId to know what to delete

  return {
    sessionId,
    sessionHistory,
    createNewSession,
    loadSessionHistory,
    clearCurrentSession,
  };
};
