import React from 'react';
import { Button } from "@/components/ui/button"; // Shadcn/ui Button component
import { Card, CardContent } from "@/components/ui/card"; // Shadcn/ui Card components
import { UploadCloud, Mic, Loader2, StopCircle, Download, Settings } from "lucide-react"; // Icons

/**
 * @component ControlPanel
 * @description Provides UI controls for audio input (file upload, recording),
 * session management (new, clear, view history), and initiating analysis.
 * It also displays loading states, progress, and error messages.
 *
 * @param {object} props - The properties passed to the component.
 * @param {File|null} props.file - The currently selected audio file.
 * @param {function} props.setFile - Function to update the selected file state.
 * @param {boolean} props.loading - Boolean indicating if an analysis is in progress.
 * @param {boolean} props.recording - Boolean indicating if audio recording is active.
 * @param {string|null} props.error - Error message string, if any.
 * @param {number} props.analysisProgress - Current progress of the analysis (0-100).
 * @param {string|null} props.sessionId - The current active session ID.
 * @param {Array<object>} props.sessionHistory - Array of past analysis entries for the current session.
 * @param {boolean} props.showSessionPanel - Boolean to control visibility of the session history panel.
 * @param {function} props.setShowSessionPanel - Function to toggle session history panel visibility.
 * @param {function} props.createNewSession - Async function to create a new session.
 * @param {function} props.clearCurrentSession - Async function to clear the current session.
 * @param {function} props.handleUpload - Async function to handle audio file upload and analysis.
 * @param {function} props.startRecording - Async function to start audio recording.
 * @param {function} props.stopRecording - Function to stop audio recording.
 * @param {function} props.exportResults - Function to export current analysis results.
 * @param {object|null} props.result - The current analysis result object, used to conditionally show export button.
 * @param {function} props.validateAudioFile - Function to validate an audio file before setting it.
 * @returns {JSX.Element} The ControlPanel component.
 */
const ControlPanel = ({
  file,
  setFile,
  loading,
  recording,
  error,
  analysisProgress,
  sessionId,
  sessionHistory,
  showSessionPanel,
  setShowSessionPanel,
  createNewSession,
  clearCurrentSession,
  handleUpload,
  startRecording,
  stopRecording,
  exportResults,
  result, // Used to conditionally render the Export button
}) => {
  return (
    // Main card container for the control panel with styling.
    <Card className="mb-8 bg-white/10 backdrop-blur-md border-white/20 shadow-2xl">
      <CardContent className="p-8">
        {/* Flex container for layout of control panel sections. */}
        <div className="flex flex-col gap-6">

          {/* Session Management Section */}
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-semibold text-lg">🗂️ Conversation Session</h3>
              {/* Button to toggle visibility of the session history panel */}
              <Button
                onClick={() => setShowSessionPanel(!showSessionPanel)}
                variant="outline"
                size="sm"
                className="text-white border-white/30 hover:bg-white/10"
              >
                <Settings className="w-4 h-4 mr-2" />
                {showSessionPanel ? 'Hide' : 'Show'} Session Details
              </Button>
            </div>

            {/* Display current session ID and history summary */}
            <div className="flex flex-wrap items-center gap-3">
              {sessionId ? (
                <div className="flex items-center gap-3">
                  <div className="bg-green-500/20 border border-green-400/30 rounded-lg px-3 py-2">
                    <span className="text-green-200 text-sm">
                      📝 Session Active: {sessionId.substring(0, 8)}... {/* Show truncated session ID */}
                    </span>
                  </div>
                  {sessionHistory.length > 0 && (
                    <div className="text-white/70 text-sm">
                      {sessionHistory.length} analysis{sessionHistory.length !== 1 ? 'es' : ''} in this session.
                    </div>
                  )}
                </div>
              ) : (
                // Message shown when no session is active.
                <div className="text-white/50 text-sm">No active session. A new session will be created on the first analysis.</div>
              )}

              {/* Session action buttons (New Session, Clear Session) */}
              <div className="flex gap-2 ml-auto">
                <Button
                  onClick={createNewSession}
                  size="sm"
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                  disabled={loading} // Disable if loading to prevent conflicts
                >
                  New Session
                </Button>
                {/* Clear Session button only shown if a session is active */}
                {sessionId && (
                  <Button
                    onClick={clearCurrentSession}
                    size="sm"
                    variant="outline"
                    className="text-red-400 border-red-400/30 hover:bg-red-500/10"
                    disabled={loading} // Disable if loading
                  >
                    Clear Session
                  </Button>
                )}
              </div>
            </div>

            {/* Collapsible Session History Panel */}
            {showSessionPanel && sessionHistory.length > 0 && (
              <div className="mt-4 pt-4 border-t border-white/20">
                <h4 className="text-white font-medium mb-3">Session History Quick View</h4>
                {/* Scrollable container for session history items */}
                <div className="space-y-2 max-h-32 overflow-y-auto pr-2"> {/* Added pr-2 for scrollbar spacing */}
                  {sessionHistory.map((entry, index) => (
                    // Individual history item card
                    <div key={entry.timestamp?.toString() + index} className="bg-black/40 rounded-lg p-3 text-sm"> {/* Use a more robust key if available */}
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-white/80 font-medium">Analysis #{entry.analysis_number || index + 1}</span>
                        <span className="text-white/50 text-xs">
                          {/* Format timestamp to be more readable */}
                          {entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString() : 'N/A'}
                        </span>
                      </div>
                      <p className="text-gray-300 text-xs truncate mb-1" title={entry.transcript}>
                        "{entry.transcript ? entry.transcript.substring(0, 80) + (entry.transcript.length > 80 ? "..." : "") : "Transcript not available"}"
                      </p>
                      {/* Display key metrics from the analysis summary of the history item */}
                      <div className="flex gap-2 flex-wrap">
                        {entry.analysis?.credibility_score !== undefined && ( // Check for undefined explicitly for scores that can be 0
                          <span className={`text-xs px-2 py-0.5 rounded-full ${ // Adjusted padding and rounded-full
                            entry.analysis.credibility_score >= 70 ? 'bg-green-500/30 text-green-200' :
                            entry.analysis.credibility_score >= 40 ? 'bg-yellow-500/30 text-yellow-200' :
                            'bg-red-500/30 text-red-200'
                          }`}>
                            Credibility: {entry.analysis.credibility_score}/100
                          </span>
                        )}
                        {entry.analysis?.overall_risk && (
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            entry.analysis.overall_risk === 'high' ? 'bg-red-500/30 text-red-200' :
                            entry.analysis.overall_risk === 'medium' ? 'bg-yellow-500/30 text-yellow-200' :
                            'bg-green-500/30 text-green-200' // Assuming 'low' or other as green
                          }`}>
                            Risk: {entry.analysis.overall_risk}
                          </span>
                        )}
                         {entry.analysis?.top_emotion && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-purple-500/30 text-purple-200">
                            Emotion: {entry.analysis.top_emotion}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {showSessionPanel && sessionHistory.length === 0 && (
                 <p className="text-sm text-white/50 mt-3">No analysis history in this session yet.</p>
            )}
          </div>

          {/* Audio File Input Section */}
          <div className="flex flex-col lg:flex-row gap-6">
            <div className="flex-1">
              <label htmlFor="audioFile" className="block text-white font-medium mb-3">Upload Audio File</label>
              {/* Styled file input for audio files */}
              <input
                id="audioFile" // Added id for label association
                type="file"
                accept="audio/*" // Accepts all audio types, specific validation might be in `validateAudioFile`
                onChange={(e) => {
                    const selectedFile = e.target.files[0];
                    if (selectedFile) {
                        // Validate before setting: This part was missing in the original snippet,
                        // but it's good practice to validate before `setFile`.
                        // However, `appHandleUpload` in App.jsx also calls validateAudioFile if a file is passed directly.
                        // To avoid double validation or ensure it's always done, logic might need adjustment.
                        // For now, assuming `setFile` is the primary way to get file into `useAudioProcessing` state
                        // and `handleUpload` in `App.jsx` uses that state.
                        setFile(selectedFile);
                    }
                }}
                className="w-full border border-white/30 bg-white/10 backdrop-blur-sm text-white p-4 rounded-xl
                         file:mr-4 file:py-3 file:px-6 file:rounded-lg file:border-0 file:text-sm file:font-semibold
                         file:bg-gradient-to-r file:from-blue-500 file:to-purple-500 file:text-white
                         hover:file:from-blue-600 hover:file:to-purple-600 transition-all duration-300 cursor-pointer"
              />
            </div>
          </div>

          {/* Action Buttons Section: Analyze, Record, Export */}
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Analyze Audio Button */}
            <Button
              onClick={() => handleUpload(file)} // Calls the upload handler from App.jsx
              disabled={!file || loading || recording} // Disabled if no file, or if loading/recording
              className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50"
            >
              {loading && !recording ? <Loader2 className="w-5 h-5 animate-spin" /> : <UploadCloud className="w-5 h-5" />}
              {loading && !recording ? "Analyzing..." : "Analyze Selected Audio"}
            </Button>

            {/* Record Audio / Stop Recording Button */}
            <Button
              onClick={recording ? stopRecording : startRecording}
              disabled={loading && !recording} // Disabled if analyzing and not already recording
              className={`flex-1 flex items-center justify-center gap-2 font-semibold py-3 px-6 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 ${
                recording
                  ? 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white' // Red when recording
                  : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white' // Green when not recording
              }`}
            >
              {recording ? <StopCircle className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              {recording ? "Stop Recording" : "Record New Audio"}
            </Button>

            {/* Export Results Button: Only shown if there are results to export */}
            {result && (
              <Button
                onClick={exportResults}
                disabled={loading} // Disable if loading
                className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50"
              >
                <Download className="w-5 h-5" />
                Export Analysis Results
              </Button>
            )}
          </div>

          {/* Analysis Progress Indicator: Shown when loading and progress is > 0 */}
          {loading && analysisProgress > 0 && (
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-xl p-4 mt-4">
              <div className="flex items-center gap-3">
                <Loader2 className="w-5 h-5 animate-spin text-blue-300" />
                <span className="text-white font-medium">Analysis in progress: {analysisProgress}%</span>
                {/* Basic progress bar */}
                <div className="w-full bg-white/20 rounded-full h-2.5">
                  <div className="bg-blue-500 h-2.5 rounded-full transition-all duration-300" style={{ width: `${analysisProgress}%` }}></div>
                </div>
              </div>
            </div>
          )}

          {/* Error Display Area: Shown if an error message exists */}
          {error && (
            <div className="bg-red-600/30 backdrop-blur-sm border border-red-500/50 rounded-xl p-4 mt-4">
              <p className="text-red-200 font-medium text-center">⚠️ Error: {error}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ControlPanel;
