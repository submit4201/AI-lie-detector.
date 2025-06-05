import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge"; // For risk assessment

const KeyHighlightsSection = ({ result, getCredibilityColor, getCredibilityLabel }) => {
  if (!result) {
    return null;
  }

  const { credibility_score, risk_assessment, red_flags_per_speaker, gemini_summary } = result;

  const getRiskColorClasses = (riskLevel) => {
    if (riskLevel === 'high') return 'bg-red-500/30 text-red-200 border-red-400/50';
    if (riskLevel === 'medium') return 'bg-yellow-500/30 text-yellow-200 border-yellow-400/50';
    if (riskLevel === 'low') return 'bg-green-500/30 text-green-200 border-green-400/50';
    return 'bg-gray-500/30 text-gray-200 border-gray-400/50';
  };

  const allRedFlags = red_flags_per_speaker
    ? Object.values(red_flags_per_speaker).flat()
    : [];

  return (
    <Card className="bg-gradient-to-br from-purple-600/20 via-blue-600/20 to-indigo-600/20 backdrop-blur-lg border-white/20 shadow-2xl">
      <CardContent className="p-6">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">✨ Key Highlights ✨</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

          {/* 1. Overall Credibility Score */}
          {credibility_score !== undefined && (
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 flex flex-col items-center justify-center text-center">
              <h3 className="text-lg font-semibold text-white mb-3">🎯 Overall Credibility</h3>
              <div className={`text-5xl font-bold ${getCredibilityColor(credibility_score / 100)} mb-2`}>
                {credibility_score}/100
              </div>
              <div className={`text-xl font-semibold ${getCredibilityColor(credibility_score / 100)} mb-3`}>
                {getCredibilityLabel(credibility_score / 100)}
              </div>
              <div className="w-full bg-white/20 rounded-full h-2.5">
                <div
                  className={`h-2.5 rounded-full ${getCredibilityColor(credibility_score / 100).replace('text-', 'bg-')}`}
                  style={{ width: `${credibility_score}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* 2. Overall Risk Assessment */}
          {risk_assessment?.overall_risk && (
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 flex flex-col items-center justify-center text-center">
              <h3 className="text-lg font-semibold text-white mb-3">⚠️ Overall Risk</h3>
              <Badge className={`px-6 py-3 text-2xl font-bold ${getRiskColorClasses(risk_assessment.overall_risk)}`}>
                {risk_assessment.overall_risk.toUpperCase()}
              </Badge>
              <p className="text-xs text-gray-400 mt-3">
                Deception risk based on detected patterns and behavioral indicators.
              </p>
            </div>
          )}

          {/* 3. AI Insights Summary (Fallback if specific fields are missing) */}
          {gemini_summary && (
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 md:col-span-2 lg:col-span-1">
              <h3 className="text-lg font-semibold text-white mb-3 text-center">💡 AI Insights Summary</h3>
              <div className="text-sm text-gray-300 space-y-2 text-center">
                {gemini_summary.credibility && (
                  <p><strong className="text-purple-300">Credibility:</strong> {gemini_summary.credibility.substring(0, 150)}{gemini_summary.credibility.length > 150 ? '...' : ''}</p>
                )}
                {gemini_summary.key_concerns && (
                  <p><strong className="text-yellow-300">Concerns:</strong> {gemini_summary.key_concerns.substring(0,150)}{gemini_summary.key_concerns.length > 150 ? '...' : ''}</p>
                )}
                {(!gemini_summary.credibility && !gemini_summary.key_concerns && typeof gemini_summary === 'string') &&
                  <p>{gemini_summary.substring(0, 300)}{gemini_summary.length > 300 ? '...' : ''}</p>
                }
              </div>
            </div>
          )}

          {/* 4. Key Deception Indicators (If any) */}
          {allRedFlags.length > 0 && (
             <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 md:col-span-2 lg:col-span-3"> {/* Spans more columns */}
              <h3 className="text-lg font-semibold text-white mb-3 text-center">🚩 Key Deception Indicators</h3>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {allRedFlags.map((flag, index) => (
                  <div key={index} className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-md p-2">
                    <p className="text-red-200 text-sm">⚠️ {flag}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
           {allRedFlags.length === 0 && red_flags_per_speaker && ( // Only show if red_flags_per_speaker was checked
             <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 md:col-span-2 lg:col-span-3">
              <h3 className="text-lg font-semibold text-white mb-3 text-center">🚩 Key Deception Indicators</h3>
              <div className="bg-green-500/20 backdrop-blur-sm border border-green-400/30 rounded-md p-3 text-center">
                <p className="text-green-200 text-sm">✅ No significant deception indicators detected across speakers.</p>
              </div>
            </div>
          )}

        </div>
      </CardContent>
    </Card>
  );
};

export default KeyHighlightsSection;
