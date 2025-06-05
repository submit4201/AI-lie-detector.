import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import React, { useState, useRef } from "react"; // Ensure React is imported
import React, { useState, useRef } from "react";
import Header from "./components/App/Header";
import ControlPanel from "./components/App/ControlPanel";
import ResultsDisplay from "./components/App/ResultsDisplay";

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
      } else {
        const errorText = await response.text().catch(() => 'Unknown server error');
        setError(`Failed to create session: ${response.status} ${errorText}`);
        console.error('Failed to create session:', response.status, errorText);
      }
    } catch (err) {
      console.error('Failed to create session:', err);
      setError(`Failed to create session: ${err.message}. Check your network connection or if the server is running.`);
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
      } else {
        // Optionally, inform user if loading history fails, though it's less critical than other errors.
        console.warn('Failed to load session history:', response.status);
      }
    } catch (err) {
      console.warn('Failed to load session history:', err);
    }
  };

  const clearCurrentSession = async () => {
    if (!sessionId) return;
    
    try {
      const response = await fetch(`http://localhost:8000/session/${sessionId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        setSessionId(null);
        setSessionHistory([]);
        setResult(null);
        setError(null); // Clear any previous errors
      } else {
        const errorText = await response.text().catch(() => 'Unknown server error');
        setError(`Failed to clear session: ${response.status} ${errorText}`);
        console.error('Failed to clear session:', response.status, errorText);
      }
    } catch (err) {
      console.error('Failed to clear session:', err);
      setError(`Failed to clear session: ${err.message}. Check your network connection or if the server is running.`);
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
        let errorText = await res.text().catch(() => 'Could not retrieve error message from server.');
        // Attempt to parse as JSON if it's a structured error from backend
        try {
          const errorJson = JSON.parse(errorText);
          if (errorJson.detail) { // FastAPI often uses 'detail' for errors
            errorText = errorJson.detail;
          } else if (errorJson.error) {
            errorText = errorJson.error;
          }
        } catch (e) {
          // Not a JSON error, use errorText as is
        }
        throw new Error(`Server error (${res.status}): ${errorText}`);
      }
      
      setAnalysisProgress('Running AI analysis...');
      const data = await res.json();
      console.log("Received data:", data);
      
      if (data.error) { // Check for application-level error in successful response
        setError(`Analysis failed: ${data.error}`);
        setResult(null); // Ensure no partial/previous results are shown
      } else {
        setAnalysisProgress('Analysis complete!');
        setResult(data);
        loadSessionHistory(currentSessionId); // Load updated session history
      }
    } catch (err) {
      console.error("Upload error:", err);
      // Distinguish network errors from server errors
      if (err.message.startsWith('Server error')) {
        setError(`Upload failed. ${err.message}`);
      } else {
        setError(`Upload failed: ${err.message}. Please check your network connection or if the server is running.`);
      }
      setResult(null); // Clear previous results on error
    } finally {
      setLoading(false);
      // Clear analysisProgress unless it's already "Analysis complete!" and there's no error
      if (error || !(analysisProgress === 'Analysis complete!' && result)) {
        setAnalysisProgress('');
      }
    }
  };

  const startRecording = async () => {
    setError(null); // Clear previous errors
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        // Consider adding validation for blob size or type if necessary
        const recordedFile = new File([audioBlob], "recording.wav", { type: "audio/wav" });
        setFile(recordedFile); // Show the recorded file in the input (optional)
        handleUpload(recordedFile); // Directly upload after recording stops
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setRecording(true);
    } catch (err) {
      console.error("Recording error:", err);
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        setError("Microphone access was denied. Please enable microphone permissions in your browser settings.");
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        setError("No microphone found. Please ensure a microphone is connected and enabled.");
      } else {
        setError("Could not start recording: Microphone access denied or unavailable. Please check browser permissions and hardware.");
      }
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
      <Header />

      <div className="max-w-7xl mx-auto px-6 py-8">
        <ControlPanel
          file={file}
          setFile={setFile}
          loading={loading}
          recording={recording}
          error={error}
          analysisProgress={analysisProgress}
          sessionId={sessionId}
          sessionHistory={sessionHistory}
          showSessionPanel={showSessionPanel}
          setShowSessionPanel={setShowSessionPanel}
          createNewSession={createNewSession}
          clearCurrentSession={clearCurrentSession}
          handleUpload={handleUpload}
          startRecording={startRecording}
          stopRecording={stopRecording}
          exportResults={exportResults}
          result={result}
        />
        <ResultsDisplay
          result={result}
          parseGeminiAnalysis={parseGeminiAnalysis}
          getCredibilityColor={getCredibilityColor}
          getCredibilityLabel={getCredibilityLabel}
          // sessionHistory is used inside the Gemini part of results, so pass it if available
          // or modify ResultsDisplay to not depend on it directly if it's only for a small part
          sessionHistory={sessionHistory}
        />
      </div>
    </div>
  );
}
