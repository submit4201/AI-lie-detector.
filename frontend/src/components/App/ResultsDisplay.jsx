import React from 'react';
import { Card, CardContent } from "@/components/ui/card"; // Shadcn/ui Card components
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"; // Shadcn/ui Tabs components
// Individual result sections
import BasicAnalysisSection from './results/BasicAnalysisSection';
import AIDeepAnalysisSection from './results/AIDeepAnalysisSection';
import QuantitativeMetricsSection from './results/QuantitativeMetricsSection';
import SessionInsightsSection from './results/SessionInsightsSection';
import KeyHighlightsSection from './results/KeyHighlightsSection';

/**
 * @component ResultsDisplay
 * @description This component is responsible for rendering the comprehensive analysis results.
 * It structures the display into several key sections: Transcript, Key Highlights,
 * top metric cards (Credibility, Confidence, Risk), and a tabbed interface for
 * Basic Analysis, AI Deep Analysis, and Quantitative Metrics. It also includes
 * a separate section for Session Insights if available.
 *
 * @param {object} props - The properties passed to the component.
 * @param {object|null} props.result - The main analysis result object from the backend. If null, the component renders nothing.
 * @param {function} props.parseGeminiAnalysis - Utility function to parse parts of the Gemini analysis text (if needed).
 * @param {function} props.getCredibilityColor - Utility function to get Tailwind CSS color class based on credibility score.
 * @param {function} props.getCredibilityLabel - Utility function to get a human-readable label for credibility score.
 * @param {function} props.formatConfidenceLevel - Utility function to format the confidence level.
 * @param {Array<object>} props.sessionHistory - Array of past analysis entries for the current session, passed to relevant sub-sections.
 * @returns {JSX.Element|null} The ResultsDisplay component UI, or null if no result is provided.
 */
const ResultsDisplay = ({ result, parseGeminiAnalysis, getCredibilityColor, getCredibilityLabel, formatConfidenceLevel, sessionHistory }) => {
  // If there's no result data, don't render anything.
  if (!result) {
    return null;
  }

  // Main container for all result sections.
  return (
    <div className="mt-8 space-y-8">
      {/* Section 1: Full Audio Transcript */}
      {/* Conditionally renders if a transcript is available in the results. */}
      {result.transcript && ( // Corrected from result.transcription to result.transcript
        <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
          <CardContent className="p-6">
            <h2 className="text-2xl font-bold text-white mb-4 text-center lg:text-left">
              📝 Audio Transcript
            </h2>
            {/* Decorative underline element */}
            <div className="w-16 h-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded mx-auto lg:mx-0 mb-6"></div>
            {/* Inner card for the transcript text with specific styling */}
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-6">
              <p className="text-gray-200 leading-relaxed whitespace-pre-wrap text-lg">
                {result.transcript}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Section 2: Key Highlights derived from the analysis */}
      <KeyHighlightsSection
        result={result}
        getCredibilityColor={getCredibilityColor} // Pass down utility functions
        getCredibilityLabel={getCredibilityLabel}
      />

      {/* Section 3: Grid of Top Three Key Metric Cards (Credibility, Confidence, Risk) */}
      {/* This grid adapts to different screen sizes. */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">

        {/* Credibility Score Card: Displays overall credibility. */}
        {result.credibility_score !== undefined && ( // Check if credibility_score is part of the result
          <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-full flex flex-col">
            <CardContent className="p-6 flex-1 flex flex-col">
              <h3 className="text-xl font-semibold text-white mb-4">🎯 Credibility Score</h3>
              <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-6 flex-1 flex flex-col justify-center">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-white font-semibold text-lg">Overall Score</span>
                  {/* Display score with dynamic color based on value */}
                  <span
                    className={`text-3xl font-bold ${getCredibilityColor(result.credibility_score / 100)}`}
                  >
                    {result.credibility_score}/100
                  </span>
                </div>
                {/* Progress bar representation of the credibility score */}
                <div className="w-full bg-white/20 rounded-full h-3 mb-3">
                  <div
                    className={`h-3 rounded-full transition-all duration-1000 ${
                      getCredibilityColor(result.credibility_score / 100).replace('text-', 'bg-') // Convert text color to bg color
                    }`}
                    style={{
                      width: `${result.credibility_score}%`, // Dynamic width for progress bar
                    }}
                  ></div>
                </div>
                {/* Human-readable label for the credibility score */}
                <p
                  className={`text-center font-semibold text-lg ${getCredibilityColor(result.credibility_score / 100)}`}
                >
                  {getCredibilityLabel(result.credibility_score / 100)}
                </p>
              </div>
              <div className="mt-4 text-sm text-gray-300">
                <p>Overall likelihood that the speaker is being truthful based on vocal patterns and linguistic analysis.</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Analysis Confidence Level Card: Displays how confident the AI is in its analysis. */}
        {result.confidence_level && (
          <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-full flex flex-col">
            <CardContent className="p-6 flex-1 flex flex-col">
              <h3 className="text-xl font-semibold text-white mb-4">📊 Analysis Confidence</h3>
              <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 flex-1 flex flex-col justify-center">
                <div className="text-center">
                  {/* Display confidence level with dynamic styling */}
                  <div className={`inline-block px-6 py-3 rounded-lg font-bold text-lg ${
                    result.confidence_level === 'very_high' ? 'bg-green-500/30 text-green-200 border border-green-400/50' :
                    result.confidence_level === 'high' ? 'bg-blue-500/30 text-blue-200 border border-blue-400/50' :
                    result.confidence_level === 'medium' ? 'bg-yellow-500/30 text-yellow-200 border border-yellow-400/50' :
                    result.confidence_level === 'low' ? 'bg-orange-500/30 text-orange-200 border border-orange-400/50' :
                    'bg-red-500/30 text-red-200 border border-red-400/50' // For 'very_low'
                  }`}>
                    {result.confidence_level.replace('_', ' ').toUpperCase()} CONFIDENCE
                  </div>
                </div>
              </div>
              <div className="mt-4 text-sm text-gray-300">
                <p>AI analysis confidence based on audio quality, speech clarity, and data completeness.</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Risk Assessment Card: Displays the overall risk level identified. */}
        {result.risk_assessment && result.risk_assessment.overall_risk && (
          <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-full flex flex-col">
            <CardContent className="p-6 flex-1 flex flex-col">
              <h3 className="text-xl font-semibold text-white mb-4">⚠️ Risk Level</h3>
              <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 flex-1 flex flex-col justify-center">
                <div className="text-center">
                  {/* Display risk level with dynamic styling */}
                  <div className={`inline-block px-6 py-3 rounded-lg font-bold text-lg ${
                    result.risk_assessment.overall_risk === 'high' ? 'bg-red-500/30 text-red-200 border border-red-400/50' :
                    result.risk_assessment.overall_risk === 'medium' ? 'bg-yellow-500/30 text-yellow-200 border border-yellow-400/50' :
                    'bg-green-500/30 text-green-200 border border-green-400/50' // For 'low'
                  }`}>
                    {result.risk_assessment.overall_risk.toUpperCase()} RISK
                  </div>
                </div>
              </div>
              <div className="mt-4 text-sm text-gray-300">
                <p>Deception risk assessment based on detected patterns and behavioral indicators.</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Section 4: Tabbed Interface for Detailed Analysis Sections */}
      {/* Uses Shadcn/ui Tabs component for organizing detailed analysis views. */}
      <Tabs defaultValue="basic-analysis" className="w-full">
        {/* Tab Triggers: Buttons to switch between different analysis views. */}
        <TabsList className="grid w-full grid-cols-1 sm:grid-cols-3 bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
          <TabsTrigger value="basic-analysis" className="text-white data-[state=active]:bg-black/30 data-[state=active]:text-blue-400">Basic Analysis</TabsTrigger>
          <TabsTrigger value="ai-deep-analysis" className="text-white data-[state=active]:bg-black/30 data-[state=active]:text-purple-400">AI Deep Dive</TabsTrigger> {/* Changed label for brevity */}
          <TabsTrigger value="quantitative-metrics" className="text-white data-[state=active]:bg-black/30 data-[state=active]:text-green-400">Quantitative Metrics</TabsTrigger>
        </TabsList>

        {/* Tab Content Panels: Each panel corresponds to a tab trigger. */}
        <TabsContent value="basic-analysis">
          {/* Renders basic analysis details like audio quality and emotion scores. */}
          <BasicAnalysisSection result={result} />
        </TabsContent>
        <TabsContent value="ai-deep-analysis">
          {/* Renders the AI-driven deep analysis from Gemini, including summary and other detailed assessments. */}
          <AIDeepAnalysisSection
            result={result} // Full result object
            // Pass down utility functions needed by AIDeepAnalysisSection or its children
            parseGeminiAnalysis={parseGeminiAnalysis}
            getCredibilityColor={getCredibilityColor}
            getCredibilityLabel={getCredibilityLabel}
            formatConfidenceLevel={formatConfidenceLevel}
            // sessionHistory might be used for context within this section if needed by sub-components
            sessionHistory={sessionHistory}
          />
        </TabsContent>
        <TabsContent value="quantitative-metrics">
          {/* Renders quantitative linguistic metrics and other numerical data. */}
          <QuantitativeMetricsSection result={result} />
        </TabsContent>
      </Tabs>

      {/* Section 5: Session Insights (Displayed separately, if available in the result) */}
      {/* This section shows insights derived from the entire session's history. */}
      <SessionInsightsSection result={result} sessionHistory={sessionHistory} />
    </div>
  );
};

export default ResultsDisplay;
