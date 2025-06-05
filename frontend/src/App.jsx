import React, { useState, useCallback, useEffect } from "react";
// Removed Button import as it's not used directly in App.jsx
// Removed duplicate React imports
import Header from "./components/App/Header";
import ControlPanel from "./components/App/ControlPanel";
import ResultsDisplay from "./components/App/ResultsDisplay";
import { useSessionManagement } from "./hooks/useSessionManagement";
import { useAudioProcessing } from "./hooks/useAudioProcessing";
import { useAnalysisResults } from "./hooks/useAnalysisResults";

export default function App() {
  const [showSessionPanel, setShowSessionPanel] = useState(false);

  const {
    sessionId,
    sessionHistory,
    createNewSession: hookCreateNewSession, // Renamed to avoid conflict if any local var was named createNewSession
    loadSessionHistory,
    clearCurrentSession,
  } = useSessionManagement();

  const {
    file,
    setFile,
    recording,
    loading,
    error: audioError, // Renamed to distinguish from other potential errors
    setError: setAudioError,
    analysisProgress,
    validateAudioFile, // Assuming useAudioProcessing exposes this
    handleUpload: hookHandleUpload,
    startRecording,
    stopRecording,
  } = useAudioProcessing(
    () => sessionId, // Pass getter for sessionId
    hookCreateNewSession // Pass session creation function
  );

  const {
    result,
    updateAnalysisResult,
    exportResults,
    getCredibilityColor,
    getCredibilityLabel,
    parseGeminiAnalysis,
    formatConfidenceLevel, // Added from hook
  } = useAnalysisResults();

  // Combined error for display
  const displayError = audioError; // For now, only using audio error. Session errors are console logged in the hook.

  // Effect to load session history when a session ID becomes available or changes
  useEffect(() => {
    if (sessionId) {
      loadSessionHistory(sessionId);
    }
  }, [sessionId, loadSessionHistory]);

  // Modified handleUpload to bridge useAudioProcessing and useAnalysisResults
  const appHandleUpload = useCallback(async (fileToUpload) => {
    // If a file is passed directly (e.g. from recording), set it in audio hook first
    if (fileToUpload) {
        // Validate first
        const validationError = validateAudioFile(fileToUpload);
        if (validationError) { // validateAudioFile returns error string or null
            setAudioError(validationError);
            return;
        }
        setFile(fileToUpload); // This will trigger the useEffect in useAudioProcessing if its own 'file' state changes, or simply set it for its handleUpload
    }
    // Now call the hook's handleUpload.
    // It uses its own 'file' state, which should be set by setFile above or via its own input.
    const analysisData = await hookHandleUpload();
    if (analysisData) {
      updateAnalysisResult(analysisData);
      if (sessionId) { // Reload history after successful analysis
        loadSessionHistory(sessionId);
      }
    }
    // If analysisData is null, useAudioProcessing hook has already set its error state.
  }, [hookHandleUpload, updateAnalysisResult, loadSessionHistory, sessionId, setFile, validateAudioFile, setAudioError]);


  // Wrapper for createNewSession to also clear results and errors
   const appCreateNewSession = useCallback(async () => {
    setAudioError(null); // Clear previous errors
    updateAnalysisResult(null); // Clear previous results
    const newSessionId = await hookCreateNewSession();
    if (newSessionId) {
      // Session history will be loaded by useEffect
    } else {
      setAudioError("Failed to create a new session. Please try again."); // Set error in App state if hook fails
    }
  }, [hookCreateNewSession, updateAnalysisResult, setAudioError]);

  // Wrapper for clearCurrentSession to also clear results and errors
  const appClearCurrentSession = useCallback(async () => {
    await clearCurrentSession(); // This function in the hook already sets sessionId to null
    updateAnalysisResult(null);
    setAudioError(null);
    // sessionHistory will be updated by the hook or an effect listening to sessionId
  }, [clearCurrentSession, updateAnalysisResult, setAudioError]);


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Header />

      <div className="max-w-7xl mx-auto px-6 py-8">
        <ControlPanel
          file={file}
          setFile={setFile} // Pass setFile from useAudioProcessing
          loading={loading}
          recording={recording}
          error={displayError} // Use the combined/selected error
          setError={setAudioError} // Pass setError from useAudioProcessing
          analysisProgress={analysisProgress}
          sessionId={sessionId}
          sessionHistory={sessionHistory}
          showSessionPanel={showSessionPanel}
          setShowSessionPanel={setShowSessionPanel}
          createNewSession={appCreateNewSession} // Use wrapped version
          clearCurrentSession={appClearCurrentSession} // Use wrapped version
          handleUpload={appHandleUpload} // Use wrapped version
          startRecording={startRecording}
          stopRecording={stopRecording}
          exportResults={exportResults} // From useAnalysisResults
          result={result} // From useAnalysisResults
          validateAudioFile={validateAudioFile} // From useAudioProcessing
        />
        <ResultsDisplay
          result={result} // From useAnalysisResults
          parseGeminiAnalysis={parseGeminiAnalysis} // From useAnalysisResults
          getCredibilityColor={getCredibilityColor} // From useAnalysisResults
          getCredibilityLabel={getCredibilityLabel} // From useAnalysisResults
          formatConfidenceLevel={formatConfidenceLevel} // From useAnalysisResults
          sessionHistory={sessionHistory} // From useSessionManagement
        />
      </div>
    </div>
  );
}
