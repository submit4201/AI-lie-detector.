import React from 'react';
import { Card, CardContent } from "@/components/ui/card"; // Shadcn/ui Card components
import { ResponsiveContainer, RadialBarChart, RadialBar, PolarAngleAxis, Text } from 'recharts'; // Charting library

/**
 * @component MetricCard
 * @description A reusable card component to display a single quantitative metric.
 * It shows a title, value, unit, description, and optional comparison text.
 * Color theming is supported.
 * @param {object} props - Component props.
 * @param {string} props.title - The title of the metric.
 * @param {string|number|null|undefined} props.value - The value of the metric.
 * @param {string} [props.unit] - Optional unit for the metric value (e.g., " WPM", "%").
 * @param {string} props.description - A brief explanation of the metric.
 * @param {string} [props.color="blue"] - Base color theme for styling (e.g., "blue", "green").
 * @param {string} [props.comparison] - Optional text providing comparative context or interpretation.
 */
const MetricCard = ({ title, value, unit, description, color = "blue", comparison }) => (
  // Main container for the metric card with dynamic border color.
  <div className={`bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-${color}-400/30`}>
    <div className="flex justify-between items-center mb-1">
      {/* Metric title with dynamic text color. */}
      <span className={`text-${color}-300 font-medium text-sm`}>{title}</span>
      {/* Metric value and unit, or "N/A" if value is not provided. */}
      <span className={`text-${color}-200 font-bold`}>
        {value !== null && value !== undefined ? `${value}${unit || ''}` : 'N/A'}
      </span>
    </div>
    {/* Optional comparison text. */}
    {comparison && (
      <div className="text-xs text-gray-400 mb-1">{comparison}</div>
    )}
    {/* Metric description. */}
    <div className="text-xs text-gray-400">{description}</div>
  </div>
);

/**
 * @component SpeechPatternsCard
 * @description Displays a card with various metrics related to speech patterns,
 * such as speech rate, word count, sentence count, average words per sentence,
 * average word length, and audio duration.
 * @param {object} props - Component props.
 * @param {object} props.linguisticAnalysis - Object containing linguistic analysis data.
 * @param {object} props.audioQuality - Object containing audio quality metrics, including duration.
 * @returns {JSX.Element|null} The SpeechPatternsCard UI, or null if no linguisticAnalysis data.
 */
const SpeechPatternsCard = ({ linguisticAnalysis, audioQuality }) => {
  if (!linguisticAnalysis) return null; // Don't render if data is missing.

  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-white mb-4">🎵 Speech Pattern Analysis</h3>
        {/* Grid layout for speech pattern metrics. */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          
          <MetricCard
            title="Speech Rate"
            value={linguisticAnalysis.speech_rate_wpm?.toFixed(0)} // Ensure value is handled if potentially undefined
            unit=" WPM"
            description="Words per minute - normal range is 140-180 WPM"
            color="blue"
            comparison={linguisticAnalysis.speech_rate_wpm && 
              (linguisticAnalysis.speech_rate_wpm < 120 ? "Slow pace may indicate hesitation" :
               linguisticAnalysis.speech_rate_wpm > 200 ? "Fast pace may indicate nervousness" :
               "Normal speaking pace")}
          />

          <MetricCard
            title="Word Count"
            value={linguisticAnalysis.word_count}
            description="Total words spoken in the analysis"
            color="green"
          />

          <MetricCard
            title="Sentence Count"
            value={linguisticAnalysis.sentence_count}
            description="Number of complete sentences identified"
            color="purple"
          />

          <MetricCard
            title="Avg Words/Sentence"
            value={linguisticAnalysis.avg_words_per_sentence?.toFixed(1)}
            description="Average sentence length - longer may indicate complexity"
            color="indigo"
            comparison={linguisticAnalysis.avg_words_per_sentence && 
              (linguisticAnalysis.avg_words_per_sentence > 20 ? "Complex sentence structure" :
               linguisticAnalysis.avg_words_per_sentence < 8 ? "Simple sentence structure" : // Corrected comparison for simple
               "Moderate sentence structure")}
          />

          <MetricCard
            title="Avg Word Length"
            value={linguisticAnalysis.avg_word_length?.toFixed(1)}
            unit=" chars"
            description="Average word length indicates vocabulary complexity"
            color="cyan"
            comparison={linguisticAnalysis.avg_word_length && 
              (linguisticAnalysis.avg_word_length > 5.5 ? "Complex vocabulary" :
               linguisticAnalysis.avg_word_length < 4.5 ? "Simple vocabulary" : // Corrected comparison for simple
               "Moderate vocabulary")}
          />

          <MetricCard
            title="Audio Duration"
            value={audioQuality?.duration?.toFixed(1)}
            unit=" sec"
            description="Total audio length analyzed"
            color="gray" // Using a neutral color for duration
          />
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * @component HesitationAnalysisCard
 * @description Displays metrics related to hesitations, filler words, and repetitions in speech.
 * @param {object} props - Component props.
 * @param {object} props.linguisticAnalysis - Object containing linguistic analysis data.
 * @returns {JSX.Element|null} The HesitationAnalysisCard UI, or null if no linguisticAnalysis data.
 */
const HesitationAnalysisCard = ({ linguisticAnalysis }) => {
  if (!linguisticAnalysis) return null; // Don't render if data is missing.

  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-white mb-4">⚡ Hesitation & Uncertainty Analysis</h3>
        {/* Grid layout for hesitation and uncertainty metrics. */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <MetricCard
            title="Hesitation Count"
            value={linguisticAnalysis.hesitation_count}
            description="Markers like 'um', 'uh', 'er', 'ah', 'like', 'you know'"
            color="red"
            comparison={linguisticAnalysis.hesitation_count > 10 ? "High hesitation level" :
                       linguisticAnalysis.hesitation_count > 5 ? "Moderate hesitation level" :
                       "Low hesitation level"}
          />

          <MetricCard
            title="Hesitation Rate"
            value={linguisticAnalysis.hesitation_rate_hpm?.toFixed(1)} // Corrected: hesitation_rate -> hesitation_rate_hpm
            unit="/min"
            description="Hesitation markers per minute of speech"
            color="orange"
            comparison={linguisticAnalysis.hesitation_rate_hpm && // Corrected
              (linguistic_analysis.hesitation_rate_hpm > 8 ? "High frequency of hesitations" :
               linguistic_analysis.hesitation_rate_hpm > 4 ? "Moderate frequency of hesitations" :
               "Normal hesitation frequency")}
          />

          <MetricCard
            title="Filler Words (Strict)"
            value={linguisticAnalysis.filler_count}
            description="Specific fillers: 'um', 'uh', 'er', 'ah' only"
            color="yellow"
            comparison={linguisticAnalysis.filler_count > 8 ? "Excessive use of filler words" :
                       linguisticAnalysis.filler_count > 4 ? "Some use of filler words" :
                       "Few filler words used"}
          />

          <MetricCard
            title="Repetitions"
            value={linguisticAnalysis.repetition_count}
            description="Count of repeated words or short phrases"
            color="pink"
            comparison={linguisticAnalysis.repetition_count > 5 ? "High number of repetitions" :
                       linguisticAnalysis.repetition_count > 2 ? "Some repetitions noted" :
                       "Low number of repetitions"}
          />
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * @component ConfidenceAnalysisCard
 * @description Displays metrics related to linguistic confidence, including certainty and
 * uncertainty indicators, and an overall confidence ratio.
 * @param {object} props - Component props.
 * @param {object} props.linguisticAnalysis - Object containing linguistic analysis data.
 * @returns {JSX.Element|null} The ConfidenceAnalysisCard UI, or null if no linguisticAnalysis data.
 */
const ConfidenceAnalysisCard = ({ linguisticAnalysis }) => {
  if (!linguisticAnalysis) return null; // Don't render if data is missing.

  // Calculate confidence percentage from the ratio.
  const confidencePercentage = (linguisticAnalysis.confidence_ratio * 100).toFixed(1);

  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-white mb-4">🎯 Linguistic Confidence & Certainty</h3>
        {/* Grid layout for confidence-related metrics. */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <MetricCard
            title="Certainty Indicators"
            value={linguisticAnalysis.certainty_count}
            description="Words like 'definitely', 'absolutely', 'sure'"
            color="green"
            comparison={linguisticAnalysis.certainty_count > 8 ? "Very confident language" :
                       linguisticAnalysis.certainty_count > 4 ? "Moderately confident language" :
                       "Few explicit confidence markers"}
          />

          <MetricCard
            title="Uncertainty Qualifiers"
            value={linguisticAnalysis.qualifier_count}
            description="Words like 'maybe', 'perhaps', 'might'"
            color="yellow"
            comparison={linguisticAnalysis.qualifier_count > 8 ? "High use of uncertain terms" :
                       linguisticAnalysis.qualifier_count > 4 ? "Some use of uncertain terms" :
                       "Minimal use of uncertain terms"}
          />

          <MetricCard
            title="Overall Confidence Ratio"
            value={confidencePercentage}
            unit="%"
            description="Ratio of certainty to total certainty/qualifier words"
            color="blue"
            comparison={linguisticAnalysis.confidence_ratio > 0.7 ? "High linguistic confidence overall" :
                       linguisticAnalysis.confidence_ratio > 0.4 ? "Balanced linguistic confidence" :
                       "Low linguistic confidence / high qualification"}
          />

          {/* Detailed breakdown of certainty vs. uncertainty counts with a progress bar visual. */}
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
            <div className="text-blue-300 font-medium text-sm mb-2">Confidence Score Breakdown</div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Certainty Indicators:</span>
                <span className="text-green-300 font-semibold">{linguistic_analysis.certainty_count}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Uncertainty Qualifiers:</span>
                <span className="text-yellow-300 font-semibold">{linguistic_analysis.qualifier_count}</span>
              </div>
              {/* Visual representation of the confidence ratio. */}
              <div className="w-full bg-white/20 rounded-full h-2 mt-2">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-blue-600 via-sky-500 to-teal-400" // Example gradient
                  style={{width: `${confidencePercentage}%`}}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * @component ScoreChart
 * @description Renders a semi-circular radial bar chart to display a score (0-100).
 * @param {object} props - Component props.
 * @param {number} props.score - The score to display (0-100).
 * @param {string} props.name - Name of the score (used for dataKey, not directly visible).
 * @param {string} props.color - Fill color for the radial bar.
 * @param {string} props.textColor - Fill color for the text label in the chart.
 * @param {string} [props.unit="/100"] - Unit to display next to the score.
 */
const ScoreChart = ({ score, name, color, textColor, unit = "/100" }) => {
  // Prepare data for Recharts. RadialBarChart expects an array.
  const chartData = [{ name: name, value: score || 0, fill: color }];
  const percentage = score || 0; // Ensure score is not null/undefined for display.

  return (
    // Responsive container for the chart. Height must be explicitly set for Recharts.
    <div style={{ width: '100%', height: 150 }}>
      <ResponsiveContainer>
        <RadialBarChart
          cx="50%" // Center X
          cy="70%" // Center Y, adjusted to make the semi-circle base align better
          innerRadius="60%" // Size of the inner hole
          outerRadius="100%" // Size of the outer bar
          barSize={12} // Thickness of the bar
          data={chartData}
          startAngle={180} // Start angle for semi-circle (left)
          endAngle={0}    // End angle for semi-circle (right)
        >
          {/* Defines the numerical scale of the chart. */}
          <PolarAngleAxis
            type="number"
            domain={[0, 100]} // Assuming scores are 0-100
            angleAxisId={0}
            tick={false} // Hide ticks on the axis
          />
          {/* The actual bar representing the score. */}
          <RadialBar
            background={{ fill: '#333' }} // Background track for the bar
            dataKey="value" // Key in `chartData` to use for bar value
            cornerRadius={6} // Rounded corners for the bar
            angleAxisId={0} // Associate with the defined PolarAngleAxis
          />
          {/* Custom text label to display the score in the center of the chart. */}
          <Text
            x="50%"
            y="70%" // Vertical position of the text, aligned with cy
            textAnchor="middle" // Horizontal alignment
            dominantBaseline="middle" // Vertical alignment
            className="fill-current font-bold text-xl" // Tailwind classes for styling
            style={{ fill: textColor }} // Dynamic text color from props
          >
            {`${percentage.toFixed(1)}${unit}`}
          </Text>
        </RadialBarChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * @component ComplexityAnalysisCard
 * @description Displays language complexity analysis, including formality and overall complexity scores,
 * visualized using ScoreChart components.
 * @param {object} props - Component props.
 * @param {object} props.linguisticAnalysis - Object containing linguistic analysis data.
 * @returns {JSX.Element|null} The ComplexityAnalysisCard UI, or null if no linguisticAnalysis data.
 */
const ComplexityAnalysisCard = ({ linguisticAnalysis }) => {
  if (!linguisticAnalysis) return null; // Don't render if data is missing.

  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-white mb-4">🧠 Language Complexity & Formality</h3>
        {/* Grid layout for formality and complexity charts. */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Formality Score Chart and Description */}
          <div className="bg-black/20 backdrop-blur-sm p-4 rounded-lg border border-purple-400/30 flex flex-col items-center">
            <span className="text-purple-300 font-medium text-center mb-2">Formality Score</span>
            <ScoreChart
              score={linguisticAnalysis.formality_score}
              name="Formality"
              color="#a855f7" // Tailwind purple-500
              textColor="#c084fc" // Tailwind purple-400
            />
            {/* Qualitative description based on formality score. */}
            <div className="text-xs text-gray-400 text-center mt-2">
              {linguisticAnalysis.formality_score > 70 ? "Primarily formal and professional language." :
               linguisticAnalysis.formality_score > 40 ? "Mix of formal and informal language (semi-formal)." :
               "Predominantly casual and informal language."}
            </div>
            <div className="text-xs text-gray-400 mt-1 text-center">
              (Based on formal terms, politeness, professional jargon)
            </div>
          </div>

          {/* Complexity Score Chart and Description */}
          <div className="bg-black/20 backdrop-blur-sm p-4 rounded-lg border border-indigo-400/30 flex flex-col items-center">
            <span className="text-indigo-300 font-medium text-center mb-2">Overall Linguistic Complexity Score</span>
            <ScoreChart
              score={linguisticAnalysis.complexity_score}
              name="Complexity"
              color="#6366f1" // Tailwind indigo-500
              textColor="#818cf8" // Tailwind indigo-400
            />
            {/* Qualitative description based on complexity score. */}
            <div className="text-xs text-gray-400 text-center mt-2">
              {linguisticAnalysis.complexity_score > 70 ? "Highly sophisticated linguistic structure." :
               linguisticAnalysis.complexity_score > 40 ? "Moderately complex language and structure." :
               "Relatively simple language structure."}
            </div>
            <div className="text-xs text-gray-400 mt-1 text-center">
              (Based on vocabulary, sentence structure, word variety)
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * @component QuantitativeMetricsSection
 * @description This component serves as a container to display various cards
 * related to quantitative linguistic analysis, such as speech patterns,
 * hesitation, confidence, and language complexity.
 *
 * @param {object} props - The properties passed to the component.
 * @param {object} props.result - The main analysis result object, expected to contain
 *                                `linguistic_analysis` and `audio_quality` data.
 * @returns {JSX.Element} The QuantitativeMetricsSection UI, or a fallback message if data is unavailable.
 */
const QuantitativeMetricsSection = ({ result }) => {
  // Fallback UI if essential linguistic analysis data is missing.
  if (!result || !result.linguistic_analysis) {
    return (
      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-white mb-4">📊 Quantitative Linguistic Analysis</h3>
          <div className="bg-yellow-500/20 backdrop-blur-sm border border-yellow-400/30 rounded-lg p-4">
            <p className="text-yellow-200 text-center">📊 Quantitative metrics are not available. Ensure that linguistic analysis was successfully performed.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Render the different analysis cards.
  return (
    <div className="space-y-6">
      {/* Card displaying speech pattern metrics. */}
      <SpeechPatternsCard 
        linguisticAnalysis={result.linguistic_analysis} 
        audioQuality={result.audio_quality} // Pass audio_quality for metrics like duration
      />
      
      {/* Card displaying hesitation and uncertainty metrics. */}
      <HesitationAnalysisCard linguisticAnalysis={result.linguistic_analysis} />
      
      {/* Card displaying confidence and certainty metrics. */}
      <ConfidenceAnalysisCard linguisticAnalysis={result.linguistic_analysis} />
      
      {/* Card displaying language complexity and formality scores. */}
      <ComplexityAnalysisCard linguisticAnalysis={result.linguistic_analysis} />
    </div>
  );
};

export default QuantitativeMetricsSection;
