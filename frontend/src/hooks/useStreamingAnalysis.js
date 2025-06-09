import { useState, useCallback, useRef, useEffect } from 'react';

const API_URL = 'http://localhost:8000'; // DO NOT CHANGE THIS IF ITS NOT CONNECTING STOP THE BACKEND AND ENSURE IT ON THIS PORT

export const useStreamingAnalysis = (sessionId, onAnalysisUpdate) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingProgress, setStreamingProgress] = useState(0);
  const [streamingStep, setStreamingStep] = useState('');
  const [streamingError, setStreamingError] = useState(null);
  const [partialResults, setPartialResults] = useState({});
  
  const websocketRef = useRef(null);
  const eventSourceRef = useRef(null);

  // WebSocket connection for real-time updates
  const connectWebSocket = useCallback(() => {
    if (!sessionId || websocketRef.current) return;

    try {
      const wsUrl = `ws://localhost:8000/ws/${sessionId}`;//DO NOT CHANGE THIS
      websocketRef.current = new WebSocket(wsUrl);

      websocketRef.current.onopen = () => {
        console.log('WebSocket connected for session:', sessionId);
      };

      websocketRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('WebSocket message received:', message);

          switch (message.type) {
            case 'progress_update':
              setStreamingProgress(message.percentage || 0);
              setStreamingStep(message.step || '');
              break;
            
            case 'analysis_update':
              setPartialResults(prev => ({
                ...prev,
                [message.analysis_type]: message.data
              }));
              if (onAnalysisUpdate) {
                onAnalysisUpdate(message.analysis_type, message.data);
              }
              break;
            
            case 'error':
              setStreamingError(message.message);
              setIsStreaming(false);
              break;
            
            default:
              console.log('Unknown message type:', message.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      websocketRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setStreamingError('WebSocket connection failed');
      };

      websocketRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        websocketRef.current = null;
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }, [sessionId, onAnalysisUpdate]);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
  }, []);

  // Server-Sent Events streaming analysis
  const startStreamingAnalysis = useCallback(async (audioFile) => {
    if (!audioFile || !sessionId) {
      setStreamingError('Missing audio file or session ID');
      return null;
    }

    setIsStreaming(true);
    setStreamingError(null);
    setStreamingProgress(0);
    setStreamingStep('Initializing...');
    setPartialResults({});

    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('session_id', sessionId);

      // Start EventSource for streaming updates
      const eventSourceUrl = `${API_URL}/analyze/stream`;
      
      // Use fetch to upload the file and get streaming response
      const response = await fetch(eventSourceUrl, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Read the streaming response
      const reader = response.body.getReader();
      let finalResult = null;

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          // Decode the chunk
          const chunk = new TextDecoder().decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                console.log('SSE data received:', data);

                switch (data.type) {
                  case 'progress':
                    setStreamingProgress((data.progress / data.total) * 100);
                    setStreamingStep(data.step || 'Processing...');
                    break;
                  
                  case 'result':
                    setPartialResults(prev => ({
                      ...prev,
                      [data.analysis_type]: data.data
                    }));
                    if (onAnalysisUpdate) {
                      onAnalysisUpdate(data.analysis_type, data.data);
                    }
                    break;
                  
                  case 'complete':
                    setStreamingProgress(100);
                    setStreamingStep('Analysis Complete');
                    // Combine all partial results into final result
                    finalResult = { ...partialResults };
                    break;
                  
                  case 'error':
                    setStreamingError(data.message);
                    break;
                }
              } catch (parseError) {
                console.error('Error parsing SSE data:', parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

      setIsStreaming(false);
      return finalResult;

    } catch (error) {
      console.error('Streaming analysis error:', error);
      setStreamingError(error.message || 'Streaming analysis failed');
      setIsStreaming(false);
      return null;
    }
  }, [sessionId, onAnalysisUpdate, partialResults]);

  // Connect WebSocket when sessionId changes
  useEffect(() => {
    if (sessionId) {
      connectWebSocket();
    }
    return () => {
      disconnectWebSocket();
    };
  }, [sessionId, connectWebSocket, disconnectWebSocket]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
      const eventSource = eventSourceRef.current;
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [disconnectWebSocket]);

  return {
    isStreaming,
    streamingProgress,
    streamingStep,
    streamingError,
    partialResults,
    startStreamingAnalysis,
    connectWebSocket,
    disconnectWebSocket,
  };
};
