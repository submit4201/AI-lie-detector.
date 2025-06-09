import React from 'react';
import { Card, CardContent } from "@/components/ui/card"; // Shadcn/ui Card components
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"; // Shadcn/ui Accordion components

/**
 * @component DeceptionIndicatorsCard
 * @description Displays a list of deception indicators or a message if none are detected.
 * Note: This component is defined but currently NOT USED within the BasicAnalysisSection's rendered output.
 * It can be integrated if direct display of `red_flags_per_speaker` is desired in this section.
 * @param {object} props - Component props.
 * @param {string[]} props.deceptionFlags - An array of strings, each a deception indicator.
 */
const DeceptionIndicatorsCard = ({ deceptionFlags }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🚩 Deception Indicators</h3>
      {/* Conditionally render flags or a "no indicators" message. */}
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
          <p className="text-green-200">✅ No significant deception indicators detected based on current analysis parameters for this section.</p>
        </div>
      )}
    </CardContent>
  </Card>
);

/**
 * @component ConfidenceScoresCard
 * @description Displays various confidence scores from the analysis, often from an `advanced_analysis` object.
 * @param {object} props - Component props.
 * @param {object} props.confidenceScores - An object where keys are categories and values are scores (0-100).
 */
const ConfidenceScoresCard = ({ confidenceScores }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">📊 Model Confidence Scores</h3>
      <div className="space-y-3">
        {/* Map over confidence score entries (e.g., "transcription_confidence": 95). */}
        {Object.entries(confidenceScores).map(([category, score], index) => (
          <div key={index} className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
            <div className="flex justify-between items-center mb-2">
              {/* Display category name (e.g., "Transcription Confidence"). */}
              <span className="text-gray-200 capitalize font-medium">{category.replace('_', ' ')}</span>
              {/* Display score with dynamic coloring. */}
              <span className={`font-semibold ${score > 70 ? 'text-green-400' : score > 40 ? 'text-yellow-400' : 'text-red-400'}`}>
                {score.toFixed(1)}%
              </span>
            </div>
            {/* Progress bar representation of the score. */}
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

/**
 * @component BehavioralAnalysisCard
 * @description Displays a summary of behavioral analysis, including speech patterns,
 * communication style, emotional state, and stress indicators.
 * It pulls data from both `linguistic_analysis` and `gemini_summary` parts of the result.
 * @param {object} props - Component props.
 * @param {object} props.result - The main analysis result object.
 */
const BehavioralAnalysisCard = ({ result }) => (
  // This card is designed to be embedded within an AccordionContent.
  <Card className="bg-transparent shadow-none border-none rounded-none">
    <CardContent className="p-0">
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        <div className="space-y-4">
          {/* Speech Patterns Summary with quantitative details */}
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
            <span className="font-semibold text-blue-300">🎵 Speech Patterns:</span>
            <p className="text-gray-200 mt-1 text-sm">
              {/* Display a preview of speech patterns text, or a placeholder. */}
              {result.linguistic_analysis?.speech_patterns?.substring(0, 120) || 
               "Analysis of speech rhythm, pacing, and vocal patterns."}
              {result.linguistic_analysis?.speech_patterns?.length > 120 && "..."}
            </p>
            {/* Quantitative metrics related to speech patterns. */}
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
                    {result.linguistic_analysis?.word_count ?? 'N/A'} {/* Use nullish coalescing for 0 values */}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Communication Style with quantitative details */}
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-purple-400/30">
            <span className="font-semibold text-purple-300">💬 Communication Style:</span>
            <p className="text-gray-200 mt-1 text-sm">
              {/* Display a preview of communication style text from Gemini summary, or a placeholder. */}
              {typeof result.gemini_summary === 'object' && result.gemini_summary?.communication_style?.substring(0, 120) ||
               (typeof result.gemini_summary === 'string' && result.gemini_summary.substring(0, 120)) || // Fallback if gemini_summary is a string
               "Analyzing communication patterns and verbal behaviors."}
              {((typeof result.gemini_summary === 'object' && result.gemini_summary?.communication_style?.length > 120) ||
               (typeof result.gemini_summary === 'string' && result.gemini_summary.length > 120)) ? "..." : ""}
            </p>
            {/* Quantitative metrics related to communication style. */}
            <div className="mt-2 pt-2 border-t border-purple-400/30">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-400">Formality Score:</span>
                  <span className="text-purple-200">
                    {result.linguistic_analysis?.formality_score !== undefined
                      ? `${Math.round(result.linguistic_analysis.formality_score)}/100`
                      : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Complexity Score:</span>
                  <span className="text-purple-200">
                    {result.linguistic_analysis?.complexity_score !== undefined
                      ? `${Math.round(result.linguistic_analysis.complexity_score)}/100`
                      : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Emotional State / Consistency with quantitative details */}
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-yellow-400/30">
            <span className="font-semibold text-yellow-300">😊 Emotional State & Consistency:</span>
            <p className="text-gray-200 mt-1 text-sm">
              {/* Display emotional state from Gemini or emotional consistency from linguistic analysis. */}
              {typeof result.gemini_summary === 'object' && result.gemini_summary?.emotional_state?.substring(0, 120) ||
               result.linguistic_analysis?.emotional_consistency?.substring(0, 120) ||
               "Evaluating emotional consistency and authenticity."}
              {((typeof result.gemini_summary === 'object' && result.gemini_summary?.emotional_state?.length > 120) ||
                (result.linguistic_analysis?.emotional_consistency?.length > 120)) && "..."}
            </p>
            {/* Display primary detected emotion. */}
            {result.emotion_analysis && Array.isArray(result.emotion_analysis) && result.emotion_analysis.length > 0 && (
              <div className="mt-2 pt-2 border-t border-yellow-400/30">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">Primary Emotion Detected:</span>
                  <span className="text-yellow-200 capitalize">
                    {result.emotion_analysis[0].label.replace('_', ' ')} ({Math.round(result.emotion_analysis[0].score * 100)}%)
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Stress Indicators from linguistic analysis */}
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
            <span className="font-semibold text-red-300">⚡ Stress & Hesitation Indicators:</span>
            <div className="mt-2 space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-400">Filler Words Count:</span>
                <span className="text-red-200">
                  {result.linguistic_analysis?.filler_count ?? 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Hesitation Markers Count:</span>
                <span className="text-red-200">
                  {result.linguistic_analysis?.hesitation_count ?? 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Word/Phrase Repetitions:</span>
                <span className="text-red-200">
                  {result.linguistic_analysis?.repetition_count ?? 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Hesitation Rate (per min):</span>
                <span className="text-red-200">
                  {result.linguistic_analysis?.hesitation_rate_hpm  // Corrected field name
                    ? `${result.linguistic_analysis.hesitation_rate_hpm.toFixed(1)}/min`
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

/**
 * @component KeyFindingsCard
 * @description Displays key findings from the AI analysis, focusing on credibility strengths,
 * key concerns, and motivation assessment from the Gemini summary.
 * @param {object} props - Component props.
 * @param {object} props.result - The main analysis result object.
 */
const KeyFindingsCard = ({ result }) => (
  // This card is designed to be embedded within an AccordionContent.
  <Card className="bg-transparent shadow-none border-none rounded-none">
    <CardContent className="p-0">
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        <div className="space-y-3">
          {/* Display Strengths if available in Gemini summary. */}
          {typeof result.gemini_summary === 'object' && result.gemini_summary?.strengths && (
            <div className="bg-green-500/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
              <span className="font-semibold text-green-300">✅ Credibility Strengths Identified:</span>
              <p className="text-gray-200 mt-1 text-sm whitespace-pre-wrap">{result.gemini_summary.strengths}</p>
            </div>
          )}

          {/* Display Key Concerns if available in Gemini summary. */}
          {typeof result.gemini_summary === 'object' && result.gemini_summary?.key_concerns && (
            <div className="bg-red-500/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
              <span className="font-semibold text-red-300">⚠️ Key Concerns Identified:</span>
              <p className="text-gray-200 mt-1 text-sm whitespace-pre-wrap">{result.gemini_summary.key_concerns}</p>
            </div>
          )}

          {/* Display Motivation Assessment if available in Gemini summary. */}
          {typeof result.gemini_summary === 'object' && result.gemini_summary?.motivation && (
            <div className="bg-blue-500/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
              <span className="font-semibold text-blue-300">🎯 Assessed Motivation:</span>
              <p className="text-gray-200 mt-1 text-sm whitespace-pre-wrap">{result.gemini_summary.motivation}</p>
            </div>
          )}
        </div>
      </div>
    </CardContent>
  </Card>
);

/**
 * @component BasicAnalysisSection
 * @description This section displays fundamental analysis results, typically including
 * behavioral analysis and key findings, often presented within an accordion structure
 * for better organization. It may also display confidence scores if available.
 *
 * @param {object} props - The properties passed to the component.
 * @param {object} props.result - The main analysis result object containing data for sub-components.
 * @returns {JSX.Element|null} The BasicAnalysisSection UI, or null if no result is provided.
 */
const BasicAnalysisSection = ({ result }) => {
  if (!result) return null; // Do not render if no result data.

  // Defines which accordion items are open by default.
  const defaultOpenValues = ["item-behavioral-analysis", "item-key-findings"];

  return (
    // Main container for this section.
    <div className="space-y-6 h-fit">
      {/* Accordion for organizing Behavioral Analysis and Key Findings. */}
      <Accordion type="multiple" defaultValue={defaultOpenValues} className="space-y-4">

        {/* Accordion Item: Behavioral Analysis */}
        {/* This check for `result` might be redundant if the parent `BasicAnalysisSection` already ensures `result` exists. */}
        {result && (
          <AccordionItem value="item-behavioral-analysis" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              🧠 Behavioral Analysis Summary
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              {/* Renders the BehavioralAnalysisCard with relevant data from the result. */}
              <BehavioralAnalysisCard result={result} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Accordion Item: Key Findings */}
        {result && (
          <AccordionItem value="item-key-findings" className="bg-white/5 backdrop-blur-md border-white/10 shadow-lg rounded-lg data-[state=closed]:rounded-lg data-[state=open]:rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white hover:no-underline p-6 data-[state=open]:border-b data-[state=open]:border-white/20">
              🔍 AI Key Findings & Interpretations
            </AccordionTrigger>
            <AccordionContent className="p-6 pt-4">
              {/* Renders the KeyFindingsCard with relevant data from the result. */}
              <KeyFindingsCard result={result} />
            </AccordionContent>
          </AccordionItem>
        )}
      </Accordion>

      {/* Standalone Card: Confidence Scores (if available in the result structure) */}
      {/* This is rendered outside the accordion, directly in the BasicAnalysisSection. */}
      {result.advanced_analysis?.confidence_scores && (
        <ConfidenceScoresCard confidenceScores={result.advanced_analysis.confidence_scores} />
      )}
    </div>
  );
};

export default BasicAnalysisSection;
