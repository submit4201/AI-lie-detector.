# Frontend Application Structure Documentation

This document provides an overview of the main entry point (`main.jsx`) and the root application component (`App.jsx`) for the frontend of the AI Lie Detector application.

---

## `frontend/src/main.jsx`

### Purpose
This file serves as the main entry point for the React application. It is responsible for initializing the React DOM and rendering the root `App` component into the HTML page.

### Key Imports
*   **`StrictMode` from `react`**: A tool for highlighting potential problems in an application. It activates additional checks and warnings for its descendants.
*   **`createRoot` from `react-dom/client`**: The new API for creating a root to render or unmount.
*   **`./index.css`**: Global CSS styles for the application.
*   **`App` from `./App.jsx`**: The main application component.

### Rendering Logic
1.  **`createRoot(document.getElementById('root'))`**: This creates a React root for the DOM element with the ID `root`. This element is expected to be present in the main `index.html` file and serves as the container for the entire React application.
2.  **`.render(...)`**: This method is called on the created root to render the React elements into the DOM.
    *   **`<StrictMode>`**: The `App` component is wrapped with `StrictMode`. In development mode, this helps identify unsafe lifecycles, legacy API usage, and other potential issues by, for example, double-invoking certain functions like constructors and render methods. It has no effect in production builds.
    *   **`<App />`**: The root `App` component is rendered, initiating the application's UI and logic.

### Providers
*   The `main.jsx` in the provided code does not explicitly set up any React Context Providers like `TooltipProvider` (as mentioned in the prompt's example). If such global providers were needed, they would typically wrap the `<App />` component here.

---

## `frontend/src/App.jsx`

### Overall Purpose
`App.jsx` is the main application component. It defines the overall layout and structure of the user interface. It integrates various custom hooks for managing state and logic related to session management, audio processing, analysis results, and streaming. It then passes down state and callbacks to child components responsible for different UI sections like the header, control panel, and results display. While it doesn't use a formal routing library like React Router in the provided code, it manages the display of different information based on application state, effectively acting as a single-page application.

### Key State Variables (Managed by Hooks or Directly)
*   **`showSessionPanel: boolean`**: Controls the visibility of a session panel (passed to `ControlPanel`). Initialized with `useState(false)`.
*   **`useStreaming: boolean`**: A toggle to switch between streaming analysis and traditional full-upload analysis. Initialized with `useState(true)`.
*   **Session Management (via `useSessionManagement` hook)**:
    *   `sessionId: string | null`
    *   `sessionHistory: Array<Object>`
*   **Audio Processing (via `useAudioProcessing` hook)**:
    *   `file: File | null`
    *   `recording: boolean`
    *   `loading: boolean` (for traditional uploads)
    *   `error: string | null` (renamed `audioError` in `App.jsx`)
    *   `analysisProgress: number` (for traditional uploads)
*   **Analysis Results (via `useAnalysisResults` hook)**:
    *   `result: Object | null` (stores the main analysis data)
*   **Streaming Analysis (via `useStreamingAnalysis` hook)**:
    *   `isStreaming: boolean` (indicates if a streaming connection is active)
    *   `streamingProgress: number` (overall percentage for streaming)
    *   `streamingStep: string` (current step description for streaming)
    *   `streamingError: string | null`
    *   `partialResults: Object` (accumulated results from streaming)
    *   `lastReceivedComponent: string | null`
    *   `componentsReceived: Set<string>`

### Main JSX Structure
The component renders a main `div` with class `app-container` and a gradient background. Inside, it has:
1.  **`<Header />`**: A component likely displaying the application title or global navigation.
2.  **Main Content Area (`div.max-w-7xl.mx-auto.px-6.py-8.fade-in`)**: A centered container for the primary content.
    *   **`<TestingPanel />`**: A component for development/testing purposes, allowing loading of sample data. It's noted to be removed in production.
    *   **`<ControlPanel />`**: A major component responsible for user inputs, including file upload, recording controls, session management actions (new session, clear session), and initiating analysis. It receives numerous props, including state from the hooks and callback handlers defined in `App.jsx`.
    *   **`<ResultsDisplay />`**: A major component that takes the analysis results (`result`, `partialResults`), loading states, and various helper functions from `useAnalysisResults` to render the findings of the lie detection analysis. It also displays streaming-specific information.

### Component Integration & Custom Hooks
*   **`Header`**: Renders the application header.
*   **`ControlPanel`**: Receives props for:
    *   File handling (`file`, `setFile`, `validateAudioFile`).
    *   Loading, recording, error, and progress states (uses `displayError` and `displayProgress` which combine streaming/non-streaming states).
    *   Session management (`sessionId`, `sessionHistory`, `showSessionPanel`, `setShowSessionPanel`, `appCreateNewSession`, `appClearCurrentSession`).
    *   Analysis initiation (`appHandleUpload`).
    *   Recording controls (`startRecording`, `stopRecording`).
    *   Result handling (`exportResults`, `result`, `updateAnalysisResult`).
    *   Streaming toggle and status (`useStreaming`, `setUseStreaming`, `isStreamingConnected`, `streamingProgress`).
*   **`ResultsDisplay`**: Receives props for:
    *   Displaying analysis results (`analysisResults`, which is `result` from `useAnalysisResults`).
    *   Helper functions for formatting results (`parseGeminiAnalysis`, `getCredibilityColor`, etc.).
    *   Session context (`sessionHistory`, `sessionId`).
    *   Streaming-specific data (`isStreaming`, `streamingProgress` (renamed `streamingStep`), `partialResults`, `lastReceivedComponent`, `componentsReceived`).
    *   Loading state (`isLoading`, which is `loading` from `useAudioProcessing`).
*   **`TestingPanel`**: A development tool that calls `handleLoadSampleData` to populate the UI with mock data.

### Custom Hooks Interaction
`App.jsx` makes extensive use of custom hooks to encapsulate and manage complex logic:
*   **`useSessionManagement`**: Provides `sessionId`, `sessionHistory`, and functions `hookCreateNewSession`, `loadSessionHistory`, `clearCurrentSession`. `App.jsx` wraps `hookCreateNewSession` and `clearCurrentSession` in `appCreateNewSession` and `appClearCurrentSession` respectively to add UI-related actions like clearing results and errors.
*   **`useAudioProcessing`**: Provides states for `file`, `recording`, `loading`, `audioError`, `analysisProgress`, and functions `setFile`, `validateAudioFile`, `hookHandleUpload`, `startRecording`, `stopRecording`. `App.jsx` wraps `hookHandleUpload` in `appHandleUpload` to decide whether to use streaming or traditional analysis.
*   **`useAnalysisResults`**: Provides `result` (the main analysis data object) and utility functions `updateAnalysisResult`, `exportResults`, `getCredibilityColor`, etc.
*   **`useStreamingAnalysis`**: Provides states and functions related to the streaming analysis process, such as `isStreaming`, `streamingProgress`, `streamingStep`, `streamingError`, `partialResults`, `startStreamingAnalysis`, and `resetStreamingState`.

### Key Logic and Effects
*   **Error Display**: `displayError` combines `streamingError` and `audioError` for a unified error display.
*   **Progress Display**: `displayProgress` shows streaming progress if `useStreaming` is true, otherwise shows traditional upload progress.
*   **`useEffect` for `sessionId`**: Loads session history whenever `sessionId` changes.
*   **`useEffect` for `partialResults`**: Updates the main `result` state with incoming partial results from streaming. If a seemingly complete result is received via stream (has transcript and credibility score), it schedules a `loadSessionHistory` call.
*   **`appHandleUpload`**: This callback orchestrates the analysis.
    *   Validates the file if provided directly.
    *   If `useStreaming` is true and `sessionId` exists, it calls `startStreamingAnalysis`. If that fails, it attempts to fall back to `hookHandleUpload` (traditional full upload).
    *   If `useStreaming` is false, it directly calls `hookHandleUpload`.
    *   After successful analysis (either streaming or traditional), it updates results and schedules a `loadSessionHistory` call.
*   **`appCreateNewSession` / `appClearCurrentSession`**: These wrap the respective hook functions to also clear local UI state like errors, results, and streaming state.

### Routing
No explicit routing library (like React Router) is used. The application functions as a single page where content in `ResultsDisplay` changes based on the state of `result`, `loading`, `isStreaming`, etc.

---
