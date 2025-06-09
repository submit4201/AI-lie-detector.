import React from 'react';
import { Card, CardContent } from "@/components/ui/card"; // Shadcn/ui Card components

/**
 * @component ListItem
 * @description A simple stateless component to render a styled list item, typically with an icon.
 * @param {object} props - Component props.
 * @param {string} props.item - The text content of the list item.
 * @param {string} [props.icon="🔹"] - Emoji or icon character to display before the item text.
 */
const ListItem = ({ item, icon = "🔹" }) => (
  // List item with flex layout to align icon and text.
  <li className="text-gray-300 text-sm bg-black/20 p-2 rounded-md border border-white/10 flex items-start">
    {/* Icon element with right margin. */}
    <span className="mr-2 text-blue-400">{icon}</span>
    {/* Text content of the list item. */}
    <span>{item}</span>
  </li>
);

/**
 * @component EnhancedUnderstandingCard
 * @description Displays deeper insights derived from the AI analysis, such as key inconsistencies,
 * areas of evasiveness, suggested follow-up questions, and unverified claims made by the speaker.
 * This card is typically used within an accordion item.
 *
 * @param {object} props - Component props.
 * @param {object|null} props.understanding - The enhanced understanding data object. Expected to contain fields like:
 *   - `key_inconsistencies` (Array<string>)
 *   - `areas_of_evasiveness` (Array<string>)
 *   - `suggested_follow_up_questions` (Array<string>)
 *   - `unverified_claims` (Array<string>)
 * @returns {JSX.Element} The EnhancedUnderstandingCard UI, or a fallback message if data is unavailable.
 */
const EnhancedUnderstandingCard = ({ understanding }) => {
  // If no understanding data is provided, render a fallback message.
  if (!understanding) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Enhanced understanding data not available for this analysis.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Destructure fields from the understanding object with default empty arrays to prevent errors.
  const {
    key_inconsistencies = [],
    areas_of_evasiveness = [],
    suggested_follow_up_questions = [],
    unverified_claims = []
  } = understanding;

  return (
    // Main card container. Transparent background as it's designed to be embedded.
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0"> {/* No padding from CardContent itself. */}
        {/* Inner container with styling for the content block and spacing between sections. */}
        <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 space-y-4">

          {/* Section for Key Inconsistencies */}
          <div>
            <h4 className="text-md font-semibold text-red-300 mb-2">Key Inconsistencies / Contradictions</h4>
            {/* Conditionally render the list or a "None detected" message. */}
            {key_inconsistencies.length > 0 ? (
              <ul className="space-y-1">
                {key_inconsistencies.map((item, index) => <ListItem key={index} item={item} icon="⚠️"/>)}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">No significant inconsistencies detected in the statements.</p>
            )}
          </div>

          {/* Section for Areas of Evasiveness */}
          <div>
            <h4 className="text-md font-semibold text-yellow-300 mb-2">Potential Areas of Evasiveness</h4>
            {areas_of_evasiveness.length > 0 ? (
              <ul className="space-y-1">
                {areas_of_evasiveness.map((item, index) => <ListItem key={index} item={item} icon="🤫"/>)}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">No specific areas of evasiveness noted.</p>
            )}
          </div>

          {/* Section for Suggested Follow-up Questions */}
          <div>
            <h4 className="text-md font-semibold text-green-300 mb-2">Suggested Follow-up Questions</h4>
            {suggested_follow_up_questions.length > 0 ? (
              <ul className="space-y-1">
                {suggested_follow_up_questions.map((item, index) => <ListItem key={index} item={item} icon="❓"/>)}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">No specific follow-up questions suggested by the AI.</p>
            )}
          </div>

          {/* Section for Unverified Claims */}
          <div>
            <h4 className="text-md font-semibold text-purple-300 mb-2">Unverified Claims Requiring Fact-Checking</h4>
            {unverified_claims.length > 0 ? (
              <ul className="space-y-1">
                {unverified_claims.map((item, index) => <ListItem key={index} item={item} icon="🧐"/>)}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">No specific unverified claims identified for fact-checking.</p>
            )}
          </div>

        </div>
      </CardContent>
    </Card>
  );
};

export default EnhancedUnderstandingCard;
