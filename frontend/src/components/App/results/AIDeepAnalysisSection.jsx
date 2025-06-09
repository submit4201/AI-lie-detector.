import React from 'react';
import { Card, CardContent } from "@/components/ui/card"; // Shadcn/ui Card component
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"; // Shadcn/ui Accordion components
// Imported Card components for specific analysis dimensions
import ManipulationAssessmentCard from './ManipulationAssessmentCard';
import ArgumentAnalysisCard from './ArgumentAnalysisCard';
import SpeakerAttitudeCard from './SpeakerAttitudeCard';
import EnhancedUnderstandingCard from './EnhancedUnderstandingCard';

// --- Internally Defined Card Components for this Section ---
// These components are defined within this file as they are specific to the layout
// and data structure of the AIDeepAnalysisSection.

/**
 * @component AnalysisErrorCard
 * @description Displays an error message if the AI analysis data is incomplete or an error is reported.
 * @param {object} props - Component props.
 * @param {object} props.geminiData - The Gemini analysis part of the result, which might contain an error.
 */
const AnalysisErrorCard = ({ geminiData }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">❌ Analysis Error</h3>
      <div className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-lg p-4">
        <p className="text-red-200">
          {/* Display error from geminiData if available, otherwise a generic message. */}
          {geminiData?.error || 'Failed to process or retrieve complete AI analysis.'}
        </p>
        {/* Display Gemini summary text if it exists, as it might contain further error details from Gemini itself. */}
        {geminiData?.gemini_summary && typeof geminiData.gemini_summary === 'string' && (
          <div className="mt-3 pt-3 border-t border-red-400/30">
            <p className="text-red-100 text-sm whitespace-pre-wrap">{geminiData.gemini_summary}</p>
          </div>
        )}
      </div>
    </CardContent>
  </Card>
);

/**
 * @component GeminiSummaryCard
 * @description Displays the structured summary from the Gemini AI analysis, breaking it down by aspects like tone, motivation, etc.
 * @param {object} props - Component props.
 * @param {object|string} props.summary - The `gemini_summary` object or a fallback string.
 */
const GeminiSummaryCard = ({ summary }) => (
  // This card is designed to be embedded within an AccordionContent, so it has minimal styling.
  <Card className="bg-transparent shadow-none border-none rounded-none">
    <CardContent className="p-0"> {/* No padding from CardContent itself, parent AccordionContent provides it */}
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        {/* Check if summary is a structured object or a plain string (fallback). */}
        {typeof summary === 'object' && summary !== null ? (
          <div className="space-y-3">
            {/* Conditionally render each part of the Gemini summary. */}
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
             {/* Key Concerns and Strengths are part of GeminiSummary but were missing here, adding them */}
            {summary.key_concerns && (
              <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
                <span className="font-semibold text-red-300">🔑 Key Concerns:</span>
                <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.key_concerns}</p>
              </div>
            )}
            {summary.strengths && (
              <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-teal-400/30">
                <span className="font-semibold text-teal-300">💪 Strengths:</span>
                <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.strengths}</p>
              </div>
            )}
          </div>
        ) : (
          // Fallback if summary is just a string.
          <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{summary}</p>
        )}
      </div>
    </CardContent>
  </Card>
);

// Note: SessionInsightsCard was defined here but is imported as a separate component in ResultsDisplay.jsx.
// If it's meant to be used here, it should be passed `insights={result.session_insights}`.
// For now, assuming it's handled by the parent `ResultsDisplay` component.

/**
 * @component LinguisticAnalysisCard
 * @description Displays the qualitative linguistic analysis patterns.
 * @param {object} props - Component props.
 * @param {object} props.analysis - The `linguistic_analysis` object from the main result.
 */
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

/**
 * @component SpeakerSpecificAnalysisCard
 * @description Displays red flags or deception indicators identified for each speaker.
 * @param {object} props - Component props.
 * @param {object} props.analysis - The `red_flags_per_speaker` object from the main result.
 */
const SpeakerSpecificAnalysisCard = ({ analysis }) => (
  <Card className="bg-transparent shadow-none border-none rounded-none">
    <CardContent className="p-0">
      <div className="space-y-4">
        {/* Iterate over speakers found in the analysis. */}
        {Object.entries(analysis).map(([speaker, flags], index) => (
          <div key={index} className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <h4 className="text-white font-semibold mb-3">{speaker}</h4>
            {/* Check if there are any flags for this speaker. */}
            {Array.isArray(flags) && flags.length > 0 ? (
              <div className="space-y-2">
                {/* List each flag. */}
                {flags.map((flag, flagIndex) => (
                  <div key={flagIndex} className="bg-red-500/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
                    <span className="text-red-200">⚠️ {flag}</span>
                  </div>
                ))}
              </div>
            ) : (
              // Message if no flags are detected for this speaker.
              <div className="bg-green-500/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
                <span className="text-green-200">✅ No significant deception indicators detected for this speaker.</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </CardContent>
  </Card>
);

// SpeakerTranscriptsCard and DebugInfoCard are defined but not used in the current AIDeepAnalysisSection accordion.
// They are kept here in case they are intended for future use or were part of an older design.
// If they are truly unused, they could be removed or commented out.
// For now, adding basic JSDoc comments.

/**
 * @component SpeakerTranscriptsCard
 * @description Displays transcripts separated by speaker. (Currently not used in AIDeepAnalysisSection accordion)
 * @param {object} props - Component props.
 * @param {object} props.transcripts - The `speaker_transcripts` object.
 */
const SpeakerTranscriptsCard = ({ transcripts }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
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

/**
 * @component RecommendationsCard
 * @description Displays actionable recommendations based on the analysis.
 * @param {object} props - Component props.
 * @param {Array<string>|string} props.recommendations - List of recommendation strings or a single string.
 */
const RecommendationsCard = ({ recommendations }) => (
  <Card className="bg-transparent shadow-none border-none rounded-none">
    <CardContent className="p-0">
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        {Array.isArray(recommendations) && recommendations.length > 0 ? (
          <div className="space-y-3">
            {recommendations.map((rec, index) => (
              <div key={index} className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border-l-4 border-green-400">
                <div className="flex items-start">
                  {/* Numbered bullet point style */}
                  <span className="bg-green-900/50 text-green-300 font-bold rounded-full w-6 h-6 flex items-center justify-center text-sm mr-3 mt-0.5 shrink-0">
                    {index + 1}
                  </span>
                  <p className="text-gray-200 leading-relaxed">{rec}</p>
                </div>
              </div>
            ))}
          </div>
        ) : typeof recommendations === 'string' ? (
          <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{recommendations}</p>
        ) : (
           <p className="text-gray-400">No specific recommendations provided at this time.</p>
        )}
      </div>
    </CardContent>
  </Card>
);

// DebugInfoCard is defined but not used in the current AIDeepAnalysisSection accordion.
/**
 * @component DebugInfoCard
 * @description Displays debugging or metadata related to the analysis. (Currently not used in AIDeepAnalysisSection accordion)
 * @param {object} props - Component props.
 * @param {object} props.metadata - Object containing debug information.
 */
const DebugInfoCard = ({ metadata }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
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


/**
 * @component AIDeepAnalysisSection
 * @description Renders a section with an accordion interface to display various detailed
 * AI-driven analysis results, including Gemini summary, manipulation assessment,
 * argument analysis, speaker attitude, enhanced understanding, linguistic patterns,
 * speaker-specific flags, and recommendations.
 *
 * @param {object} props - The properties passed to the component.
 * @param {object} props.result - The main analysis result object containing all detailed analysis sections.
 * @param {function} props.parseGeminiAnalysis - Utility function (currently seems unused here, but passed down).
 * @param {function} props.getCredibilityColor - Utility function (currently seems unused here).
 * @param {function} props.getCredibilityLabel - Utility function (currently seems unused here).
 * @param {function} props.formatConfidenceLevel - Utility function (currently seems unused here).
 * @param {Array<object>} props.sessionHistory - Session history (currently seems unused here).
 * @returns {JSX.Element|null} The AI Deep Analysis section UI, or null if no result.
 */
const AIDeepAnalysisSection = ({ result, parseGeminiAnalysis, getCredibilityColor, getCredibilityLabel, formatConfidenceLevel, sessionHistory }) => {
  if (!result) return null; // Do not render if there's no result object.

  // Check if essential AI analysis data is present. If not, show an error/incomplete message.
  // `gemini_summary` is a good indicator of whether the core AI analysis ran.
  // `credibility_score` is also a key top-level metric from AI.
  if (!result.gemini_summary || result.credibility_score === undefined) {
    // Render a specific card or message indicating that AI deep analysis is unavailable or incomplete.
    return (
      <div className="space-y-6 h-fit">
        <div className="text-center lg:text-left">
          <h2 className="text-2xl font-bold text-white mb-2">🤖 AI Deep Analysis</h2>
          <div className="w-16 h-1 bg-gradient-to-r from-green-500 to-blue-500 rounded mx-auto lg:mx-0"></div>
        </div>
        {/* Using AnalysisErrorCard or a similar display for incomplete data */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
          <CardContent className="p-6">
            <h3 className="text-xl font-semibold text-white mb-4">⚠️ AI Analysis Incomplete</h3>
            <p className="text-gray-300">Detailed AI-driven analysis data (e.g., summary, specific assessments) is missing or was not successfully processed for this result.</p>
            {result.error && <p className="text-red-300 mt-2">Error reported: {result.error}</p>}
          </CardContent>
        </Card>
      </div>
    );
  }

  // Default open accordion items for better user experience.
  const defaultOpenValues = [
    "item-gemini-summary", // Keep Gemini summary open by default.
    "item-manipulation-assessment",
    "item-argument-analysis",
    "item-speaker-attitude",
    "item-enhanced-understanding",
    // "item-linguistic-analysis", // Often lengthy, can be closed by default.
    // "item-speaker-specific",    // Can be closed by default.
    // "item-recommendations"      // Can be closed by default.
  ];

  // Main container for the AI Deep Analysis section.
  return (
    <div className="space-y-6 h-fit">
      {/* Section Title */}
      <div className="text-center lg:text-left">
        <h2 className="text-2xl font-bold text-white mb-2">🤖 AI Deep Analysis & Insights</h2>
        {/* Decorative underline */}
        <div className="w-16 h-1 bg-gradient-to-r from-purple-500 to-teal-500 rounded mx-auto lg:mx-0 mb-6"></div>
      </div>

      {/* Accordion container for collapsible analysis sections. */}
      <Accordion type="multiple" defaultValue={defaultOpenValues} className="space-y-4">

        {/* Accordion Item: Core AI Summary (from Gemini) */}
        {result.gemini_summary && (
          <AccordionItem value="item-gemini-summary" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              📋 Overall AI Summary
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              {/* Renders the structured Gemini summary. */}
              <GeminiSummaryCard summary={result.gemini_summary} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Accordion Item: Manipulation Assessment */}
        {result.manipulation_assessment && (
          <AccordionItem value="item-manipulation-assessment" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              🛡️ Manipulation Tactics Assessment
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              {/* Renders manipulation assessment details. */}
              <ManipulationAssessmentCard assessment={result.manipulation_assessment} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Accordion Item: Argument Analysis */}
        {result.argument_analysis && (
          <AccordionItem value="item-argument-analysis" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              ⚖️ Argument Coherence & Structure
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              {/* Renders argument analysis details. */}
              <ArgumentAnalysisCard analysis={result.argument_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Accordion Item: Speaker Attitude */}
        {result.speaker_attitude && (
          <AccordionItem value="item-speaker-attitude" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              🗣️ Speaker Attitude & Tone
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              {/* Renders speaker attitude details. */}
              <SpeakerAttitudeCard attitude={result.speaker_attitude} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Accordion Item: Enhanced Understanding */}
        {result.enhanced_understanding && (
          <AccordionItem value="item-enhanced-understanding" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              💡 Deeper Understanding & Follow-ups
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              {/* Renders enhanced understanding details like inconsistencies and follow-up questions. */}
              <EnhancedUnderstandingCard understanding={result.enhanced_understanding} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Accordion Item: Qualitative Linguistic Analysis (descriptive part) */}
        {result.linguistic_analysis && (
          <AccordionItem value="item-linguistic-analysis" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              📝 Qualitative Linguistic Insights
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              {/* Renders descriptive linguistic patterns. */}
              <LinguisticAnalysisCard analysis={result.linguistic_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Accordion Item: Speaker-Specific Red Flags/Deception Indicators */}
        {result.red_flags_per_speaker && Object.keys(result.red_flags_per_speaker).length > 0 && (
          <AccordionItem value="item-speaker-specific" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              🚩 Speaker-Specific Deception Indicators
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              {/* Renders red flags detected for each speaker. */}
              <SpeakerSpecificAnalysisCard analysis={result.red_flags_per_speaker} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Accordion Item: Actionable Recommendations */}
        {result.recommendations && result.recommendations.length > 0 && (
          <AccordionItem value="item-recommendations" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              🚀 Actionable Recommendations
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              {/* Renders actionable recommendations. */}
              <RecommendationsCard recommendations={result.recommendations} />
            </AccordionContent>
          </AccordionItem>
        )}
      </Accordion>
    </div>
  );
};

export default AIDeepAnalysisSection;
