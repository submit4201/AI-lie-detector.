import React from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { UploadCloud, Mic, Loader2, StopCircle, Download, Settings } from "lucide-react";

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
  result // Added result to conditionally render Export button
}) => {
  return (
    <Card className="mb-8 bg-white/10 backdrop-blur-md border-white/20 shadow-2xl">
      <CardContent className="p-8">
        <div className="flex flex-col gap-6">
          {/* Session Management */}
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-semibold text-lg">🗂️ Conversation Session</h3>
              <Button
                onClick={() => setShowSessionPanel(!showSessionPanel)}
                variant="outline"
                size="sm"
                className="text-white border-white/30 hover:bg-white/10"
              >
                <Settings className="w-4 h-4 mr-2" />
                {showSessionPanel ? 'Hide' : 'Show'} Session
              </Button>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {sessionId ? (
                <div className="flex items-center gap-3">
                  <div className="bg-green-500/20 border border-green-400/30 rounded-lg px-3 py-2">
                    <span className="text-green-200 text-sm">
                      📝 Session Active: {sessionId.substring(0, 8)}...
                    </span>
                  </div>
                  {sessionHistory.length > 0 && (
                    <div className="text-white/70 text-sm">
                      {sessionHistory.length} analysis{sessionHistory.length !== 1 ? 'es' : ''} in session
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-white/50 text-sm">No active session - will create new session on first analysis</div>
              )}

              <div className="flex gap-2 ml-auto">
                <Button
                  onClick={createNewSession}
                  size="sm"
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  New Session
                </Button>
                {sessionId && (
                  <Button
                    onClick={clearCurrentSession}
                    size="sm"
                    variant="outline"
                    className="text-red-400 border-red-400/30 hover:bg-red-500/10"
                  >
                    Clear Session
                  </Button>
                )}
              </div>
            </div>

            {showSessionPanel && sessionHistory.length > 0 && (
              <div className="mt-4 pt-4 border-t border-white/20">
                <h4 className="text-white font-medium mb-3">Session History</h4>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {sessionHistory.map((entry, index) => (
                    <div key={index} className="bg-black/40 rounded-lg p-3 text-sm">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-white/80">Analysis #{index + 1}</span>
                        <span className="text-white/50 text-xs">
                          {new Date(entry.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-gray-300 text-xs truncate mb-1">
                        "{entry.transcript.substring(0, 80)}..."
                      </p>
                      <div className="flex gap-2">
                        {entry.analysis_summary.credibility_score && (
                          <span className={`text-xs px-2 py-1 rounded ${
                            entry.analysis_summary.credibility_score >= 70 ? 'bg-green-500/20 text-green-300' :
                            entry.analysis_summary.credibility_score >= 40 ? 'bg-yellow-500/20 text-yellow-300' :
                            'bg-red-500/20 text-red-300'
                          }`}>
                            {entry.analysis_summary.credibility_score}/100
                          </span>
                        )}
                        {entry.analysis_summary.overall_risk && (
                          <span className={`text-xs px-2 py-1 rounded ${
                            entry.analysis_summary.overall_risk === 'high' ? 'bg-red-500/20 text-red-300' :
                            entry.analysis_summary.overall_risk === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                            'bg-green-500/20 text-green-300'
                          }`}>
                            {entry.analysis_summary.overall_risk} risk
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex flex-col lg:flex-row gap-6">
            <div className="flex-1">
              <label className="block text-white font-medium mb-3">Upload Audio File</label>
              <input
                type="file"
                accept="audio/*"
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full border border-white/30 bg-white/10 backdrop-blur-sm text-white p-4 rounded-xl
                         file:mr-4 file:py-3 file:px-6 file:rounded-lg file:border-0 file:text-sm file:font-semibold
                         file:bg-gradient-to-r file:from-blue-500 file:to-purple-500 file:text-white
                         hover:file:from-blue-600 hover:file:to-purple-600 transition-all duration-300"
              />
            </div>
          </div>

          <div className="flex flex-col lg:flex-row gap-4">
            <Button
              onClick={() => handleUpload(file)}
              disabled={!file || loading}
              className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <UploadCloud className="w-5 h-5" />}
              {loading ? "Analyzing..." : "Analyze Audio"}
            </Button>

            <Button
              onClick={recording ? stopRecording : startRecording}
              disabled={loading}
              className={`flex items-center gap-2 font-semibold py-3 px-6 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl ${
                recording
                  ? 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white'
                  : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white'
              }`}
            >
              {recording ? <StopCircle className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              {recording ? "Stop Recording" : "Record Audio"}
            </Button>

            {result && (
              <Button
                onClick={exportResults}
                className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                <Download className="w-5 h-5" />
                Export Results
              </Button>
            )}
          </div>

          {/* Progress Indicator */}
          {loading && analysisProgress && (
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-4">
              <div className="flex items-center gap-3">
                <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
                <span className="text-white font-medium">{analysisProgress}</span>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-xl p-4">
              <p className="text-red-200 font-medium">⚠️ {error}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ControlPanel;
