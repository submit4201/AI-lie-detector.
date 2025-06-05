import React from 'react';
import { Card, CardContent } from "@/components/ui/card";

const ListItem = ({ item, icon = "🔹" }) => (
  <li className="text-gray-300 text-sm bg-black/20 p-2 rounded-md border border-white/10 flex items-start">
    <span className="mr-2 text-blue-400">{icon}</span>
    <span>{item}</span>
  </li>
);

const EnhancedUnderstandingCard = ({ understanding }) => {
  if (!understanding) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Enhanced understanding data not available.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const {
    key_inconsistencies = [],
    areas_of_evasiveness = [],
    suggested_follow_up_questions = [],
    unverified_claims = []
  } = understanding;

  return (
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0">
        <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 space-y-4">

          <div>
            <h4 className="text-md font-semibold text-red-300 mb-2">Key Inconsistencies</h4>
            {key_inconsistencies.length > 0 ? (
              <ul className="space-y-1">
                {key_inconsistencies.map((item, index) => <ListItem key={index} item={item} icon="⚠️"/>)}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">None detected.</p>
            )}
          </div>

          <div>
            <h4 className="text-md font-semibold text-yellow-300 mb-2">Areas of Evasiveness</h4>
            {areas_of_evasiveness.length > 0 ? (
              <ul className="space-y-1">
                {areas_of_evasiveness.map((item, index) => <ListItem key={index} item={item} icon="🤫"/>)}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">None detected.</p>
            )}
          </div>

          <div>
            <h4 className="text-md font-semibold text-green-300 mb-2">Suggested Follow-up Questions</h4>
            {suggested_follow_up_questions.length > 0 ? (
              <ul className="space-y-1">
                {suggested_follow_up_questions.map((item, index) => <ListItem key={index} item={item} icon="❓"/>)}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">None suggested.</p>
            )}
          </div>

          <div>
            <h4 className="text-md font-semibold text-purple-300 mb-2">Unverified Claims</h4>
            {unverified_claims.length > 0 ? (
              <ul className="space-y-1">
                {unverified_claims.map((item, index) => <ListItem key={index} item={item} icon="🧐"/>)}
              </ul>
            ) : (
              <p className="text-gray-400 text-sm">None identified.</p>
            )}
          </div>

        </div>
      </CardContent>
    </Card>
  );
};

export default EnhancedUnderstandingCard;
