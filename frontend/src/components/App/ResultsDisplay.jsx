import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import BasicAnalysisSection from './results/BasicAnalysisSection';
import AIDeepAnalysisSection from './results/AIDeepAnalysisSection';
import QuantitativeMetricsSection from './results/QuantitativeMetricsSection';
import SessionInsightsSection from './results/SessionInsightsSection';

const ResultsDisplay = ({ result, parseGeminiAnalysis, getCredibilityColor, getCredibilityLabel, formatConfidenceLevel, sessionHistory }) => {
  if (!result) {
    return null;
  }
  return (
    <div className="mt-8 space-y-8">
      {/* 1. Transcript Section - Full Width at Top */}
      {result.transcription && (
        <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
          <CardContent className="p-6">
            <h2 className="text-2xl font-bold text-white mb-4 text-center lg:text-left">
              📝 Audio Transcript
            </h2>
            <div className="w-16 h-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded mx-auto lg:mx-0 mb-6"></div>
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-6">
              <p className="text-gray-200 leading-relaxed whitespace-pre-wrap text-lg">
                {result.transcription}
              </p>
            </div>
          </CardContent>
        </Card>
      )}      {/* 2. Top Three Key Metric Cards - Same Height */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
        {/* Credibility Score Card */}
        {result.credibility_score !== undefined && (
          <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-full flex flex-col">
            <CardContent className="p-6 flex-1 flex flex-col">
              <h3 className="text-xl font-semibold text-white mb-4">🎯 Credibility Score</h3>
              <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-6 flex-1 flex flex-col justify-center">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-white font-semibold text-lg">Overall Score</span>
                  <span
                    className="text-3xl font-bold"
                    style={{ color: getCredibilityColor(result.credibility_score / 100) }}
                  >
                    {result.credibility_score}/100
                  </span>
                </div>
                <div className="w-full bg-white/20 rounded-full h-3 mb-3">
                  <div
                    className="h-3 rounded-full transition-all duration-1000"
                    style={{
                      width: `${result.credibility_score}%`,
                      background: `linear-gradient(90deg, ${getCredibilityColor(result.credibility_score / 100)}, ${getCredibilityColor(result.credibility_score / 100)}88)`
                    }}
                  ></div>
                </div>
                <p
                  className="text-center font-semibold text-lg"
                  style={{ color: getCredibilityColor(result.credibility_score / 100) }}
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

        {/* Confidence Level Card */}
        {result.confidence_level && (
          <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-full flex flex-col">
            <CardContent className="p-6 flex-1 flex flex-col">
              <h3 className="text-xl font-semibold text-white mb-4">📊 Analysis Confidence</h3>
              <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 flex-1 flex flex-col justify-center">
                <div className="text-center">
                  <div className={`inline-block px-6 py-3 rounded-lg font-bold text-lg ${
                    result.confidence_level === 'very_high' ? 'bg-green-500/30 text-green-200 border border-green-400/50' :
                    result.confidence_level === 'high' ? 'bg-blue-500/30 text-blue-200 border border-blue-400/50' :
                    result.confidence_level === 'medium' ? 'bg-yellow-500/30 text-yellow-200 border border-yellow-400/50' :
                    result.confidence_level === 'low' ? 'bg-orange-500/30 text-orange-200 border border-orange-400/50' :
                    'bg-red-500/30 text-red-200 border border-red-400/50'
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

        {/* Risk Assessment Card */}
        {result.risk_assessment && (
          <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-full flex flex-col">
            <CardContent className="p-6 flex-1 flex flex-col">
              <h3 className="text-xl font-semibold text-white mb-4">⚠️ Risk Level</h3>
              <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 flex-1 flex flex-col justify-center">
                <div className="text-center">
                  <div className={`inline-block px-6 py-3 rounded-lg font-bold text-lg ${
                    result.risk_assessment.overall_risk === 'high' ? 'bg-red-500/30 text-red-200 border border-red-400/50' :
                    result.risk_assessment.overall_risk === 'medium' ? 'bg-yellow-500/30 text-yellow-200 border border-yellow-400/50' :
                    'bg-green-500/30 text-green-200 border border-green-400/50'
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

      {/* 3. Quantitative Metrics Section (NEW) */}
      <QuantitativeMetricsSection result={result} />

      {/* 4. Session Insights Section (NEW) */}
      <SessionInsightsSection result={result} sessionHistory={sessionHistory} />

      {/* 5. Basic Analysis Section */}
      <BasicAnalysisSection result={result} />

      {/* 6. AI Deep Analysis Section */}
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
