import React from 'react';
import { Card, CardContent } from "@/components/ui/card";

// Individual card components for AI Deep Analysis
// These could be further broken down if they become too complex or are reused.

const AnalysisErrorCard = ({ geminiData }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">❌ Analysis Error</h3>
      <div className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-lg p-4">
        <p className="text-red-200">
          {geminiData?.error || 'Failed to process AI analysis'}
        </p>
        {geminiData?.gemini_summary && (
          <div className="mt-3 pt-3 border-t border-red-400/30">
            <p className="text-red-100 text-sm">{geminiData.gemini_summary}</p>
          </div>
        )}
      </div>
    </CardContent>
  </Card>
);

const CredibilityScoreCard = ({ score, getColor, getLabel }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🎯 Credibility Assessment</h3>
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <span className="text-white font-semibold text-lg">Overall Score</span>
          <span
            className="text-2xl font-bold"
            style={{ color: getColor(score) }}
          >
            {score}/100
          </span>
        </div>
        <div className="w-full bg-white/20 rounded-full h-3 mb-3">
          <div
            className="h-3 rounded-full transition-all duration-1000"
            style={{
              width: `${score}%`,
              background: `linear-gradient(90deg, ${getColor(score)}, ${getColor(score)}88)`
            }}
          ></div>
        </div>
        <p
          className="text-center font-semibold text-lg"
          style={{ color: getColor(score) }}
        >
          {getLabel(score)}
        </p>
      </div>
    </CardContent>
  </Card>
);

const GeminiSummaryCard = ({ summary }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">📋 Overall Summary</h3>
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        {typeof summary === 'object' ? (
          <div className="space-y-3">
            {summary.tone && (
              <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-purple-400/30">
                <span className="font-semibold text-purple-300">🎭 Tone Analysis:</span>
                <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.tone}</p>
              </div>
            )}
            {summary.motivation && (
              <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
                <span className="font-semibold text-blue-300">🎯 Motivation Assessment:</span>
                <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.motivation}</p>
              </div>
            )}
            {summary.credibility && (
              <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
                <span className="font-semibold text-green-300">✅ Credibility Analysis:</span>
                <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.credibility}</p>
              </div>
            )}
            {summary.emotional_state && (
              <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-yellow-400/30">
                <span className="font-semibold text-yellow-300">😊 Emotional State:</span>
                <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.emotional_state}</p>
              </div>
            )}
            {summary.communication_style && (
              <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-cyan-400/30">
                <span className="font-semibold text-cyan-300">💬 Communication Style:</span>
                <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.communication_style}</p>
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{summary}</p>
        )}
      </div>
    </CardContent>
  </Card>
);

const SessionInsightsCard = ({ insights }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🔍 Session Insights</h3>
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        <div className="space-y-3">
          {insights.consistency_analysis && (
            <div className="bg-blue-500/10 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
              <span className="font-semibold text-blue-300">Consistency Analysis:</span>
              <p className="text-gray-200 mt-1 whitespace-pre-wrap">{insights.consistency_analysis}</p>
            </div>
          )}
          {insights.behavioral_evolution && (
            <div className="bg-orange-500/10 backdrop-blur-sm p-3 rounded-lg border border-orange-400/30">
              <span className="font-semibold text-orange-300">Behavioral Evolution:</span>
              <p className="text-gray-200 mt-1 whitespace-pre-wrap">{insights.behavioral_evolution}</p>
            </div>
          )}
          {insights.risk_trajectory && (
            <div className="bg-red-500/10 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
              <span className="font-semibold text-red-300">Risk Trajectory:</span>
              <p className="text-gray-200 mt-1 whitespace-pre-wrap">{insights.risk_trajectory}</p>
            </div>
          )}
          {insights.conversation_dynamics && (
            <div className="bg-green-500/10 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
              <span className="font-semibold text-green-300">Conversation Dynamics:</span>
              <p className="text-gray-200 mt-1 whitespace-pre-wrap">{insights.conversation_dynamics}</p>
            </div>
          )}
        </div>
      </div>
    </CardContent>
  </Card>
);

const LinguisticAnalysisCard = ({ analysis }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">📝 Linguistic Analysis</h3>
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        <div className="space-y-3">
          {analysis.speech_patterns && (
            <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
              <span className="font-semibold text-blue-300">🎵 Speech Patterns:</span>
              <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.speech_patterns}</p>
            </div>
          )}
          {analysis.word_choice && (
            <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-purple-400/30">
              <span className="font-semibold text-purple-300">📖 Word Choice:</span>
              <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.word_choice}</p>
            </div>
          )}
          {analysis.emotional_consistency && (
            <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-yellow-400/30">
              <span className="font-semibold text-yellow-300">💭 Emotional Consistency:</span>
              <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.emotional_consistency}</p>
            </div>
          )}
          {analysis.detail_level && (
            <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
              <span className="font-semibold text-green-300">🔍 Detail Level:</span>
              <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.detail_level}</p>
            </div>
          )}
        </div>
      </div>
    </CardContent>
  </Card>
);

const RiskAssessmentCard = ({ assessment }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">⚠️ Risk Assessment</h3>
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        <div className="mb-4 text-center">
          <div className={`inline-block px-6 py-3 rounded-lg font-bold text-lg ${
            assessment.overall_risk === 'high' ? 'bg-red-500/30 text-red-200 border border-red-400/50' :
            assessment.overall_risk === 'medium' ? 'bg-yellow-500/30 text-yellow-200 border border-yellow-400/50' :
            'bg-green-500/30 text-green-200 border border-green-400/50'
          }`}>
            {assessment.overall_risk.toUpperCase()} RISK
          </div>
        </div>

        {assessment.risk_factors && assessment.risk_factors.length > 0 && (
          <div className="mb-4">
            <h4 className="text-white font-semibold mb-2">🚩 Risk Factors:</h4>
            <div className="space-y-2">
              {assessment.risk_factors.map((factor, index) => (
                <div key={index} className="bg-red-500/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
                  <span className="text-red-200">• {factor}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {assessment.mitigation_suggestions && assessment.mitigation_suggestions.length > 0 && (
          <div>
            <h4 className="text-white font-semibold mb-2">💡 Mitigation Suggestions:</h4>
            <div className="space-y-2">
              {assessment.mitigation_suggestions.map((suggestion, index) => (
                <div key={index} className="bg-green-500/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
                  <span className="text-green-200">• {suggestion}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </CardContent>
  </Card>
);

const ConfidenceLevelCard = ({ level }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">📊 Analysis Confidence</h3>
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        <div className="text-center">
          <div className={`inline-block px-6 py-3 rounded-lg font-bold text-lg ${
            level === 'very_high' ? 'bg-green-500/30 text-green-200 border border-green-400/50' :
            level === 'high' ? 'bg-blue-500/30 text-blue-200 border border-blue-400/50' :
            level === 'medium' ? 'bg-yellow-500/30 text-yellow-200 border border-yellow-400/50' :
            level === 'low' ? 'bg-orange-500/30 text-orange-200 border border-orange-400/50' :
            'bg-red-500/30 text-red-200 border border-red-400/50'
          }`}>
            {level.replace('_', ' ').toUpperCase()} CONFIDENCE
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
);

const SpeakerSpecificAnalysisCard = ({ analysis }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🔍 Speaker-Specific Analysis</h3>
      <div className="space-y-4">
        {Object.entries(analysis).map(([speaker, flags], index) => (
          <div key={index} className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <h4 className="text-white font-semibold mb-3">{speaker}</h4>
            {Array.isArray(flags) && flags.length > 0 ? (
              <div className="space-y-2">
                {flags.map((flag, flagIndex) => (
                  <div key={flagIndex} className="bg-red-500/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
                    <span className="text-red-200">⚠️ {flag}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-green-500/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
                <span className="text-green-200">✅ No significant indicators detected</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </CardContent>
  </Card>
);

const SpeakerTranscriptsCard = ({ transcripts }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🗣️ Speaker Transcripts</h3>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {Object.entries(transcripts).map(([speaker, transcript], index) => (
          <div key={index} className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-white font-semibold mb-2">{speaker}</p>
            <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{transcript}</p>
          </div>
        ))}
        </div>
    </CardContent>
  </Card>
);

const RecommendationsCard = ({ recommendations }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">💡 Recommendations</h3>
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        {Array.isArray(recommendations) ? (
          <div className="space-y-3">
            {recommendations.map((rec, index) => (
              <div key={index} className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border-l-4 border-green-400">
                <div className="flex items-start">
                  <span className="bg-green-900/50 text-green-300 font-bold rounded-full w-6 h-6 flex items-center justify-center text-sm mr-3 mt-0.5 shrink-0">
                    {index + 1}
                  </span>
                  <p className="text-gray-200 leading-relaxed">{rec}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{recommendations}</p>
        )}
      </div>
    </CardContent>
  </Card>
);

const DebugInfoCard = ({ metadata }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🔧 Debug Information</h3>
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-gray-400">Processing Time:</span>
            <span className="text-white ml-2">{metadata.processing_time}s</span>
          </div>
          <div>
            <span className="text-gray-400">File Size:</span>
            <span className="text-white ml-2">{(metadata.file_size / 1024).toFixed(1)} KB</span>
          </div>
          <div>
            <span className="text-gray-400">Analysis Version:</span>
            <span className="text-white ml-2">{metadata.analysis_version}</span>
          </div>
          <div>
            <span className="text-gray-400">Timestamp:</span>
            <span className="text-white ml-2">{new Date(metadata.timestamp).toLocaleTimeString()}</span>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
);


// parseGeminiAnalysis is passed but likely not needed for top-level data anymore.
// It could be used internally by a sub-card if a specific text field needs deep parsing.
const AIDeepAnalysisSection = ({ result, parseGeminiAnalysis, getCredibilityColor, getCredibilityLabel, formatConfidenceLevel, sessionHistory }) => {
  // result is the full AnalyzeResponse object from the backend.
  if (!result) return null;

  // Error handling for Gemini can be based on a specific field or overall structure if necessary
  // For example, if gemini_summary is crucial and missing, or contains an error message from service.
  // The backend's validate_and_structure_gemini_response aims to always provide a structure.

  // Example: Check if core Gemini data is present, otherwise show an error or reduced view
  if (!result.gemini_summary || !result.credibility_score === undefined) {
     // This condition might need adjustment based on what's considered a "valid" minimal Gemini result
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-white mb-4">🤖 AI Deep Analysis</h2>
        <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
          <CardContent className="p-6">
            <h3 className="text-xl font-semibold text-white mb-4">⚠️ Analysis Incomplete</h3>
            <p className="text-gray-300">Detailed AI analysis data is missing or incomplete.</p>
            {/* Optionally, show result.error if the backend populates such a field */}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white mb-4">🤖 AI Deep Analysis</h2>

      {result.credibility_score !== undefined && (
        <CredibilityScoreCard
          score={result.credibility_score} // Direct from backend (0-100)
          getColor={(score) => getCredibilityColor(score / 100)} // Scale to 0-1 for color/label helpers
          getLabel={(score) => getCredibilityLabel(score / 100)} // Scale to 0-1 for color/label helpers
        />
      )}

      {result.gemini_summary && <GeminiSummaryCard summary={result.gemini_summary} />}

      {result.session_insights && sessionHistory && sessionHistory.length > 0 && (
        <SessionInsightsCard insights={result.session_insights} />
      )}

      {result.linguistic_analysis && <LinguisticAnalysisCard analysis={result.linguistic_analysis} />}
      {result.risk_assessment && <RiskAssessmentCard assessment={result.risk_assessment} />}

      {/* ConfidenceLevelCard expects the string value e.g. "high", "medium" */}
      {/* The formatConfidenceLevel helper is for numeric 0-1 scores, not this string. */}
      {/* So, we pass result.confidence_level directly if it's the string. */}
      {/* If ConfidenceLevelCard expected numeric, then formatConfidenceLevel(numeric_confidence_score) would be used. */}
      {/* Assuming ConfidenceLevelCard is designed for the string value from backend's AnalyzeResponse.confidence_level */}
      {result.confidence_level && <ConfidenceLevelCard level={result.confidence_level} />}


      {result.red_flags_per_speaker && Object.keys(result.red_flags_per_speaker).length > 0 && (
        <SpeakerSpecificAnalysisCard analysis={result.red_flags_per_speaker} />
      )}

      {result.speaker_transcripts && <SpeakerTranscriptsCard transcripts={result.speaker_transcripts} />}
      {result.recommendations && <RecommendationsCard recommendations={result.recommendations} />}

      {/* Assuming result.metadata might exist - this was in the original JSX but not in AnalyzeResponse model */}
      {/* If it's not part of AnalyzeResponse, this card won't render or will need different data */}
      {/* For now, keeping it conditional as in original code. */}
      {result.metadata && <DebugInfoCard metadata={result.metadata} />}
    </div>
  );
};

export default AIDeepAnalysisSection;
