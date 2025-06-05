import React from 'react';
// Card and CardContent are used by the sub-components, so they are imported in those files.
// No direct imports needed here if ResultsDisplay only orchestrates sub-sections.
import BasicAnalysisSection from './results/BasicAnalysisSection';
import AIDeepAnalysisSection from './results/AIDeepAnalysisSection';

const ResultsDisplay = ({ result, parseGeminiAnalysis, getCredibilityColor, getCredibilityLabel, formatConfidenceLevel, sessionHistory }) => {
  if (!result) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8"> {/* Added mt-8 for spacing */}
      <BasicAnalysisSection result={result} />
      <AIDeepAnalysisSection
        result={result}
        parseGeminiAnalysis={parseGeminiAnalysis}
        getCredibilityColor={getCredibilityColor}
        getCredibilityLabel={getCredibilityLabel}
        formatConfidenceLevel={formatConfidenceLevel}
        sessionHistory={sessionHistory}
      />
    </div>
  );
};

export default ResultsDisplay;
