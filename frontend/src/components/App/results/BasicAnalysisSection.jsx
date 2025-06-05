import React from 'react';
import { Card, CardContent } from "@/components/ui/card";

const DeceptionIndicatorsCard = ({ deceptionFlags }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🚩 Deception Indicators</h3>
      {deceptionFlags?.length > 0 ? (
        <div className="space-y-2">
          {deceptionFlags.map((flag, index) => (
            <div key={index} className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-lg p-3">
              <span className="text-red-200">⚠️ {flag}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-green-500/20 backdrop-blur-sm border border-green-400/30 rounded-lg p-4">
          <p className="text-green-200">✅ No significant deception indicators detected</p>
        </div>
      )}
    </CardContent>
  </Card>
);

const ConfidenceScoresCard = ({ confidenceScores }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">📊 Analysis Confidence</h3>
      <div className="space-y-3">
        {Object.entries(confidenceScores).map(([category, score], index) => (
          <div key={index} className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-gray-200 capitalize font-medium">{category.replace('_', ' ')}</span>
              <span className={`font-semibold ${score > 70 ? 'text-green-400' : score > 40 ? 'text-yellow-400' : 'text-red-400'}`}>
                {score.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-white/20 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${score > 70 ? 'bg-green-500' : score > 40 ? 'bg-yellow-500' : 'bg-red-500'}`}
                style={{width: `${score}%`}}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </CardContent>
  </Card>
);

const BehavioralAnalysisCard = ({ result }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🧠 Behavioral Analysis</h3>
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        <div className="space-y-4">
          {/* Speech Patterns Summary */}
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
            <span className="font-semibold text-blue-300">🎵 Speech Patterns:</span>
            <p className="text-gray-200 mt-1 text-sm">
              {result.linguistic_analysis?.speech_patterns?.substring(0, 120) || 
               "Analysis of speech rhythm, pacing, and vocal patterns in progress..."}
              {result.linguistic_analysis?.speech_patterns?.length > 120 && "..."}
            </p>            {/* Add quantitative metrics from structured data */}
            <div className="mt-2 pt-2 border-t border-blue-400/30">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-400">Speech Rate:</span>
                  <span className="text-blue-200">
                    {result.linguistic_analysis?.speech_rate_wpm 
                      ? `${Math.round(result.linguistic_analysis.speech_rate_wpm)} WPM`
                      : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Word Count:</span>
                  <span className="text-blue-200">
                    {result.linguistic_analysis?.word_count || 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Communication Style */}
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-purple-400/30">
            <span className="font-semibold text-purple-300">💬 Communication Style:</span>
            <p className="text-gray-200 mt-1 text-sm">
              {typeof result.gemini_summary === 'object' && result.gemini_summary?.communication_style?.substring(0, 120) ||
               typeof result.gemini_summary === 'string' && result.gemini_summary.substring(0, 120) ||
               "Analyzing communication patterns and verbal behaviors..."}
              {(typeof result.gemini_summary === 'object' && result.gemini_summary?.communication_style?.length > 120) ||
               (typeof result.gemini_summary === 'string' && result.gemini_summary.length > 120) ? "..." : ""}
            </p>            {/* Add communication metrics from structured data */}
            <div className="mt-2 pt-2 border-t border-purple-400/30">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-400">Formality Score:</span>
                  <span className="text-purple-200">
                    {result.linguistic_analysis?.formality_score 
                      ? `${Math.round(result.linguistic_analysis.formality_score)}/100`
                      : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Complexity:</span>
                  <span className="text-purple-200">
                    {result.linguistic_analysis?.complexity_score 
                      ? `${Math.round(result.linguistic_analysis.complexity_score)}/100`
                      : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Emotional Consistency */}
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-yellow-400/30">
            <span className="font-semibold text-yellow-300">😊 Emotional State:</span>
            <p className="text-gray-200 mt-1 text-sm">
              {typeof result.gemini_summary === 'object' && result.gemini_summary?.emotional_state?.substring(0, 120) ||
               result.linguistic_analysis?.emotional_consistency?.substring(0, 120) ||
               "Evaluating emotional consistency and authenticity..."}
              {((typeof result.gemini_summary === 'object' && result.gemini_summary?.emotional_state?.length > 120) ||
                (result.linguistic_analysis?.emotional_consistency?.length > 120)) && "..."}
            </p>
            {/* Add emotional metrics */}
            {result.emotion_analysis && Array.isArray(result.emotion_analysis) && result.emotion_analysis.length > 0 && (
              <div className="mt-2 pt-2 border-t border-yellow-400/30">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">Primary Emotion:</span>
                  <span className="text-yellow-200 capitalize">
                    {result.emotion_analysis[0].label.replace('_', ' ')} ({Math.round(result.emotion_analysis[0].score * 100)}%)
                  </span>
                </div>
              </div>
            )}
          </div>          {/* Stress Indicators - Using structured data */}
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
            <span className="font-semibold text-red-300">⚡ Stress Indicators:</span>
            <div className="mt-2 space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-400">Filler Words:</span>
                <span className="text-red-200">
                  {result.linguistic_analysis?.filler_count ?? 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Hesitation Count:</span>
                <span className="text-red-200">
                  {result.linguistic_analysis?.hesitation_count ?? 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Repetitions:</span>
                <span className="text-red-200">
                  {result.linguistic_analysis?.repetition_count ?? 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Hesitation Rate:</span>
                <span className="text-red-200">
                  {result.linguistic_analysis?.hesitation_rate 
                    ? `${result.linguistic_analysis.hesitation_rate.toFixed(1)}/min`
                    : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
);

const KeyFindingsCard = ({ result }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🔍 Key Findings</h3>
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        <div className="space-y-3">
          {/* Strengths */}
          {typeof result.gemini_summary === 'object' && result.gemini_summary?.strengths && (
            <div className="bg-green-500/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
              <span className="font-semibold text-green-300">✅ Credibility Strengths:</span>
              <p className="text-gray-200 mt-1 text-sm">{result.gemini_summary.strengths}</p>
            </div>
          )}

          {/* Key Concerns */}
          {typeof result.gemini_summary === 'object' && result.gemini_summary?.key_concerns && (
            <div className="bg-red-500/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
              <span className="font-semibold text-red-300">⚠️ Key Concerns:</span>
              <p className="text-gray-200 mt-1 text-sm">{result.gemini_summary.key_concerns}</p>
            </div>
          )}

          {/* Motivation Assessment */}
          {typeof result.gemini_summary === 'object' && result.gemini_summary?.motivation && (
            <div className="bg-blue-500/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
              <span className="font-semibold text-blue-300">🎯 Motivation Assessment:</span>
              <p className="text-gray-200 mt-1 text-sm">{result.gemini_summary.motivation}</p>
            </div>
          )}
        </div>
      </div>
    </CardContent>
  </Card>
);

const BasicAnalysisSection = ({ result }) => {
  if (!result) return null;
  return (
    <div className="space-y-6 h-fit">
      {/* Behavioral Analysis */}
      <BehavioralAnalysisCard result={result} />

      {/* Key Findings */}
      <KeyFindingsCard result={result} />

      {/* Confidence Scores if available */}
      {result.advanced_analysis?.confidence_scores && (
        <ConfidenceScoresCard confidenceScores={result.advanced_analysis.confidence_scores} />
      )}
    </div>
  );
};

export default BasicAnalysisSection;
