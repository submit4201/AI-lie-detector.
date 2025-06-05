import { useState, useCallback } from 'react';

// Helper functions (originally in App.jsx)
export const getCredibilityColor = (level) => {
  if (level === null || level === undefined) return "text-gray-500"; // Default or loading
  if (level < 0.3) return "text-red-500"; // Low credibility
  if (level < 0.7) return "text-yellow-500"; // Medium credibility
  return "text-green-500"; // High credibility
};

export const getCredibilityLabel = (level) => {
  if (level === null || level === undefined) return "N/A";
  if (level < 0.3) return "Low Credibility";
  if (level < 0.7) return "Medium Credibility";
  return "High Credibility";
};

export const parseGeminiAnalysis = (analysisText) => {
    if (!analysisText) return { score: null, reasoning: "No analysis text provided." };

    // This function attempts to parse a score and reasoning from a combined text block.
    // Given the backend now provides structured data (credibility_score, gemini_summary),
    // this function's broad use for top-level score/reasoning is less critical.
    // It might still be useful for parsing specific string fields within gemini_summary if they contain complex text.
    // For now, its direct role in populating a top-level `parsedAnalysis` object will be removed.

    // Normalize text by removing markdown-like formatting for section headers
    const normalizedText = analysisText
        .replace(/## Credibility Score:/i, "")
        .replace(/## Reasoning:/i, "")
        .replace(/\*\*/g, ""); // Remove bold markdown

    const scoreMatch = normalizedText.match(/Credibility Score:\s*([\d.]+)/i);
    let score = null;
    if (scoreMatch && scoreMatch[1]) {
        score = parseFloat(scoreMatch[1]);
    } else {
        const numberMatch = normalizedText.match(/([\d.]+)/);
        if (numberMatch && numberMatch[1]) {
            score = parseFloat(numberMatch[1]);
        }
    }

    let reasoning = normalizedText;
    if (scoreMatch) {
        reasoning = normalizedText.substring(normalizedText.indexOf(scoreMatch[0]) + scoreMatch[0].length).trim();
    } else if (score !== null) {
        reasoning = normalizedText.replace(String(score), "").trim();
    }
    reasoning = reasoning.replace(/^Reasoning:\s*/i, "").trim();

    if (score === null && !reasoning) {
        return { score: null, reasoning: "Could not parse analysis. Raw: " + analysisText };
    }
    // If score is null but reasoning exists, it's still valid partial data.
    return { score, reasoning: reasoning || (score === null ? "No specific reasoning found in text." : "Reasoning not explicitly parsed.") };
};

export const formatConfidenceLevel = (level) => {
  if (level === null || level === undefined) return "N/A";
  return `${(level * 100).toFixed(0)}%`;
};


export const useAnalysisResults = () => {
  const [result, setResult] = useState(null); // Stores the full analysis object, expecting AnalyzeResponse structure

  // The main function to update results.
  // newResult is expected to be the structured object from the backend (AnalyzeResponse).
  const updateAnalysisResult = useCallback((newResult) => {
    if (newResult === null) {
      setResult(null);
      return;
    }
    // Directly set the structured result from the backend.
    // The backend now provides credibility_score, gemini_summary, etc., as direct fields.
    // No need for a separate top-level `parsedAnalysis` field based on string parsing here.
    // Components should use result.credibility_score, result.gemini_summary.credibility, etc.
    setResult(newResult);
  }, []);


  const exportResults = useCallback(() => {
    if (!result) {
      alert("No results to export.");
      return;
    }
    // Simple JSON export for now
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `analysis_results_${result.session_id || 'current'}.json`);
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  }, [result]);

  return {
    result,
    updateAnalysisResult, // Renamed from setResult for clarity
    exportResults,
    // Exposing helpers if they are needed directly by components,
    // though often they'd be used internally or through the processed `result`
    getCredibilityColor,
    getCredibilityLabel,
    parseGeminiAnalysis,
    formatConfidenceLevel,
  };
};
