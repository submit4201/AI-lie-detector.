import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { UploadCloud, Mic, Loader2, StopCircle, Download, Settings } from "lucide-react";

export default function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [error, setError] = useState(null);
  const [analysisProgress, setAnalysisProgress] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([]);
  const [showSessionPanel, setShowSessionPanel] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const getCredibilityColor = (score) => {
    if (score >= 70) return '#4ade80' // green
    if (score >= 40) return '#fbbf24' // yellow
    return '#ef4444' // red
  }

  const getCredibilityLabel = (score) => {
    if (score >= 70) return 'High Credibility'
    if (score >= 40) return 'Moderate Credibility'
    return 'Low Credibility'
  }

  // Enhanced parsing helper functions
  const parseGeminiAnalysis = (analysis) => {
    if (!analysis) return null;
    
    if (typeof analysis === 'object' && !Array.isArray(analysis)) {
      return analysis;
    }
    
    if (typeof analysis === 'string') {
      try {
        const cleanedAnalysis = analysis
          .replace(/```json\s*/g, '')
          .replace(/```\s*/g, '')
          .trim();
        
        return JSON.parse(cleanedAnalysis);
      } catch (error) {
        console.warn('Failed to parse Gemini analysis:', error);
        return { gemini_summary: analysis, error: 'Failed to parse structured response' };
      }
    }
    
    return null;
  };

  const formatConfidenceLevel = (score) => {
    if (score >= 90) return { level: 'Very High', color: 'text-green-800', bgColor: 'bg-green-100' };
    if (score >= 70) return { level: 'High', color: 'text-green-700', bgColor: 'bg-green-50' };
    if (score >= 50) return { level: 'Moderate', color: 'text-yellow-700', bgColor: 'bg-yellow-50' };
    if (score >= 30) return { level: 'Low', color: 'text-orange-700', bgColor: 'bg-orange-50' };
    return { level: 'Very Low', color: 'text-red-700', bgColor: 'bg-red-50' };
  };

  // Audio file validation
  const validateAudioFile = (file) => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg', 'audio/webm'];
    
    if (!allowedTypes.includes(file.type)) {
      return { valid: false, error: 'Invalid file type. Please upload WAV, MP3, or OGG files.' };
    }
    
    if (file.size > maxSize) {
      return { valid: false, error: 'File too large. Maximum size is 10MB.' };
    }
      return { valid: true };
  };

  // Session management functions
  const createNewSession = async () => {
    try {
      const response = await fetch('http://localhost:8000/session/new', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        setSessionHistory([]);
        setResult(null);
        setError(null);
        return data.session_id;
      }
    } catch (err) {
      console.error('Failed to create session:', err);
    }
    return null;
  };

  const loadSessionHistory = async (currentSessionId) => {
    if (!currentSessionId) return;
    
    try {
      const response = await fetch(`http://localhost:8000/session/${currentSessionId}/history`);
      if (response.ok) {
        const data = await response.json();
        setSessionHistory(data.history || []);
      }
    } catch (err) {
      console.error('Failed to load session history:', err);
    }
  };

  const clearCurrentSession = async () => {
    if (!sessionId) return;
    
    try {
      await fetch(`http://localhost:8000/session/${sessionId}`, {
        method: 'DELETE'
      });
      setSessionId(null);
      setSessionHistory([]);
      setResult(null);
    } catch (err) {
      console.error('Failed to clear session:', err);
    }
  };

  const handleUpload = async (uploadFile) => {
    if (!uploadFile) {
      setError("No file selected");
      return;
    }

    // Validate audio file
    const validation = validateAudioFile(uploadFile);
    if (!validation.valid) {
      setError(validation.error);
      return;
    }    setLoading(true);
    setError(null);
    setResult(null);
    setAnalysisProgress('Uploading audio file...');
    
    // Create or use existing session
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      currentSessionId = await createNewSession();
      if (!currentSessionId) {
        setError("Failed to create analysis session");
        setLoading(false);
        return;
      }
    }
    
    const formData = new FormData();
    formData.append("audio", uploadFile);
    formData.append("session_id", currentSessionId);

    try {
      console.log("Sending request to backend...");
      setAnalysisProgress('Processing audio and transcribing...');
      
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });
      
      console.log("Response status:", res.status);
      setAnalysisProgress('Analyzing speech patterns...');
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Server error (${res.status}): ${errorText}`);
      }
      
      setAnalysisProgress('Running AI analysis...');
      const data = await res.json();
      console.log("Received data:", data);
      setAnalysisProgress('Analysis complete!');
        setTimeout(() => {
        setResult(data);
        setAnalysisProgress('');
        // Load updated session history
        loadSessionHistory(currentSessionId);
      }, 500);
      
      if (data.error) {
        setError(data.error);
      }
    } catch (err) {
      console.error("Upload error:", err);
      setError(`Upload failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        const file = new File([audioBlob], "recording.wav", { type: "audio/wav" });
        setFile(file);
        handleUpload(file);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setRecording(true);
    } catch (err) {
      console.error(err);
      setError("Microphone access denied or unavailable");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };
  // Export functionality
  const exportResults = () => {
    if (!result) return;
    
    const exportData = {
      timestamp: new Date().toISOString(),
      session_id: result.session_id,
      analysis: {
        transcript: result.transcript,
        audio_quality: result.audio_quality,
        emotion_analysis: result.emotion_analysis,
        deception_flags: result.deception_flags,
        // Include all structured fields from the validated response
        credibility_score: result.credibility_score,
        confidence_level: result.confidence_level,
        speaker_transcripts: result.speaker_transcripts,
        red_flags_per_speaker: result.red_flags_per_speaker,
        gemini_summary: result.gemini_summary,
        recommendations: result.recommendations,
        linguistic_analysis: result.linguistic_analysis,
        risk_assessment: result.risk_assessment,
        session_insights: result.session_insights,
        // Legacy field for compatibility
        gemini_analysis: result.gemini_analysis
      }
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lie-detector-analysis-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="text-center">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent mb-3">
              🎙️ AI Lie Detector
            </h1>
            <p className="text-gray-300 text-lg">Advanced voice analysis with AI-powered deception detection</p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">        {/* Control Panel */}
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

        {/* Results */}
        {result && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Basic Analysis */}
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-white mb-4">📊 Basic Analysis</h2>
              
              {/* Transcript */}
              <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">📝 Transcript</h3>
                  <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
                    <p className="text-gray-200 leading-relaxed">{result.transcript}</p>
                  </div>
                </CardContent>
              </Card>              {/* Emotion Analysis */}
              <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">😊 Emotion Analysis</h3>
                  <div className="space-y-3">
                    {(() => {
                      // Handle both nested array and flat array structures
                      let emotions = result.emotion_analysis;
                      if (emotions && Array.isArray(emotions[0])) {
                        emotions = emotions[0]; // If nested, take the first array
                      }
                      if (!emotions || !Array.isArray(emotions)) {
                        return (
                          <div className="bg-yellow-500/20 backdrop-blur-sm border border-yellow-400/30 rounded-lg p-4">
                            <p className="text-yellow-200">No emotion analysis data available</p>
                          </div>
                        );
                      }
                      return emotions.slice(0, 5).map((emotion, index) => (
                        <div key={index} className="flex justify-between items-center bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
                          <span className="text-gray-200 capitalize font-medium">{emotion.label}</span>
                          <div className="flex items-center gap-3">
                            <div className="w-24 bg-white/20 rounded-full h-2">
                              <div 
                                className="h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full" 
                                style={{width: `${(emotion.score * 100).toFixed(1)}%`}}
                              ></div>
                            </div>
                            <span className="text-white font-semibold min-w-[50px]">{(emotion.score * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                      ));
                    })()}
                  </div>
                </CardContent>
              </Card>

              {/* Deception Flags */}
              <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">🚩 Deception Indicators</h3>
                  {result.deception_flags?.length > 0 ? (
                    <div className="space-y-2">
                      {result.deception_flags.map((flag, index) => (
                        <div key={index} className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-lg p-3">
                          <span className="text-red-200">⚠️ {flag}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-green-500/20 backdrop-blur-sm border border-green-400/30 rounded-lg p-4">
                      <p className="text-green-200">✅ No significant deception indicators detected</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Advanced Analysis Results */}
              {result.advanced_analysis && (
                <>
                  {/* Confidence Scores */}
                  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                    <CardContent className="p-6">
                      <h3 className="text-xl font-semibold text-white mb-4">📊 Confidence Scores</h3>
                      <div className="space-y-3">
                        {Object.entries(result.advanced_analysis.confidence_scores).map(([category, score], index) => (
                          <div key={index} className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-gray-200 capitalize font-medium">{category.replace('_', ' ')}</span>
                              <span className={`font-semibold ${score > 70 ? 'text-red-400' : score > 40 ? 'text-yellow-400' : 'text-green-400'}`}>
                                {score.toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-full bg-white/20 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${score > 70 ? 'bg-red-500' : score > 40 ? 'bg-yellow-500' : 'bg-green-500'}`}
                                style={{width: `${score}%`}}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Risk Assessment */}
                  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                    <CardContent className="p-6">
                      <h3 className="text-xl font-semibold text-white mb-4">⚡ Risk Assessment</h3>
                      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
                        <div className="flex items-center justify-center">
                          <span className={`text-2xl font-bold px-6 py-3 rounded-lg ${
                            result.advanced_analysis.overall_risk === 'high' ? 'bg-red-500/30 text-red-200' :
                            result.advanced_analysis.overall_risk === 'medium' ? 'bg-yellow-500/30 text-yellow-200' :
                            'bg-green-500/30 text-green-200'
                          }`}>
                            {result.advanced_analysis.overall_risk.toUpperCase()} RISK
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </>
              )}

              {/* Audio Quality Metrics */}
              {result.audio_quality && (
                <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                  <CardContent className="p-6">
                    <h3 className="text-xl font-semibold text-white mb-4">🎵 Audio Quality</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
                        <span className="text-gray-300 text-sm">Duration</span>
                        <p className="text-white font-semibold">{result.audio_quality.duration.toFixed(1)}s</p>
                      </div>
                      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
                        <span className="text-gray-300 text-sm">Quality Score</span>
                        <p className={`font-semibold ${result.audio_quality.quality_score > 70 ? 'text-green-400' : result.audio_quality.quality_score > 40 ? 'text-yellow-400' : 'text-red-400'}`}>
                          {result.audio_quality.quality_score}/100
                        </p>
                      </div>
                      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
                        <span className="text-gray-300 text-sm">Sample Rate</span>
                        <p className="text-white font-semibold">{result.audio_quality.sample_rate} Hz</p>
                      </div>
                      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
                        <span className="text-gray-300 text-sm">Loudness</span>
                        <p className="text-white font-semibold">{result.audio_quality.loudness.toFixed(1)} dBFS</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* AI Analysis */}
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-white mb-4">🤖 AI Deep Analysis</h2>
              
              {(() => {
                const geminiData = parseGeminiAnalysis(result.gemini_analysis);
                if (!geminiData || geminiData.error) {
                  return (
                    <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                      <CardContent className="p-6">
                        <h3 className="text-xl font-semibold text-white mb-4">❌ Analysis Error</h3>
                        <div className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-lg p-4">
                          <p className="text-red-200">
                            {geminiData?.error || 'Failed to process AI analysis'}
                          </p>
                          {geminiData?.gemini_summary && (
                            <div className="mt-3 pt-3 border-t border-red-400/30">
                              <p className="text-red-100 text-sm">{geminiData.gemini_summary}</p>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                }

                return (
                  <>
                    {/* Credibility Score */}
                    {geminiData.credibility_score !== undefined && (
                      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                        <CardContent className="p-6">
                          <h3 className="text-xl font-semibold text-white mb-4">🎯 Credibility Assessment</h3>
                          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-6">
                            <div className="flex items-center justify-between mb-4">
                              <span className="text-white font-semibold text-lg">Overall Score</span>
                              <span 
                                className="text-2xl font-bold"
                                style={{ color: getCredibilityColor(geminiData.credibility_score) }}
                              >
                                {geminiData.credibility_score}/100
                              </span>
                            </div>
                            <div className="w-full bg-white/20 rounded-full h-3 mb-3">
                              <div 
                                className="h-3 rounded-full transition-all duration-1000"
                                style={{
                                  width: `${geminiData.credibility_score}%`,
                                  background: `linear-gradient(90deg, ${getCredibilityColor(geminiData.credibility_score)}, ${getCredibilityColor(geminiData.credibility_score)}88)`
                                }}
                              ></div>
                            </div>
                            <p 
                              className="text-center font-semibold text-lg"
                              style={{ color: getCredibilityColor(geminiData.credibility_score) }}
                            >
                              {getCredibilityLabel(geminiData.credibility_score)}
                            </p>                          </div>
                        </CardContent>
                      </Card>
                    )}
                    
                    {/* Gemini Summary */}
                    {geminiData.gemini_summary && (
                      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                        <CardContent className="p-6">
                          <h3 className="text-xl font-semibold text-white mb-4">📋 Overall Summary</h3>
                          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">                            {typeof geminiData.gemini_summary === 'object' ? (
                              <div className="space-y-3">
                                {geminiData.gemini_summary.tone && (
                                  <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-purple-400/30">
                                    <span className="font-semibold text-purple-300">🎭 Tone Analysis:</span>
                                    <p className="text-gray-200 mt-1">{geminiData.gemini_summary.tone}</p>
                                  </div>
                                )}
                                {geminiData.gemini_summary.motivation && (
                                  <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
                                    <span className="font-semibold text-blue-300">🎯 Motivation Assessment:</span>
                                    <p className="text-gray-200 mt-1">{geminiData.gemini_summary.motivation}</p>
                                  </div>
                                )}
                                {geminiData.gemini_summary.credibility && (
                                  <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
                                    <span className="font-semibold text-green-300">✅ Credibility Analysis:</span>
                                    <p className="text-gray-200 mt-1">{geminiData.gemini_summary.credibility}</p>
                                  </div>
                                )}
                                {geminiData.gemini_summary.emotional_state && (
                                  <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-yellow-400/30">
                                    <span className="font-semibold text-yellow-300">😊 Emotional State:</span>
                                    <p className="text-gray-200 mt-1">{geminiData.gemini_summary.emotional_state}</p>
                                  </div>
                                )}
                                {geminiData.gemini_summary.communication_style && (
                                  <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-cyan-400/30">
                                    <span className="font-semibold text-cyan-300">💬 Communication Style:</span>
                                    <p className="text-gray-200 mt-1">{geminiData.gemini_summary.communication_style}</p>
                                  </div>
                                )}
                              </div>
                            ) : (
                              <p className="text-gray-200 leading-relaxed">{geminiData.gemini_summary}</p>
                            )}
                          </div>                        </CardContent>
                      </Card>
                    )}

                    {/* Session Insights - only show if part of ongoing conversation */}
                    {geminiData.session_insights && sessionHistory.length > 0 && (
                      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                        <CardContent className="p-6">
                          <h3 className="text-xl font-semibold text-white mb-4">🔍 Session Insights</h3>
                          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
                            <div className="space-y-3">
                              {geminiData.session_insights.consistency_analysis && (
                                <div className="bg-blue-500/10 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
                                  <span className="font-semibold text-blue-300">Consistency Analysis:</span>
                                  <p className="text-gray-200 mt-1">{geminiData.session_insights.consistency_analysis}</p>
                                </div>
                              )}
                              {geminiData.session_insights.behavioral_evolution && (
                                <div className="bg-orange-500/10 backdrop-blur-sm p-3 rounded-lg border border-orange-400/30">
                                  <span className="font-semibold text-orange-300">Behavioral Evolution:</span>
                                  <p className="text-gray-200 mt-1">{geminiData.session_insights.behavioral_evolution}</p>
                                </div>
                              )}
                              {geminiData.session_insights.risk_trajectory && (
                                <div className="bg-red-500/10 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
                                  <span className="font-semibold text-red-300">Risk Trajectory:</span>
                                  <p className="text-gray-200 mt-1">{geminiData.session_insights.risk_trajectory}</p>
                                </div>
                              )}
                              {geminiData.session_insights.conversation_dynamics && (
                                <div className="bg-green-500/10 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
                                  <span className="font-semibold text-green-300">Conversation Dynamics:</span>
                                  <p className="text-gray-200 mt-1">{geminiData.session_insights.conversation_dynamics}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}               
                    
                    {/* Linguistic Analysis */}
                    {geminiData.linguistic_analysis && (
                      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                        <CardContent className="p-6">
                          <h3 className="text-xl font-semibold text-white mb-4">📝 Linguistic Analysis</h3>
                          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
                            <div className="space-y-3">
                              {geminiData.linguistic_analysis.speech_patterns && (
                                <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
                                  <span className="font-semibold text-blue-300">🎵 Speech Patterns:</span>
                                  <p className="text-gray-200 mt-1">{geminiData.linguistic_analysis.speech_patterns}</p>
                                </div>
                              )}
                              {geminiData.linguistic_analysis.word_choice && (
                                <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-purple-400/30">
                                  <span className="font-semibold text-purple-300">📖 Word Choice:</span>
                                  <p className="text-gray-200 mt-1">{geminiData.linguistic_analysis.word_choice}</p>
                                </div>
                              )}
                              {geminiData.linguistic_analysis.emotional_consistency && (
                                <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-yellow-400/30">
                                  <span className="font-semibold text-yellow-300">💭 Emotional Consistency:</span>
                                  <p className="text-gray-200 mt-1">{geminiData.linguistic_analysis.emotional_consistency}</p>
                                </div>
                              )}
                              {geminiData.linguistic_analysis.detail_level && (
                                <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
                                  <span className="font-semibold text-green-300">🔍 Detail Level:</span>
                                  <p className="text-gray-200 mt-1">{geminiData.linguistic_analysis.detail_level}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Risk Assessment */}
                    {geminiData.risk_assessment && (
                      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                        <CardContent className="p-6">
                          <h3 className="text-xl font-semibold text-white mb-4">⚠️ Risk Assessment</h3>
                          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
                            {/* Overall Risk Level */}
                            <div className="mb-4 text-center">
                              <div className={`inline-block px-6 py-3 rounded-lg font-bold text-lg ${
                                geminiData.risk_assessment.overall_risk === 'high' ? 'bg-red-500/30 text-red-200 border border-red-400/50' :
                                geminiData.risk_assessment.overall_risk === 'medium' ? 'bg-yellow-500/30 text-yellow-200 border border-yellow-400/50' :
                                'bg-green-500/30 text-green-200 border border-green-400/50'
                              }`}>
                                {geminiData.risk_assessment.overall_risk.toUpperCase()} RISK
                              </div>
                            </div>
                            
                            {/* Risk Factors */}
                            {geminiData.risk_assessment.risk_factors && geminiData.risk_assessment.risk_factors.length > 0 && (
                              <div className="mb-4">
                                <h4 className="text-white font-semibold mb-2">🚩 Risk Factors:</h4>
                                <div className="space-y-2">
                                  {geminiData.risk_assessment.risk_factors.map((factor, index) => (
                                    <div key={index} className="bg-red-500/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
                                      <span className="text-red-200">• {factor}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {/* Mitigation Suggestions */}
                            {geminiData.risk_assessment.mitigation_suggestions && geminiData.risk_assessment.mitigation_suggestions.length > 0 && (
                              <div>
                                <h4 className="text-white font-semibold mb-2">💡 Mitigation Suggestions:</h4>
                                <div className="space-y-2">
                                  {geminiData.risk_assessment.mitigation_suggestions.map((suggestion, index) => (
                                    <div key={index} className="bg-green-500/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
                                      <span className="text-green-200">• {suggestion}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Confidence Level Indicator */}
                    {geminiData.confidence_level && (
                      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                        <CardContent className="p-6">
                          <h3 className="text-xl font-semibold text-white mb-4">📊 Analysis Confidence</h3>
                          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
                            <div className="text-center">
                              <div className={`inline-block px-6 py-3 rounded-lg font-bold text-lg ${
                                geminiData.confidence_level === 'very_high' ? 'bg-green-500/30 text-green-200 border border-green-400/50' :
                                geminiData.confidence_level === 'high' ? 'bg-blue-500/30 text-blue-200 border border-blue-400/50' :
                                geminiData.confidence_level === 'medium' ? 'bg-yellow-500/30 text-yellow-200 border border-yellow-400/50' :
                                geminiData.confidence_level === 'low' ? 'bg-orange-500/30 text-orange-200 border border-orange-400/50' :
                                'bg-red-500/30 text-red-200 border border-red-400/50'
                              }`}>
                                {geminiData.confidence_level.replace('_', ' ').toUpperCase()} CONFIDENCE
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Red Flags Per Speaker */}
                    {geminiData.red_flags_per_speaker && Object.keys(geminiData.red_flags_per_speaker).length > 0 && (
                      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                        <CardContent className="p-6">
                          <h3 className="text-xl font-semibold text-white mb-4">🔍 Speaker-Specific Analysis</h3>
                          <div className="space-y-4">
                            {Object.entries(geminiData.red_flags_per_speaker).map(([speaker, flags], index) => (
                              <div key={index} className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
                                <h4 className="text-white font-semibold mb-3">{speaker}</h4>
                                {Array.isArray(flags) && flags.length > 0 ? (
                                  <div className="space-y-2">
                                    {flags.map((flag, flagIndex) => (
                                      <div key={flagIndex} className="bg-red-500/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
                                        <span className="text-red-200">⚠️ {flag}</span>
                                      </div>
                                    ))}
                                  </div>
                                ) : (
                                  <div className="bg-green-500/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
                                    <span className="text-green-200">✅ No significant indicators detected</span>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}
                    
                    {/* Speaker Transcripts */}
                    {geminiData.speaker_transcripts && (
                      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                        <CardContent className="p-6">
                          <h3 className="text-xl font-semibold text-white mb-4">🗣️ Speaker Transcripts</h3>
                          <div className="space-y-3">
                            {Object.entries(geminiData.speaker_transcripts).map(([speaker, transcript], index) => (
                              <div key={index} className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
                                <p className="text-white font-semibold mb-2">{speaker}</p>
                                <p className="text-gray-200 leading-relaxed">{transcript}</p>
                              </div>
                            ))}
                            </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Recommendations */}
                    {geminiData.recommendations && (
                      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                        <CardContent className="p-6">
                          <h3 className="text-xl font-semibold text-white mb-4">💡 Recommendations</h3>
                          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
                            {Array.isArray(geminiData.recommendations) ? (
                              <div className="space-y-3">
                                {geminiData.recommendations.map((rec, index) => (
                                  <div key={index} className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border-l-4 border-green-400">
                                    <div className="flex items-start">
                                      <span className="bg-green-900/50 text-green-300 font-bold rounded-full w-6 h-6 flex items-center justify-center text-sm mr-3 mt-0.5">
                                        {index + 1}
                                      </span>
                                      <p className="text-gray-200 leading-relaxed">{rec}</p>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <p className="text-gray-200 leading-relaxed">{geminiData.recommendations}</p>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Debug Information */}
                    {result.metadata && (
                      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                        <CardContent className="p-6">
                          <h3 className="text-xl font-semibold text-white mb-4">🔧 Debug Information</h3>
                          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                              <div>
                                <span className="text-gray-400">Processing Time:</span>
                                <span className="text-white ml-2">{result.metadata.processing_time}s</span>
                              </div>
                              <div>
                                <span className="text-gray-400">File Size:</span>
                                <span className="text-white ml-2">{(result.metadata.file_size / 1024).toFixed(1)} KB</span>
                              </div>
                              <div>
                                <span className="text-gray-400">Analysis Version:</span>
                                <span className="text-white ml-2">{result.metadata.analysis_version}</span>
                              </div>
                              <div>
                                <span className="text-gray-400">Timestamp:</span>
                                <span className="text-white ml-2">{new Date(result.metadata.timestamp).toLocaleTimeString()}</span>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </>
                );
              })()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
