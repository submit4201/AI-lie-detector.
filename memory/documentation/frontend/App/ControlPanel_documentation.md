# ControlPanel Component Documentation

This document provides an overview of the `ControlPanel` component located in `frontend/src/components/App/ControlPanel.jsx`. This component serves as the primary user interface for interacting with the AI Lie Detector application, managing audio input, session controls, and analysis initiation.

---

## Purpose

The `ControlPanel` component provides a centralized interface for users to:
*   Manage conversation sessions (create new, clear current, view history).
*   Configure analysis mode (real-time streaming vs. traditional full upload).
*   Upload audio files for analysis.
*   Record audio directly in the browser.
*   Initiate the analysis process.
*   View analysis progress and any errors.
*   Export analysis results.
*   Test UI components by loading sample data (development feature).

It's structured within a `Card` component and uses other custom UI components like `Button`.

---

## Key Props Accepted

The `ControlPanel` accepts a comprehensive set of props to manage its state and behavior, primarily passed down from the main `App.jsx` component and its custom hooks.

*   **File Handling & State**:
    *   `file: File | null`: The currently selected audio file.
    *   `setFile: (file: File | null) => void`: Function to update the selected file.
    *   `loading: boolean`: Indicates if an analysis process (traditional upload) is ongoing.
    *   `error: string | null`: Displays any error messages related to audio processing or analysis.
    *   `analysisProgress: number | string`: Progress of traditional file upload analysis (can be a percentage or a descriptive string).
*   **Recording State**:
    *   `recording: boolean`: Indicates if audio recording is currently active.
*   **Session Management**:
    *   `sessionId: string | null`: The ID of the current active session.
    *   `sessionHistory: Array<Object>`: An array of past analysis entries for the current session.
    *   `showSessionPanel: boolean`: Controls the visibility of the session history panel.
    *   `setShowSessionPanel: (show: boolean) => void`: Function to toggle the session history panel.
*   **Streaming Analysis**:
    *   `useStreaming: boolean`: If true, streaming analysis mode is enabled.
    *   `setUseStreaming: (use: boolean) => void`: Function to toggle streaming mode.
    *   `isStreamingConnected: boolean`: Indicates if a WebSocket connection for streaming is active.
    *   `streamingProgress: string | null`: Descriptive progress of the streaming analysis (e.g., current step).
*   **Event Handlers (Callbacks)**:
    *   `createNewSession: () => Promise<void>`: Function to create a new analysis session.
    *   `clearCurrentSession: () => Promise<void>`: Function to clear data for the current session.
    *   `handleUpload: (fileToUpload?: File) => Promise<void>`: Function to initiate analysis of the selected `file` or a directly provided `fileToUpload`.
    *   `startRecording: () => void`: Function to begin audio recording.
    *   `stopRecording: () => void`: Function to stop audio recording and typically trigger an upload/analysis.
    *   `exportResults: () => void`: Function to export the current analysis results.
    *   `updateAnalysisResult: (data: any) => void`: Used by the test function to load sample data into the results display.
*   **Other**:
    *   `result: Object | null`: The current analysis result object (used to conditionally show the "Export Results" button).

---

## UI Components Used

The `ControlPanel` is built using several custom and imported UI components:
*   **`Card`, `CardContent` (from `@/components/ui/card`)**: The main container for the control panel.
*   **`Button` (from `@/components/ui/button`)**: Used for all interactive buttons:
    *   Show/Hide Session panel (with `Settings` icon).
    *   New Session.
    *   Clear Session.
    *   Analyze Audio (with `UploadCloud` or `Loader2` icon).
    *   Record Audio / Stop Recording (with `Mic` or `StopCircle` icon).
    *   Export Results (with `Download` icon).
    *   Test Tabs UI (with `🧪` emoji, though an icon could be used).
*   **`Input type="file"`**: Standard HTML file input for uploading audio files, styled with Tailwind CSS.
*   **`Input type="checkbox"`**: Standard HTML checkbox for toggling the `useStreaming` state, styled.
*   **Icons (from `lucide-react`)**: `UploadCloud`, `Mic`, `Loader2`, `StopCircle`, `Download`, `Settings` are used within buttons to provide visual cues.

---

## Key Functionality and Event Handling

### Session Management
*   **Display**: Shows the current `sessionId` (truncated) if active, or a message indicating a new session will be created. Displays the number of analyses in the current session history.
*   **Toggle Session Panel**: A "Show/Hide Session" button (`<Button>` with `Settings` icon) toggles the `showSessionPanel` state.
*   **Session History**: If `showSessionPanel` is true and `sessionHistory` is not empty, it displays a scrollable list of past analyses, showing analysis number, time, a transcript snippet, credibility score, and overall risk with color-coding.
*   **New Session**: A "New Session" button calls the `createNewSession` prop.
*   **Clear Session**: A "Clear Session" button (visible only if `sessionId` exists) calls the `clearCurrentSession` prop.

### Analysis Mode (Streaming Configuration)
*   **Toggle Streaming**: A checkbox allows users to enable/disable real-time streaming analysis by calling `setUseStreaming`.
*   **Streaming Status**: If `isStreamingConnected` is true, displays a "Streaming Connected" message with a pulsing green dot.
*   **Streaming Progress**: If `useStreaming` is true and `streamingProgress` has a value, it displays the progress string with a `Loader2` (spinner) icon.

### Audio Input
*   **File Upload**: An `<input type="file">` allows users to select an audio file. The `onChange` event updates the `file` state via the `setFile` prop.
*   **Recording**:
    *   A button toggles between "Record Audio" (with `Mic` icon) and "Stop Recording" (with `StopCircle` icon) based on the `recording` prop.
    *   It calls `startRecording` or `stopRecording` props respectively.
    *   This button is disabled if `loading` (traditional analysis in progress) is true.

### Analysis Initiation
*   **Analyze Audio Button**:
    *   Triggers the `handleUpload(file)` prop.
    *   Disabled if no `file` is selected or if `loading` is true.
    *   Displays a `Loader2` (spinner) icon and "Analyzing..." text when `loading` is true. Otherwise, shows `UploadCloud` icon and "Analyze Audio".

### Results and Progress
*   **Export Results**: A button to "Export Results" (with `Download` icon) is shown if `result` data exists. It calls the `exportResults` prop.
*   **Test Button**: A "Test Tabs UI" button calls an internal `testStructuredOutput` async function, which fetches mock data from `http://127.0.0.1:8000/test-structured-output` and uses `updateAnalysisResult` to display it.
*   **Progress Indicator**: If `loading` is true and either `analysisProgress` (for traditional) or `streamingProgress` (for streaming) has a value, it displays the relevant progress string with a `Loader2` icon. It also indicates if it's in "Streaming Mode".
*   **Error Display**: If the `error` prop has a value, it's displayed in a distinct error-styled section.

### Conditional Rendering
*   **Session ID & History**: Display of session ID, history count, and "Clear Session" button depends on `sessionId` and `sessionHistory.length`. The session history panel visibility depends on `showSessionPanel`.
*   **Recording Button**: Text and icon change based on the `recording` state.
*   **Analyze Audio Button**: Text, icon, and disabled state change based on `loading` and `file` state.
*   **Export Results Button**: Only visible if `result` is present.
*   **Progress Indicators**: Only visible when `loading` is true and progress information is available.
*   **Error Messages**: Only displayed if the `error` prop is not null/empty.
*   **Streaming Progress/Status**: Only shown if `useStreaming` is enabled and relevant streaming state (like `streamingProgress` or `isStreamingConnected`) is active.

---
