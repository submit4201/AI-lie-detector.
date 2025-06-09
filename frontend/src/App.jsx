import React, { useState, useCallback, useEffect } from "react";
// UI Components
import Header from "./components/App/Header";
import ControlPanel from "./components/App/ControlPanel";
import ResultsDisplay from "./components/App/ResultsDisplay";
// Custom Hooks for state management and logic
import { useSessionManagement } from "./hooks/useSessionManagement";
import { useAudioProcessing } from "./hooks/useAudioProcessing";
import { useAnalysisResults } from "./hooks/useAnalysisResults";

/**
 * @file App.jsx
 * @description
 * This is the main root component for the AI Lie Detector application.
 * It orchestrates the overall application structure, state management, and
 * interactions between various child components and custom hooks.
 *
 * Key responsibilities include:
 * - Managing session state (session ID, history) via `useSessionManagement`.
 * - Handling audio input (file upload, recording) and processing logic via `useAudioProcessing`.
 * - Managing and displaying analysis results via `useAnalysisResults`.
 * - Coordinating actions like starting a new session, uploading audio for analysis, and clearing session data.
 * - Rendering the main UI layout including Header, ControlPanel, and ResultsDisplay.
 */
export default function App() {
  // State for controlling the visibility of the session management panel in ControlPanel.
  const [showSessionPanel, setShowSessionPanel] = useState(false);

  // --- Custom Hook Integrations ---

  // `useSessionManagement` hook: Manages session-related state and actions.
  // - sessionId: The current active session ID.
  // - sessionHistory: Array of past analysis summaries for the current session.
  // - hookCreateNewSession: Function to create a new session (renamed to avoid naming conflicts).
  // - loadSessionHistory: Function to fetch history for a given session ID.
  // - clearCurrentSession: Function to clear current session data and ID.
  const {
    sessionId,
    sessionHistory,
    createNewSession: hookCreateNewSession,
    loadSessionHistory,
    clearCurrentSession,
  } = useSessionManagement();

  // `useAudioProcessing` hook: Handles audio file selection, recording, validation, and API upload.
  // - file, setFile: State for the selected audio file.
  // - recording: Boolean indicating if audio recording is in progress.
  // - loading: Boolean indicating if an analysis or upload is in progress.
  // - audioError, setAudioError: State for managing errors related to audio processing/upload.
  // - analysisProgress: Numerical value (0-100) representing analysis progress (if available).
  // - validateAudioFile: Function to perform client-side validation of an audio file.
  // - hookHandleUpload: Function to handle the actual upload and analysis request to the backend (renamed).
  // - startRecording, stopRecording: Functions to control audio recording.
  // It receives a getter for sessionId to ensure the latest ID is used for uploads,
  // and the session creation function to initiate a new session if needed during upload.
  const {
    file,
    setFile,
    recording,
    loading,
    error: audioError,
    setError: setAudioError,
    analysisProgress,
    validateAudioFile,
    handleUpload: hookHandleUpload,
    startRecording,
    stopRecording,
  } = useAudioProcessing(
    () => sessionId, // Pass a getter for sessionId to ensure the hook uses the current value.
    hookCreateNewSession  // Pass the session creation function from useSessionManagement.
  );

  // `useAnalysisResults` hook: Manages the state and utility functions for analysis results.
  // - result: The current analysis result object to be displayed.
  // - updateAnalysisResult: Function to update the 'result' state with new analysis data.
  // - exportResults: Function to handle exporting analysis results (e.g., as JSON or PDF).
  // - getCredibilityColor, getCredibilityLabel, formatConfidenceLevel: Utility functions for formatting/displaying results.
  // - parseGeminiAnalysis: Utility to parse complex Gemini analysis parts if needed (may not be used if API returns structured data).
  const {
    result,
    updateAnalysisResult,
    exportResults,
    getCredibilityColor,
    getCredibilityLabel,
    parseGeminiAnalysis,
    formatConfidenceLevel,
  } = useAnalysisResults();

  // Centralized error display logic. Currently, it only reflects audio processing errors.
  // Session management errors are logged to the console within the `useSessionManagement` hook.
  // This could be expanded to include other error sources if needed.
  const displayError = audioError;

  // --- Effects ---

  // useEffect to automatically load session history when `sessionId` changes.
  // This ensures that if a session is restored or a new one is created and its ID becomes available,
  // its history is fetched and displayed.
  useEffect(() => {
    if (sessionId) {
      loadSessionHistory(sessionId);
    }
  }, [sessionId, loadSessionHistory]); // Dependencies: runs when sessionId or loadSessionHistory function changes.

  // --- Callback Functions ---
  // These functions wrap hook actions to provide additional App-level logic,
  // such as coordinating state updates between different hooks or UI elements.

  /**
   * Handles the audio upload process by coordinating `useAudioProcessing` and `useAnalysisResults`.
   * It first validates the file (if provided directly, e.g., from recording),
   * then calls the `handleUpload` from `useAudioProcessing`.
   * If analysis is successful, it updates the results using `useAnalysisResults` and reloads session history.
   * @param {File} [fileToUpload] - Optional. The audio file to upload. If not provided,
   *                                the `useAudioProcessing` hook will use its internally managed `file` state.
   */
  const appHandleUpload = useCallback(async (fileToUpload) => {
    // If a file is passed directly (e.g., from recording completion), set it in the audio hook.
    if (fileToUpload) {
        const validationError = validateAudioFile(fileToUpload); // Validate the file first.
        if (validationError) { // `validateAudioFile` returns an error message string if invalid, null otherwise.
            setAudioError(validationError); // Set audio error state if validation fails.
            return; // Stop the upload process.
        }
        setFile(fileToUpload); // Set the file in `useAudioProcessing` state. This might trigger its internal effects.
    }

    // Call the `handleUpload` from `useAudioProcessing`.
    // This function is responsible for the actual API call and returns analysis data or null on error.
    const analysisData = await hookHandleUpload();

    if (analysisData) {
      updateAnalysisResult(analysisData); // Update the main results state with the new data.
      if (sessionId) { // If there's an active session, reload its history to include this new analysis.
        loadSessionHistory(sessionId);
      }
    }
    // If `analysisData` is null, it means `hookHandleUpload` encountered an error,
    // and `useAudioProcessing` should have already set its own error state (`audioError`).
  }, [hookHandleUpload, updateAnalysisResult, loadSessionHistory, sessionId, setFile, validateAudioFile, setAudioError]);


  /**
   * Creates a new session, clearing any previous errors and results from the UI.
   * It calls the `createNewSession` function from `useSessionManagement`.
   * If session creation fails at the hook level, it sets an error message in the App's state.
   */
   const appCreateNewSession = useCallback(async () => {
    setAudioError(null); // Clear any existing audio/upload errors.
    updateAnalysisResult(null); // Clear any previously displayed analysis results.

    const newSessionId = await hookCreateNewSession(); // Call the hook function.
    if (newSessionId) {
      // `useEffect` listening to `sessionId` will automatically load history for the new session.
      // (Or, if it's a brand new session, history will be empty).
    } else {
      // If the hook failed to create a session (e.g., API error in the hook), set an App-level error.
      setAudioError("Failed to create a new session. Please check your connection or try again later.");
    }
  }, [hookCreateNewSession, updateAnalysisResult, setAudioError]);

  /**
   * Clears the current session data from both the `useSessionManagement` hook
   * and local UI states (results, errors).
   */
  const appClearCurrentSession = useCallback(async () => {
    await clearCurrentSession(); // This function in `useSessionManagement` sets its `sessionId` to null.
    updateAnalysisResult(null);  // Clear displayed results.
    setAudioError(null);         // Clear any displayed errors.
    // The `sessionHistory` in `useSessionManagement` will likely be cleared or become empty
    // as a result of `clearCurrentSession` or the subsequent `useEffect` reacting to `sessionId` becoming null.
  }, [clearCurrentSession, updateAnalysisResult, setAudioError]);

  // --- JSX Rendering ---
  return (
    // Main application container with a gradient background.
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Application Header Component */}
      <Header />

      {/* Main content area with padding and max width */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* ControlPanel: Handles user inputs for audio, recording, session management, and initiating analysis. */}
        <ControlPanel
          file={file} // Current file state from useAudioProcessing
          setFile={setFile} // Function to update the file state
          loading={loading} // Loading state for analysis
          recording={recording} // Recording state
          error={displayError} // Error message to display
          setError={setAudioError} // Function to set audio errors
          analysisProgress={analysisProgress} // Analysis progress value
          sessionId={sessionId} // Current session ID
          sessionHistory={sessionHistory} // Current session's history
          showSessionPanel={showSessionPanel} // State for session panel visibility
          setShowSessionPanel={setShowSessionPanel} // Function to toggle session panel
          createNewSession={appCreateNewSession} // App-level new session function
          clearCurrentSession={appClearCurrentSession} // App-level clear session function
          handleUpload={appHandleUpload} // App-level upload handler
          startRecording={startRecording} // Function to start recording
          stopRecording={stopRecording} // Function to stop recording
          exportResults={exportResults} // Function to export results
          result={result} // Current analysis result for potential display/actions in ControlPanel
          validateAudioFile={validateAudioFile} // File validation function
        />
        {/* ResultsDisplay: Shows the detailed analysis results. */}
        <ResultsDisplay
          result={result} // The main analysis result object
          parseGeminiAnalysis={parseGeminiAnalysis} // Utility for parsing Gemini response parts
          getCredibilityColor={getCredibilityColor} // Utility for credibility color coding
          getCredibilityLabel={getCredibilityLabel} // Utility for credibility label
          formatConfidenceLevel={formatConfidenceLevel} // Utility for formatting confidence level
          sessionHistory={sessionHistory} // Session history, potentially for context in results
        />
      </div>
    </div>
  );
}
