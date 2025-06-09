import React from 'react';
import { Card, CardContent } from "@/components/ui/card"; // Shadcn/ui Card components
import { CheckCircle, XCircle } from 'lucide-react'; // Icons for boolean display

/**
 * @component ListItem
 * @description A simple stateless component to render a styled list item for this card.
 * @param {object} props - Component props.
 * @param {string} props.item - The text content of the list item.
 */
const ListItem = ({ item }) => (
  // Applies styling for a list item, including background, padding, rounded corners, and border.
  <li className="text-gray-300 text-sm bg-black/20 p-2 rounded-md border border-white/10">
    {item}
  </li>
);

/**
 * @component SpeakerAttitudeCard
 * @description Displays the AI's assessment of the speaker's attitude, including
 * respectfulness level, sarcasm detection, sarcasm confidence, and specific
 * tone indicators related to respect or sarcasm.
 * This card is typically used within an accordion item in a larger analysis display.
 *
 * @param {object} props - Component props.
 * @param {object|null} props.attitude - The speaker attitude data object. Expected to contain:
 *   - `respect_level_score` (number): Score from 0-100 indicating respectfulness.
 *   - `sarcasm_detected` (boolean): Whether sarcasm was detected.
 *   - `sarcasm_confidence_score` (number): Confidence in sarcasm detection (0-100).
 *   - `tone_indicators_respect_sarcasm` (Array<string>): List of relevant tone indicators.
 * @returns {JSX.Element} The SpeakerAttitudeCard UI, or a fallback message if data is unavailable.
 */
const SpeakerAttitudeCard = ({ attitude }) => {
  // If no attitude data is provided, render a fallback message.
  if (!attitude) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Speaker attitude data not available for this analysis.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Destructure fields from the attitude object with default values.
  const {
    respect_level_score = 50, // Default to a neutral 50 if not provided.
    sarcasm_detected = false,   // Default to false.
    sarcasm_confidence_score = 0, // Default to 0.
    tone_indicators_respect_sarcasm = [] // Default to an empty array.
  } = attitude;

  return (
    // Main card container. Transparent background as it's designed to be embedded.
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0"> {/* No padding from CardContent itself. */}
        {/* Inner container with styling for the content block and spacing between sections. */}
        <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 space-y-4">

          {/* Section for Respect Level Score */}
          <div>
            <h4 className="text-md font-semibold text-cyan-300 mb-2">Respect Level Score</h4>
            <div className="flex items-center">
              {/* Progress bar visual for the respect level score. */}
              <div className="w-full bg-gray-700 rounded-full h-2.5 mr-3">
                <div
                  className="bg-cyan-500 h-2.5 rounded-full" // Cyan color for the progress bar.
                  style={{ width: `${respect_level_score}%` }} // Width based on the score.
                ></div>
              </div>
              {/* Numerical display of the score. */}
              <span className="text-cyan-200 font-bold">{respect_level_score}/100</span>
            </div>
            <p className="text-xs text-gray-400 mt-1">Higher score generally indicates a more respectful tone perceived by the AI.</p>
          </div>

          {/* Section for Sarcasm Detection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-md font-semibold text-yellow-300 mb-2">Sarcasm Detected</h4>
              <div className="flex items-center space-x-2">
                {/* Display Yes/No with appropriate icons. */}
                {sarcasm_detected ?
                  <CheckCircle className="w-5 h-5 text-yellow-400" /> : // Yellow Check for 'Yes'
                  <XCircle className="w-5 h-5 text-gray-400" />    // Gray X for 'No'
                }
                <span className={`text-lg font-semibold ${sarcasm_detected ? 'text-yellow-200' : 'text-gray-300'}`}>
                  {sarcasm_detected ? "Yes" : "No"}
                </span>
              </div>
            </div>

            {/* Sarcasm Confidence Score (only shown if sarcasm is detected) */}
            {sarcasm_detected && (
              <div>
                <h4 className="text-md font-semibold text-yellow-300 mb-2">Sarcasm Confidence Score</h4>
                <div className="flex items-center">
                  {/* Progress bar for sarcasm confidence. */}
                  <div className="w-full bg-gray-700 rounded-full h-2.5 mr-3">
                    <div
                      className="bg-yellow-500 h-2.5 rounded-full"
                      style={{ width: `${sarcasm_confidence_score}%` }}
                    ></div>
                  </div>
                  {/* Numerical display of sarcasm confidence. */}
                  <span className="text-yellow-200 font-bold">{sarcasm_confidence_score}/100</span>
                </div>
              </div>
            )}
          </div>

          {/* Section for Tone Indicators related to Respect/Sarcasm */}
          <div>
            <h4 className="text-md font-semibold text-pink-300 mb-2">Key Tone Indicators (for Respect/Sarcasm)</h4>
            {/* Conditionally render the list of indicators or a "None provided" message. */}
            {tone_indicators_respect_sarcasm.length > 0 ? (
              <ul className="space-y-1 list-disc list-inside pl-1">
                {/* Map over indicators and render each using the ListItem component. */}
                {tone_indicators_respect_sarcasm.map((indicator, index) => <ListItem key={index} item={indicator} />)}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">No specific tone indicators for respect or sarcasm were highlighted by the AI.</p>
            )}
          </div>

        </div>
      </CardContent>
    </Card>
  );
};

export default SpeakerAttitudeCard;
