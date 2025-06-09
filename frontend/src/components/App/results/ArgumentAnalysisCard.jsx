import React from 'react';
import { Card, CardContent } from "@/components/ui/card"; // Shadcn/ui Card components

/**
 * @component ListItem
 * @description A simple stateless component to render a styled list item.
 * @param {object} props - Component props.
 * @param {string} props.item - The text content of the list item.
 * @param {string} [props.colorClass="text-gray-300"] - Tailwind CSS class for text color.
 */
const ListItem = ({ item, colorClass = "text-gray-300" }) => (
  // Applies styling for a list item, including background, padding, rounded corners, and border.
  <li className={`${colorClass} text-sm bg-black/20 p-2 rounded-md border border-white/10`}>
    {item}
  </li>
);

/**
 * @component ArgumentAnalysisCard
 * @description Displays the results of an argument analysis, including its strengths,
 * weaknesses, and an overall coherence score visualized with a progress bar.
 * This card is typically used within an accordion item in a larger analysis display.
 *
 * @param {object} props - Component props.
 * @param {object|null} props.analysis - The argument analysis data object. Expected to contain:
 *   - `argument_strengths` (Array<string>): List of identified strengths.
 *   - `argument_weaknesses` (Array<string>): List of identified weaknesses.
 *   - `overall_argument_coherence_score` (number): Score from 0-100.
 * @returns {JSX.Element} The ArgumentAnalysisCard UI, or a fallback message if analysis data is unavailable.
 */
const ArgumentAnalysisCard = ({ analysis }) => {
  // If no analysis data is provided, render a fallback message.
  if (!analysis) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Argument analysis data not available.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Destructure analysis data with default values to prevent errors if fields are missing.
  const {
    argument_strengths = [], // Default to an empty array if not provided.
    argument_weaknesses = [],  // Default to an empty array.
    overall_argument_coherence_score = 0 // Default to 0 if not provided.
  } = analysis;

  return (
    // Main card container for argument analysis. Transparent background as it's meant to be within an accordion.
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0"> {/* No padding from CardContent, parent provides it. */}
        {/* Inner container with styling for the content block. */}
        <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 space-y-4">

          {/* Section for Overall Argument Coherence Score */}
          <div>
            <h4 className="text-md font-semibold text-blue-300 mb-2">Overall Argument Coherence Score</h4>
            <div className="flex items-center">
              {/* Progress bar visual for the coherence score. */}
              <div className="w-full bg-gray-700 rounded-full h-2.5 mr-3">
                <div
                  className="bg-blue-500 h-2.5 rounded-full" // Blue color for the progress bar fill.
                  style={{ width: `${overall_argument_coherence_score}%` }} // Width based on score.
                ></div>
              </div>
              {/* Numerical display of the score. */}
              <span className="text-blue-200 font-bold">{overall_argument_coherence_score}/100</span>
            </div>
          </div>

          {/* Section for Argument Strengths */}
          <div>
            <h4 className="text-md font-semibold text-green-300 mb-2">Identified Strengths</h4>
            {/* Conditionally render the list of strengths or a "None identified" message. */}
            {argument_strengths.length > 0 ? (
              <ul className="space-y-1 list-disc list-inside pl-1">
                {/* Map over strengths and render each using the ListItem component. */}
                {argument_strengths.map((strength, index) => (
                  <ListItem key={index} item={strength} colorClass="text-green-200" />
                ))}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">No specific argument strengths identified.</p>
            )}
          </div>

          {/* Section for Argument Weaknesses */}
          <div>
            <h4 className="text-md font-semibold text-red-300 mb-2">Identified Weaknesses</h4>
            {/* Conditionally render the list of weaknesses or a "None identified" message. */}
            {argument_weaknesses.length > 0 ? (
              <ul className="space-y-1 list-disc list-inside pl-1">
                {/* Map over weaknesses and render each using the ListItem component. */}
                {argument_weaknesses.map((weakness, index) => (
                  <ListItem key={index} item={weakness} colorClass="text-red-200" />
                ))}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">No specific argument weaknesses identified.</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ArgumentAnalysisCard;
