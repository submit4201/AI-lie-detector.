import { useState, useCallback } from 'react';

// --- Helper Functions for Formatting and Displaying Analysis Results ---

/**
 * Determines the Tailwind CSS text color class based on a credibility score.
 * Scores are assumed to be normalized (e.g., 0-1 or 0-100, then scaled).
 * This version assumes `level` is a score from 0.0 to 1.0.
 * @param {number|null|undefined} level - The credibility score (0.0 to 1.0).
 * @returns {string} Tailwind CSS text color class.
 */
export const getCredibilityColor = (level) => {
  if (level === null || level === undefined) return "text-gray-500"; // Default or loading state
  if (level < 0.4) return "text-red-500";         // Scores 0-39% (Low credibility)
  if (level < 0.7) return "text-yellow-500";      // Scores 40-69% (Moderate credibility)
  return "text-green-500";                        // Scores 70-100% (High credibility)
};

/**
 * Provides a human-readable label for a given credibility score.
 * Assumes `level` is a score from 0.0 to 1.0.
 * @param {number|null|undefined} level - The credibility score (0.0 to 1.0).
 * @returns {string} Human-readable credibility label.
 */
export const getCredibilityLabel = (level) => {
  if (level === null || level === undefined) return "N/A";
  if (level < 0.4) return "High Risk / Low Credibility";    // Scores 0-39%
  if (level < 0.7) return "Medium Risk / Moderate Credibility"; // Scores 40-69%
  return "Low Risk / High Credibility";     // Scores 70-100%
};

/**
 * Parses analysis text, potentially from a Gemini summary field, to extract a score and reasoning.
 * NOTE: With structured data from the backend (like `result.credibility_score` and `result.gemini_summary.credibility`),
 * this function's original primary purpose of extracting a top-level score and reasoning from a single text block
 * is less critical for the main analysis display. It might still be useful for parsing specific, complex string fields
 * within the `gemini_summary` object if those fields themselves contain embedded scores or structured text.
 *
 * @param {string} analysisText - The text to parse.
 * @returns {{score: number|null, reasoning: string}} An object containing the parsed score and reasoning.
 *                                                  Returns null for score if not found.
 */
export const parseGeminiAnalysis = (analysisText) => {
    if (!analysisText || typeof analysisText !== 'string') {
        return { score: null, reasoning: "No analysis text provided or invalid format." };
    }

    // This function attempts to parse a score and reasoning from a combined text block.
    // Given the backend now provides structured data (credibility_score, gemini_summary),
    // this function's broad use for top-level score/reasoning is less critical.
    // It might still be useful for parsing specific string fields within gemini_summary if they contain complex text.

    // Normalize text: remove common markdown-like headers and bold markers.
    const normalizedText = analysisText
        .replace(/## Credibility Score:/gi, "") // Case-insensitive removal of "Credibility Score:" header
        .replace(/## Reasoning:/gi, "")        // Case-insensitive removal of "Reasoning:" header
        .replace(/\*\*/g, "");                 // Remove bold markdown (**)

    // Attempt to find a score, looking for patterns like "Credibility Score: 75" or just a number.
    const scoreMatch = normalizedText.match(/Credibility Score:\s*([\d.]+)/i);
    let score = null;
    if (scoreMatch && scoreMatch[1]) {
        score = parseFloat(scoreMatch[1]);
    } else {
        // If specific "Credibility Score:" pattern isn't found, look for any number.
        const numberMatch = normalizedText.match(/([\d.]+)/);
        if (numberMatch && numberMatch[1]) {
            score = parseFloat(numberMatch[1]);
        }
    }

    // Extract reasoning text.
    let reasoning = normalizedText;
    if (scoreMatch && scoreMatch[0]) { // If "Credibility Score: XX" was found
        reasoning = normalizedText.substring(normalizedText.indexOf(scoreMatch[0]) + scoreMatch[0].length).trim();
    } else if (score !== null) { // If only a number was found for score
        // Attempt to remove the score itself from the reasoning, if it's the first number found.
        reasoning = normalizedText.replace(String(score), "").trim();
    }
    // Further clean up by removing any leading "Reasoning:" label.
    reasoning = reasoning.replace(/^Reasoning:\s*/i, "").trim();

    // Handle cases where parsing might fail or text is empty.
    if (score === null && !reasoning) {
        return { score: null, reasoning: "Could not parse analysis. Raw text: " + analysisText };
    }

    return {
        score,
        reasoning: reasoning || (score === null ? "No specific reasoning found in text." : "Reasoning not explicitly parsed from text.")
    };
};

/**
 * Formats a confidence level (0.0 to 1.0) as a percentage string.
 * @param {number|null|undefined} level - The confidence level (0.0 to 1.0).
 * @returns {string} Formatted percentage string (e.g., "75%") or "N/A".
 */
export const formatConfidenceLevel = (level) => {
  if (level === null || level === undefined || isNaN(level)) return "N/A";
  return `${(level * 100).toFixed(0)}%`; // Convert to percentage and remove decimals.
};

/**
 * @hook useAnalysisResults
 * @description Manages the state for analysis results received from the backend
 * and provides utility functions for handling and displaying these results.
 *
 * @returns {object} An object containing:
 *  - `result`: The current analysis result object (conforms to backend's AnalyzeResponse). Null if no result.
 *  - `updateAnalysisResult`: Function to set or clear the analysis result state.
 *  - `exportResults`: Function to download the current analysis results as a JSON file.
 *  - Helper functions: `getCredibilityColor`, `getCredibilityLabel`, `parseGeminiAnalysis`, `formatConfidenceLevel`.
 */
export const useAnalysisResults = () => {
  // State to store the full analysis result object received from the backend.
  // It's expected to match the structure of the `AnalyzeResponse` Pydantic model from the backend.
  const [result, setResult] = useState(null);

  /**
   * Updates the analysis result state.
   * Expects `newResult` to be the structured object directly from the backend API (AnalyzeResponse).
   * If `newResult` is null, it clears the current results.
   * @param {object|null} newResult - The new analysis result object, or null to clear.
   */
  const updateAnalysisResult = useCallback((newResult) => {
    if (newResult === null) {
      setResult(null); // Clear existing results.
      return;
    }
    // Directly set the structured result.
    // The backend provides structured data like `credibility_score`, `gemini_summary`, etc.,
    // so no complex client-side parsing is needed for the main fields.
    // Components should access data like `result.credibility_score`, `result.gemini_summary.credibility`, etc.
    setResult(newResult);
  }, []); // No dependencies, this function's definition is stable.


  /**
   * Exports the current analysis results to a JSON file.
   * If no result is available, it shows an alert.
   */
  const exportResults = useCallback(() => {
    if (!result) {
      alert("No analysis results available to export.");
      return;
    }
    // Create a JSON string with pretty printing (2-space indentation).
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2));

    // Create a temporary anchor element to trigger the download.
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    // Set the filename for the download, including session ID if available.
    downloadAnchorNode.setAttribute("download", `analysis_results_${result.session_id || 'current_analysis'}.json`);
    document.body.appendChild(downloadAnchorNode); // Required for Firefox.
    downloadAnchorNode.click(); // Simulate a click to trigger download.
    downloadAnchorNode.remove(); // Clean up the temporary anchor.
  }, [result]); // Dependency: `result` state. Re-create if `result` changes.

  // Return the state and functions to be used by components.
  return {
    result,
    updateAnalysisResult,
    exportResults,
    // Expose helper functions. These can be used by components to format display values.
    getCredibilityColor,
    getCredibilityLabel,
    parseGeminiAnalysis, // Its utility is now more for specific sub-fields if needed.
    formatConfidenceLevel,
  };
};
