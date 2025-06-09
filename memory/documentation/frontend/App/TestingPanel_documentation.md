# TestingPanel Component Documentation

This document provides an overview of the `TestingPanel` component located in `frontend/src/components/App/TestingPanel.jsx`. This component is primarily intended for development and testing purposes.

---

## Purpose

The `TestingPanel` component provides a user interface within the application to facilitate testing of the results display and related functionalities. It allows developers to:
*   Load pre-defined sample analysis data and session history into the application's state.
*   Clear the currently displayed analysis data.

This helps in verifying the UI and behavior of components like `ResultsDisplay` and its sub-components without needing to perform actual audio uploads and analyses, especially for testing complex data structures or specific UI states. It is typically intended to be removed or hidden in production builds.

---

## Key Props Accepted

*   **`onLoadSampleData: (sampleResult: Object | null, sampleHistory: Array<Object>) => void`** (Required):
    *   A callback function passed from the parent component (likely `App.jsx`). This function is responsible for updating the parent component's state with the provided sample data.
    *   When "Load Sample Data" is clicked, it's called with `sampleAnalysisResult` and `sampleSessionHistory`.
    *   When "Clear Data" is clicked, it's called with `null` and an empty array `[]`.
*   **`className: string`** (Optional, Default: `""`):
    *   Allows for additional custom CSS classes to be applied to the main `div` container of the panel.

---

## UI Elements Rendered

The component renders the following UI elements:
*   **Main Container (`div`)**:
    *   Styled with `section-container glow-purple` and any passed `className`.
*   **Panel Title (`h3`)**:
    *   Displays "🧪 Testing Panel".
    *   Styled with `text-lg font-semibold text-purple-300 mb-3`.
*   **Descriptive Paragraph (`p`)**:
    *   Explains the panel's purpose: "Load sample analysis data to test the enhanced interface without uploading audio."
    *   Styled with `text-gray-300 text-sm mb-4`.
*   **Action Buttons (`div` with `flex gap-3`)**:
    *   **"Load Sample Data" Button (`button`)**:
        *   Styled with purple background/glow, hover effects, border, and specific padding/text size.
        *   `onClick` handler: `handleLoadSample`.
    *   **"Clear Data" Button (`button`)**:
        *   Styled with gray background, hover effects, border, and specific padding/text size.
        *   `onClick` handler: `handleClearData`.
*   **Informational Text (`div`)**:
    *   Provides a small note: "Sample includes: Full analysis • Session history • All enhanced features".
    *   Styled with `mt-3 text-xs text-gray-400`.

---

## Functionality of Test Actions/Buttons

### "Load Sample Data" Button
*   **Handler**: `handleLoadSample`
*   **Action**:
    1.  Imports `sampleAnalysisResult` and `sampleSessionHistory` from `../../data/sampleAnalysisData`.
    2.  Calls the `onLoadSampleData` prop with these imported sample data structures. This updates the parent component's state, causing the application (e.g., `ResultsDisplay`) to render as if this data came from an actual analysis.

### "Clear Data" Button
*   **Handler**: `handleClearData`
*   **Action**:
    1.  Calls the `onLoadSampleData` prop with `null` for the analysis result and an empty array `[]` for the session history. This effectively clears the displayed data in the parent component.

---

## Interaction with Services or Parent Component State

*   **Direct Interaction**: The `TestingPanel` interacts directly with the parent component (e.g., `App.jsx`) through the `onLoadSampleData` prop. It does not call backend services itself.
*   **State Manipulation**: Its primary function is to manipulate the state of the parent component by providing it with either sample data or instructions to clear existing data. This allows for testing various states of data presentation in the UI.
*   **Data Source**: Sample data (`sampleAnalysisResult`, `sampleSessionHistory`) is imported from a local path (`../../data/sampleAnalysisData`), indicating it's statically defined for testing.

---
