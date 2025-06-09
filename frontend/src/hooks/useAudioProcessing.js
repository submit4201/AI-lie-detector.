import { useState, useCallback, useRef } from 'react';

// Base URL for the backend API.
// Consider moving this to an environment variable for better configuration management.
const API_URL = 'http://localhost:8000';

/**
 * @hook useAudioProcessing
 * @description Manages audio input (file selection and recording), state related to processing
 * (loading, errors, progress), and handles the upload of audio data to the backend for analysis.
 *
 * @param {function} getSessionId - A function that returns the current session ID.
 *                                  Needed for associating uploads with a session.
 * @param {function} createNewSessionIfNeeded - An async function that creates a new session
 *                                              if no current session ID is available, and returns the new ID.
 * @returns {object} An object containing:
 *  - `file`: The currently selected/recorded audio File object.
 *  - `setFile`: Function to update the `file` state.
 *  - `recording`: Boolean indicating if audio recording is currently active.
 *  - `loading`: Boolean indicating if an audio upload/analysis is in progress.
 *  - `error`: Error message string if an error occurs, otherwise null.
 *  - `setError`: Function to set the error state.
 *  - `analysisProgress`: A number (0-100) representing the simulated analysis progress.
 *  - `validateAudioFile`: Function to perform basic validation on an audio file.
 *  - `handleUpload`: Async function to upload the current `file` for analysis.
 *  - `startRecording`: Async function to start audio recording using the microphone.
 *  - `stopRecording`: Function to stop the current audio recording.
 */
export const useAudioProcessing = (getSessionId, createNewSessionIfNeeded) => {
  // State for the audio file (from upload input or recording).
  const [file, setFile] = useState(null);
  // State to track if recording is currently active.
  const [recording, setRecording] = useState(false);
  // State to indicate if an analysis request is loading.
  const [loading, setLoading] = useState(false);
  // State to store any error messages related to audio processing or upload.
  const [error, setError] = useState(null);
  // State to simulate analysis progress (e.g., for a progress bar).
  const [analysisProgress, setAnalysisProgress] = useState(0);

  // Ref to store the MediaRecorder instance for audio recording.
  const mediaRecorderRef = useRef(null);
  // Ref to store chunks of audio data received during recording.
  const audioChunksRef = useRef([]);

  /**
   * Validates a selected audio file based on basic criteria.
   * @param {File} selectedFile - The file selected by the user.
   * @returns {string|null} An error message string if validation fails, otherwise null.
   */
  const validateAudioFile = (selectedFile) => {
    if (!selectedFile) return "No file selected.";
    // Basic MIME type check. More robust validation (e.g., magic numbers) could be done on the backend.
    if (!selectedFile.type.startsWith("audio/")) return "Invalid file type. Please select an audio file (e.g., WAV, MP3, OGG, WEBM, M4A, FLAC).";
    // Example: Add size validation if desired (though backend also validates size).
    // const MAX_SIZE_MB = 15;
    // if (selectedFile.size > MAX_SIZE_MB * 1024 * 1024) return `File exceeds ${MAX_SIZE_MB}MB limit.`;
    return null; // No validation errors.
  };

  /**
   * Handles the upload of the currently selected/recorded audio file to the backend for analysis.
   * It ensures a session ID is available (creating one if necessary) before uploading.
   * Simulates upload progress for UX purposes.
   * @async
   * @returns {Promise<object|null>} The analysis result object from the backend on success, or null on failure.
   */
  const handleUpload = useCallback(async () => {
    if (!file) {
      setError("No file selected for upload. Please select or record an audio file.");
      return null;
    }
    setLoading(true);    // Indicate loading state.
    setError(null);      // Clear previous errors.
    setAnalysisProgress(0); // Reset progress.

    // Ensure a session ID is available for the upload.
    let currentSessionId = getSessionId();
    if (!currentSessionId) {
      currentSessionId = await createNewSessionIfNeeded(); // Create new session if one doesn't exist.
      if (!currentSessionId) {
        setError("Failed to create or retrieve a session for the upload. Please try again.");
        setLoading(false);
        return null;
      }
    }

    // Prepare form data for the API request.
    const formData = new FormData();
    formData.append('audio', file); // The backend expects the file under the 'audio' field.
    formData.append('session_id', currentSessionId); // Send current session ID.

    try {
      // --- Progress Simulation ---
      // Simulate upload/analysis progress for better UX as actual streamable upload progress is complex.
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += 10; // Increment progress
        if (progress <= 100) {
          setAnalysisProgress(progress);
        } else {
          // Avoid exceeding 100 before actual response if interval is too fast or analysis too slow
          // This part of simulation might be cleared before it reaches 100 if response is quick.
        }
      }, 200); // Update progress every 200ms. Adjust timing as needed.

      // --- API Call ---
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData,
        // Headers are not explicitly set for FormData; browser sets Content-Type to multipart/form-data.
      });

      clearInterval(progressInterval); // Stop simulating progress once response is received.
      setAnalysisProgress(100);     // Ensure progress shows 100% on completion.

      if (!response.ok) {
        // Attempt to parse error details from backend response.
        const errData = await response.json().catch(() => ({ detail: 'Failed to analyze audio and could not parse error response.' }));
        throw new Error(errData.detail || `Analysis failed with status: ${response.status}`);
      }

      const analysisResult = await response.json(); // Parse successful JSON response.
      setLoading(false); // Turn off loading state.
      return analysisResult; // Return the analysis data.

    } catch (err) {
      console.error("Upload/Analysis Error:", err);
      setError(err.message || "An unexpected error occurred during audio analysis.");
      setLoading(false);        // Turn off loading state.
      setAnalysisProgress(0);   // Reset progress on error.
      clearInterval(progressInterval); // Ensure interval is cleared on error too
      return null; // Indicate failure.
    }
  }, [file, getSessionId, createNewSessionIfNeeded]); // Dependencies for useCallback.

  /**
   * Starts audio recording using the browser's MediaRecorder API.
   * It requests microphone access, sets up event handlers for data collection,
   * and updates the recording state.
   * @async
   */
  const startRecording = useCallback(async () => {
    if (recording) return; // Prevent starting if already recording.
    setError(null); // Clear previous errors.
    try {
      // Request microphone access.
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream); // Create MediaRecorder instance.
      audioChunksRef.current = []; // Reset audio chunks array for new recording.

      // Event handler for when data becomes available from the recorder.
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data); // Collect audio data chunks.
        }
      };

      // Event handler for when recording is stopped.
      mediaRecorderRef.current.onstop = () => {
        // Combine all collected audio chunks into a single Blob.
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        // Create a File object from the Blob to be used for upload.
        const recordedFile = new File([audioBlob], "recording.wav", {
            type: "audio/wav", // Set MIME type explicitly for the file.
            lastModified: Date.now(),
        });
        setFile(recordedFile); // Set the recorded file as the current file in state.
        setRecording(false);   // Update recording state.

        // Stop all media tracks (microphone access) to release resources.
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start(); // Start recording.
      setRecording(true); // Update recording state.
    } catch (err) {
      console.error("Error starting recording:", err);
      // Provide a user-friendly error, often related to permissions.
      setError("Failed to start recording. Please ensure microphone permissions are granted and try again.");
      setRecording(false); // Reset recording state.
    }
  }, [recording]); // Dependency: `recording` state to prevent re-renders from re-triggering.

  /**
   * Stops the current audio recording if one is in progress.
   * The actual processing of the recorded audio is handled by the `onstop` event
   * handler of the `MediaRecorder`.
   */
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop(); // Trigger the `onstop` event.
      // Recording state and file update are handled in `onstop` handler.
    }
  }, [recording]); // Dependency: `recording` state.

  // Expose state variables and functions to the component using this hook.
  return {
    file,
    setFile,
    recording,
    loading,
    error,
    setError,
    analysisProgress,
    validateAudioFile,
    handleUpload,
    startRecording,
    stopRecording,
  };
};
