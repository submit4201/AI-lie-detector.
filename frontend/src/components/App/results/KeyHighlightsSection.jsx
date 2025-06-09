import React from 'react';
import { Card, CardContent } from "@/components/ui/card"; // Shadcn/ui Card components
import { Badge } from "@/components/ui/badge"; // Shadcn/ui Badge component for displaying risk level

/**
 * @component KeyHighlightsSection
 * @description This component displays a summary of the most critical analysis results,
 * including overall credibility score, overall risk assessment, a brief AI insight summary,
 * and a list of key deception indicators if any are present.
 *
 * @param {object} props - The properties passed to the component.
 * @param {object|null} props.result - The main analysis result object from the backend.
 *                                     If null, the component renders nothing.
 * @param {function} props.getCredibilityColor - Utility function to get Tailwind CSS color class based on credibility score.
 * @param {function} props.getCredibilityLabel - Utility function to get a human-readable label for credibility score.
 * @returns {JSX.Element|null} The KeyHighlightsSection UI, or null if no result is provided.
 */
const KeyHighlightsSection = ({ result, getCredibilityColor, getCredibilityLabel }) => {
  // If there's no result data, don't render this section.
  if (!result) {
    return null;
  }

  // Destructure relevant parts of the result for easier access.
  const { credibility_score, risk_assessment, red_flags_per_speaker, gemini_summary } = result;

  /**
   * Determines Tailwind CSS classes for styling the risk badge based on the risk level.
   * @param {string} riskLevel - The risk level string (e.g., 'high', 'medium', 'low').
   * @returns {string} Tailwind CSS classes for background, text, and border color.
   */
  const getRiskColorClasses = (riskLevel) => {
    if (riskLevel === 'high') return 'bg-red-500/30 text-red-200 border-red-400/50';
    if (riskLevel === 'medium') return 'bg-yellow-500/30 text-yellow-200 border-yellow-400/50';
    if (riskLevel === 'low') return 'bg-green-500/30 text-green-200 border-green-400/50';
    return 'bg-gray-500/30 text-gray-200 border-gray-400/50'; // Default for unknown risk levels
  };

  // Consolidate all red flags from all speakers into a single array.
  // The `red_flags_per_speaker` is an object where keys are speaker IDs and values are arrays of flags.
  const allRedFlags = red_flags_per_speaker
    ? Object.values(red_flags_per_speaker).flat() // Get all arrays of flags and flatten them into one.
    : []; // Default to an empty array if `red_flags_per_speaker` is not present.

  return (
    // Main card container for key highlights with a gradient background and blur effect.
    <Card className="bg-gradient-to-br from-purple-600/20 via-blue-600/20 to-indigo-600/20 backdrop-blur-lg border-white/20 shadow-2xl">
      <CardContent className="p-6">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">✨ Key Analysis Highlights ✨</h2>
        {/* Grid layout for highlight cards, responsive to screen size. */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

          {/* Highlight Card 1: Overall Credibility Score */}
          {/* Conditionally rendered if credibility_score is available. */}
          {credibility_score !== undefined && (
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 flex flex-col items-center justify-center text-center h-full">
              <h3 className="text-lg font-semibold text-white mb-3">🎯 Overall Credibility</h3>
              {/* Display numerical score with dynamic color. */}
              <div className={`text-5xl font-bold ${getCredibilityColor(credibility_score / 100)} mb-2`}>
                {credibility_score}/100
              </div>
              {/* Display human-readable label for the score with dynamic color. */}
              <div className={`text-xl font-semibold ${getCredibilityColor(credibility_score / 100)} mb-3`}>
                {getCredibilityLabel(credibility_score / 100)}
              </div>
              {/* Progress bar representation of the credibility score. */}
              <div className="w-full bg-white/20 rounded-full h-2.5">
                <div
                  className={`h-2.5 rounded-full ${getCredibilityColor(credibility_score / 100).replace('text-', 'bg-')}`} // Convert text color to background color
                  style={{ width: `${credibility_score}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Highlight Card 2: Overall Risk Assessment */}
          {/* Conditionally rendered if overall_risk is available. */}
          {risk_assessment?.overall_risk && (
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 flex flex-col items-center justify-center text-center h-full">
              <h3 className="text-lg font-semibold text-white mb-3">⚠️ Overall Risk Level</h3>
              {/* Display risk level as a styled badge. */}
              <Badge className={`px-6 py-3 text-2xl font-bold ${getRiskColorClasses(risk_assessment.overall_risk)}`}>
                {risk_assessment.overall_risk.toUpperCase()}
              </Badge>
              <p className="text-xs text-gray-400 mt-3">
                Assessment based on detected patterns and behavioral indicators.
              </p>
            </div>
          )}

          {/* Highlight Card 3: AI Insights Summary (brief points from Gemini summary) */}
          {/* Conditionally rendered if gemini_summary is available. */}
          {gemini_summary && (
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 md:col-span-2 lg:col-span-1 h-full flex flex-col justify-center"> {/* Adjusted span for layout */}
              <h3 className="text-lg font-semibold text-white mb-3 text-center">💡 AI Insights Snippet</h3>
              <div className="text-sm text-gray-300 space-y-2 text-center">
                {/* Display a snippet of credibility assessment from Gemini summary. */}
                {gemini_summary.credibility && (
                  <p><strong className="text-purple-300">AI Credibility View:</strong> {gemini_summary.credibility.substring(0, 120)}{gemini_summary.credibility.length > 120 ? '...' : ''}</p>
                )}
                {/* Display a snippet of key concerns from Gemini summary. */}
                {gemini_summary.key_concerns && (
                  <p><strong className="text-yellow-300">AI Key Concerns:</strong> {gemini_summary.key_concerns.substring(0,120)}{gemini_summary.key_concerns.length > 120 ? '...' : ''}</p>
                )}
                {/* Fallback if specific structured fields within gemini_summary are not present but gemini_summary itself is a string. */}
                {(!gemini_summary.credibility && !gemini_summary.key_concerns && typeof gemini_summary === 'string') &&
                  <p>{gemini_summary.substring(0, 250)}{gemini_summary.length > 250 ? '...' : ''}</p>
                }
              </div>
            </div>
          )}

          {/* Highlight Card 4: Key Deception Indicators (if any are found) */}
          {/* This section spans more columns on larger screens if there are indicators. */}
          {allRedFlags.length > 0 && (
             <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 md:col-span-2 lg:col-span-3">
              <h3 className="text-lg font-semibold text-white mb-3 text-center">🚩 Key Deception Indicators Identified</h3>
              {/* Scrollable list for multiple indicators. */}
              <div className="space-y-2 max-h-32 overflow-y-auto pr-2">
                {allRedFlags.map((flag, index) => (
                  <div key={index} className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-md p-2">
                    <p className="text-red-200 text-sm">⚠️ {flag}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          {/* Message if no deception indicators are found, but the check was performed. */}
           {allRedFlags.length === 0 && red_flags_per_speaker && (
             <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 md:col-span-2 lg:col-span-3">
              <h3 className="text-lg font-semibold text-white mb-3 text-center">🚩 Key Deception Indicators</h3>
              <div className="bg-green-500/20 backdrop-blur-sm border border-green-400/30 rounded-md p-3 text-center">
                <p className="text-green-200 text-sm">✅ No significant specific deception indicators were flagged by the AI across speakers.</p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default KeyHighlightsSection;
