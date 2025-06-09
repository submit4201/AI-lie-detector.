import React from 'react';
import { Card, CardContent } from "@/components/ui/card"; // Shadcn/ui Card components

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
 * @component ManipulationAssessmentCard
 * @description Displays the AI's assessment of manipulative language and tactics detected
 * in the speaker's communication. Includes a likelihood score, identified tactics,
 * an explanation, and example phrases.
 * This card is typically used within an accordion item in a larger analysis display.
 *
 * @param {object} props - Component props.
 * @param {object|null} props.assessment - The manipulation assessment data object. Expected to contain:
 *   - `manipulation_score` (number): Likelihood score (0-100).
 *   - `manipulation_tactics` (Array<string>): List of identified tactics.
 *   - `manipulation_explanation` (string): Explanation of the tactics.
 *   - `example_phrases` (Array<string>): Specific phrases indicating manipulation.
 * @returns {JSX.Element} The ManipulationAssessmentCard UI, or a fallback message if data is unavailable.
 */
const ManipulationAssessmentCard = ({ assessment }) => {
  // If no assessment data is provided, render a fallback message.
  if (!assessment) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Manipulation assessment data not available for this analysis.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Destructure fields from the assessment object with default values.
  const {
    manipulation_score = 0, // Default to 0 if not provided.
    manipulation_tactics = [],  // Default to an empty array.
    manipulation_explanation = "N/A", // Default explanation.
    example_phrases = []      // Default to an empty array.
  } = assessment;

  return (
    // Main card container. Transparent background as it's designed to be embedded.
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0"> {/* No padding from CardContent itself. */}
        {/* Inner container with styling for the content block and spacing between sections. */}
        <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 space-y-4">

          {/* Section for Manipulation Likelihood Score */}
          <div>
            <h4 className="text-md font-semibold text-purple-300 mb-2">Manipulation Likelihood Score</h4>
            <div className="flex items-center">
              {/* Progress bar visual for the manipulation score. */}
              <div className="w-full bg-gray-700 rounded-full h-2.5 mr-3">
                <div
                  className="bg-purple-500 h-2.5 rounded-full" // Purple color for the progress bar.
                  style={{ width: `${manipulation_score}%` }} // Width based on the score.
                ></div>
              </div>
              {/* Numerical display of the score. */}
              <span className="text-purple-200 font-bold">{manipulation_score}/100</span>
            </div>
          </div>

          {/* Section for Identified Manipulative Tactics */}
          <div>
            <h4 className="text-md font-semibold text-purple-300 mb-2">Identified Manipulative Tactics</h4>
            {/* Conditionally render the list of tactics or a "None detected" message. */}
            {manipulation_tactics.length > 0 ? (
              <ul className="space-y-1 list-disc list-inside pl-1">
                {/* Map over tactics and render each using the ListItem component. */}
                {manipulation_tactics.map((tactic, index) => <ListItem key={index} item={tactic} />)}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">No specific manipulative tactics prominently detected.</p>
            )}
          </div>

          {/* Section for Explanation of Tactics */}
          <div>
            <h4 className="text-md font-semibold text-purple-300 mb-2">Explanation of Tactics</h4>
            {/* Display the AI's explanation for the identified tactics. */}
            <p className="text-gray-300 text-sm bg-black/20 p-3 rounded-md border border-white/10 whitespace-pre-wrap">
              {manipulation_explanation || "No detailed explanation provided."}
            </p>
          </div>

          {/* Section for Example Phrases */}
          <div>
            <h4 className="text-md font-semibold text-purple-300 mb-2">Example Phrases (if any)</h4>
            {/* Conditionally render the list of example phrases or a "None provided" message. */}
            {example_phrases.length > 0 ? (
              <ul className="space-y-1 list-disc list-inside pl-1">
                {/* Map over example phrases and render each using the ListItem component. */}
                {example_phrases.map((phrase, index) => <ListItem key={index} item={phrase} />)}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">No specific example phrases were highlighted for manipulation.</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ManipulationAssessmentCard;
