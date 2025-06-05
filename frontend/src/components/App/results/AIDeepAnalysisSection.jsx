import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import ManipulationAssessmentCard from './ManipulationAssessmentCard';
import ArgumentAnalysisCard from './ArgumentAnalysisCard';
import SpeakerAttitudeCard from './SpeakerAttitudeCard';
import EnhancedUnderstandingCard from './EnhancedUnderstandingCard';

// Individual card components for AI Deep Analysis
// These are kept as they are, and will be wrapped by Accordion items.

const AnalysisErrorCard = ({ geminiData }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
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

const GeminiSummaryCard = ({ summary }) => (
  <Card className="bg-transparent shadow-none border-none rounded-none">
    {/* Removed CardContent padding and h3, as AccordionItem will handle padding and AccordionTrigger the title */}
    <CardContent className="p-0">
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
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🔍 Session Insights</h3>
      {/* Content of SessionInsightsCard */}
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
  <Card className="bg-transparent shadow-none border-none rounded-none">
    <CardContent className="p-0">
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

const SpeakerSpecificAnalysisCard = ({ analysis }) => (
  <Card className="bg-transparent shadow-none border-none rounded-none">
    <CardContent className="p-0">
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
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🗣️ Speaker Transcripts</h3>
      {/* Content of SpeakerTranscriptsCard */}
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
  <Card className="bg-transparent shadow-none border-none rounded-none">
    <CardContent className="p-0">
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
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🔧 Debug Information</h3>
      {/* Content of DebugInfoCard */}
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

const AIDeepAnalysisSection = ({ result, parseGeminiAnalysis, getCredibilityColor, getCredibilityLabel, formatConfidenceLevel, sessionHistory }) => {
  if (!result) return null;

  // Error handling for Gemini analysis
  if (!result.gemini_summary || result.credibility_score === undefined) {
    // ... error handling remains the same
    return (
      <div className="space-y-6 h-fit">
        <div className="text-center lg:text-left">
          <h2 className="text-2xl font-bold text-white mb-2">🤖 AI Deep Analysis</h2>
          <div className="w-16 h-1 bg-gradient-to-r from-green-500 to-blue-500 rounded mx-auto lg:mx-0"></div>
        </div>
        <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
          <CardContent className="p-6">
            <h3 className="text-xl font-semibold text-white mb-4">⚠️ Analysis Incomplete</h3>
            <p className="text-gray-300">Detailed AI analysis data is missing or incomplete.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const defaultOpenValues = [
    "item-gemini-summary",
    "item-manipulation-assessment",
    "item-argument-analysis",
    "item-speaker-attitude",
    "item-enhanced-understanding",
    "item-linguistic-analysis",
    "item-speaker-specific",
    "item-recommendations"
  ];

  return (
    <div className="space-y-6 h-fit">
      <div className="text-center lg:text-left">
        <h2 className="text-2xl font-bold text-white mb-2">🤖 AI Deep Analysis</h2>
        <div className="w-16 h-1 bg-gradient-to-r from-green-500 to-blue-500 rounded mx-auto lg:mx-0 mb-6"></div>
      </div>
      <Accordion type="multiple" defaultValue={defaultOpenValues} className="space-y-4">
        {/* Core AI Analysis */}
        {result.gemini_summary && (
          <AccordionItem value="item-gemini-summary" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              📋 Overall Summary
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              <GeminiSummaryCard summary={result.gemini_summary} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Manipulation Assessment */}
        {result.manipulation_assessment && (
          <AccordionItem value="item-manipulation-assessment" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              🛡️ Manipulation Assessment
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              <ManipulationAssessmentCard assessment={result.manipulation_assessment} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Argument Analysis */}
        {result.argument_analysis && (
          <AccordionItem value="item-argument-analysis" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              ⚖️ Argument Analysis
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              <ArgumentAnalysisCard analysis={result.argument_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Speaker Attitude */}
        {result.speaker_attitude && (
          <AccordionItem value="item-speaker-attitude" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              🗣️ Speaker Attitude
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              <SpeakerAttitudeCard attitude={result.speaker_attitude} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Enhanced Understanding */}
        {result.enhanced_understanding && (
          <AccordionItem value="item-enhanced-understanding" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              💡 Enhanced Understanding
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              <EnhancedUnderstandingCard understanding={result.enhanced_understanding} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Linguistic Patterns */}
        {result.linguistic_analysis && (
          <AccordionItem value="item-linguistic-analysis" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              📝 Linguistic Analysis
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              <LinguisticAnalysisCard analysis={result.linguistic_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Speaker-Specific Flags */}
        {result.red_flags_per_speaker && Object.keys(result.red_flags_per_speaker).length > 0 && (
          <AccordionItem value="item-speaker-specific" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              🔍 Speaker-Specific Analysis
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              <SpeakerSpecificAnalysisCard analysis={result.red_flags_per_speaker} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Actionable Recommendations */}
        {result.recommendations && (
          <AccordionItem value="item-recommendations" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              💡 Recommendations
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              <RecommendationsCard recommendations={result.recommendations} />
            </AccordionContent>
          </AccordionItem>
        )}
      </Accordion>
    </div>
  );
};

export default AIDeepAnalysisSection;
