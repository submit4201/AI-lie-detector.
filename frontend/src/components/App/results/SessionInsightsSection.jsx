    { id: 'speech', label: 'Speech Patterns', icon: '🎵' },
    { id: 'psychology', label: 'Psychology', icon: '🧠' },
    { id: 'deception', label: 'Deception Indicators', icon: '🎯' },
    { id: 'session', label: 'Session Analysis', icon: '📈' }, // Tab for session-specific insights
  ];

  /**
   * Renders the content for the "Overview" tab.
   * Displays key metrics like Deception Risk, Confidence Level, Formality, and Emotional State,
   * along with progress bars for a visual summary.
   * @returns {JSX.Element} The JSX for the Overview tab content.
   */
  const renderOverviewTab = () => (
    // Container for the Overview tab content with spacing between elements.
    <div className="space-y-6">
      {/* Grid for displaying top-level MetricCards. Responsive columns. */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Deception Risk"
          // Heuristic: Deception risk might be inverse of credibility or a direct 'deception_probability' field.
          value={result.deception_probability?.toFixed(1) ?? (result.credibility_score !== undefined ? (100 - result.credibility_score) : 'N/A')}
          unit="%"
          description="Overall likelihood of deceptive behavior based on combined indicators."
          // Dynamic coloring based on risk level.
          color={result.deception_probability > 70 || (result.credibility_score !== undefined && (100 - result.credibility_score) > 70) ? "red"
                 : result.deception_probability > 40 || (result.credibility_score !== undefined && (100 - result.credibility_score) > 40) ? "yellow"
                 : "green"}
          comparison={ // Contextual comparison text based on risk.
            result.deception_probability > 70 || (result.credibility_score !== undefined && (100 - result.credibility_score) > 70) ? "High risk - significant indicators may be present."
            : result.deception_probability > 40 || (result.credibility_score !== undefined && (100 - result.credibility_score) > 40) ? "Moderate risk - some indicators warrant attention."
            : "Low risk - minimal deception indicators observed."
          }
        />

        <MetricCard
          title="Confidence Level (Linguistic)"
          value={(linguistic_analysis.confidence_ratio * 100).toFixed(1)} // confidence_ratio is 0-1, convert to percentage.
          unit="%"
          description="Speaker's language certainty vs. uncertainty."
          color="blue"
          comparison={
            linguistic_analysis.confidence_ratio > 0.7 ? "High confidence expressed in statements." :
            linguistic_analysis.confidence_ratio > 0.4 ? "Moderate confidence level expressed." :
            "Low confidence or high uncertainty in language."
          }
        />

        <MetricCard
          title="Speech Formality"
          value={linguistic_analysis.formality_score?.toFixed(1)}
          unit="/100" // Assuming formality_score is out of 100.
          description="Assessed language formality and professionalism."
          color="purple"
          comparison={
            linguistic_analysis.formality_score > 70 ? "Primarily formal/professional language." :
            linguistic_analysis.formality_score > 40 ? "Mix of formal and informal (semi-formal)." :
            "Predominantly casual/informal speech patterns."
          }
        />

        <MetricCard
          title="Primary Emotional State"
          // Display the label of the first (dominant) emotion, or "UNKNOWN".
          value={emotion_analysis && emotion_analysis.length > 0 ? emotion_analysis[0].label.toUpperCase() : "UNKNOWN"}
          description="Most prominent emotional state detected from voice/text."
          color="cyan"
          // Display the confidence score of the dominant emotion.
          comparison={emotion_analysis && emotion_analysis.length > 0 ? `Confidence: ${(emotion_analysis[0].score * 100).toFixed(1)}%` : "Emotion score N/A"}
        />
      </div>

      {/* Card for Visual Analysis Summary using ProgressBars. */}
      <Card className="bg-black/20 backdrop-blur-sm border border-white/20">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-white mb-4">📈 Key Metrics Visual Summary</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Column 1 of ProgressBars */}
            <div className="space-y-4">
              <ProgressBar
                value={linguistic_analysis.formality_score}
                color="purple"
                label="Language Formality"
              />
              <ProgressBar
                value={linguistic_analysis.complexity_score}
                color="indigo"
                label="Linguistic Complexity"
              />
              <ProgressBar
                value={(linguistic_analysis.confidence_ratio * 100)}
                color="blue"
                label="Linguistic Confidence Ratio"
              />
            </div>
            {/* Column 2 of ProgressBars */}
            <div className="space-y-4">
              {/* Heuristic for speech fluency: higher hesitation count implies lower fluency. */}
              <ProgressBar
                value={Math.max(0, 100 - (linguistic_analysis.hesitation_count * 5))} // Example: penalize 5 points per hesitation.
                color="teal"
                label="Speech Fluency (heuristic)"
              />
              <ProgressBar
                value={audio_quality?.quality_score || 0} // Use quality_score from audio_quality object.
                color="cyan"
                label="Audio Quality Score"
              />
              <ProgressBar
                // Truthfulness Score: can be credibility_score or inverse of deception_probability.
                value={result.credibility_score !== undefined ? result.credibility_score : (100 - (result.deception_probability || 0))}
                // Dynamic color based on the score.
                color={result.credibility_score > 70 || (result.deception_probability !== undefined && result.deception_probability <= 30) ? "green" :
                       result.credibility_score > 40 || (result.deception_probability !== undefined && result.deception_probability <= 60) ? "yellow" : "red"}
                label="Assessed Truthfulness Score"
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  /**
   * Renders the content for the "Speech Patterns" tab.
   * Displays metrics like speech rate, word count, sentence structure, and hesitation analysis.
   * @returns {JSX.Element} The JSX for the Speech Patterns tab content.
   */
  const renderSpeechTab = () => (
    <div className="space-y-6">
      {/* Card for Core Speech Metrics */}
      <Card className="bg-black/20 backdrop-blur-sm border border-blue-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-blue-300 mb-4">🎵 Core Speech Metrics</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <MetricCard
              title="Speech Rate"
              value={linguistic_analysis.speech_rate_wpm?.toFixed(0)}
              unit=" WPM"
              description="Words per minute (Typical range: 140-180 WPM)."
              color="blue"
              comparison={
                linguistic_analysis.speech_rate_wpm < 120 ? "Slow pace - may indicate hesitation or deliberation." :
                linguistic_analysis.speech_rate_wpm > 200 ? "Fast pace - may indicate nervousness or excitement." :
                "Normal speaking pace observed."
              }
            />

            <MetricCard
              title="Total Word Count"
              value={linguistic_analysis.word_count}
              description="Total number of words spoken in the analyzed segment."
              color="green"
            />

            <MetricCard
              title="Sentence Structure"
              value={linguistic_analysis.avg_words_per_sentence?.toFixed(1)}
              unit=" words/sentence"
              description="Average number of words per sentence."
              color="purple"
              comparison={
                linguistic_analysis.avg_words_per_sentence > 20 ? "Complex sentence structures used." :
                linguistic_analysis.avg_words_per_sentence < 10 ? "Simpler sentence structures preferred." : // Adjusted threshold
                "Moderately complex sentences."
              }
            />
          </div>
        </CardContent>
      </Card>

      {/* Card for Hesitation and Fluency Analysis */}
      <Card className="bg-black/20 backdrop-blur-sm border border-orange-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-orange-300 mb-4">🚧 Hesitation & Fluency Analysis</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="Hesitation Markers"
              value={linguistic_analysis.hesitation_count}
              description="Count of 'um', 'uh', 'like', 'you know', etc."
              color="red"
              comparison={
                linguistic_analysis.hesitation_count > 10 ? "High number of hesitation markers detected." :
                linguistic_analysis.hesitation_count > 5 ? "Moderate hesitation markers present." :
                "Speech appears relatively fluent."
              }
            />

            <MetricCard
              title="Filler Words (Strict)"
              value={linguistic_analysis.filler_count}
              description="Count of basic fillers: 'um', 'uh', 'er', 'ah'."
              color="yellow"
            />

            <MetricCard
              title="Word/Phrase Repetitions"
              value={linguistic_analysis.repetition_count}
              description="Count of immediately repeated words or short phrases."
              color="pink"
            />

            <MetricCard
              title="Hesitation Rate"
              value={linguistic_analysis.hesitation_rate_hpm?.toFixed(1)} // Corrected field name
              unit=" per minute"
              description="Frequency of hesitation markers per minute."
              color="orange"
              comparison={
                linguistic_analysis.hesitation_rate_hpm > 8 ? "Notably high hesitation frequency." :
                linguistic_analysis.hesitation_rate_hpm > 4 ? "Moderate hesitation frequency." :
                "Normal hesitation frequency."
              }
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  /**
   * Renders the content for the "Psychology" tab.
   * Displays analysis related to confidence, certainty, language sophistication, and emotional state.
   * @returns {JSX.Element} The JSX for the Psychology tab content.
   */
  const renderPsychologyTab = () => (
    <div className="space-y-6">
      {/* Card for Confidence and Certainty Analysis */}
      <Card className="bg-black/20 backdrop-blur-sm border border-green-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-green-300 mb-4">💡 Confidence & Certainty Levels</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <MetricCard
              title="Certainty Indicators"
              value={linguistic_analysis.certainty_count ?? 'N/A'}
              description="Words like 'definitely', 'absolutely', 'sure'."
              color="green"
              comparison={
                linguistic_analysis.certainty_count > 8 ? "Very confident language used." :
                linguistic_analysis.certainty_count > 4 ? "Moderately confident language." :
                "Few explicit confidence indicators."
              }
            />

            <MetricCard
              title="Uncertainty Qualifiers"
              value={linguistic_analysis.qualifier_count ?? 'N/A'}
              description="Words like 'maybe', 'perhaps', 'might'."
              color="yellow"
              comparison={
                linguistic_analysis.qualifier_count > 8 ? "High use of uncertain language." :
                linguistic_analysis.qualifier_count > 4 ? "Some use of uncertain language." :
                "Minimal use of uncertain language."
              }
            />

            <div className="bg-black/20 backdrop-blur-sm p-4 rounded-lg border border-blue-400/30">
              <div className="text-blue-300 font-medium text-sm mb-3">Linguistic Confidence Ratio</div>
              {/* Detailed breakdown of confidence vs. uncertainty counts. */}
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Certainty Word Count:</span>
                  <span className="text-green-300 font-semibold">{linguistic_analysis.certainty_count}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Qualifier Word Count:</span>
                  <span className="text-yellow-300 font-semibold">{linguistic_analysis.qualifier_count}</span>
                </div>
                <ProgressBar
                  value={linguistic_analysis.confidence_ratio * 100}
                  color="blue"
                  label="Overall Linguistic Confidence"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Card for Language Sophistication (Formality & Complexity) */}
      <Card className="bg-black/20 backdrop-blur-sm border border-purple-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-purple-300 mb-4">📚 Language Sophistication</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <ProgressBar
                value={linguistic_analysis.formality_score}
                color="purple"
                label="Formality Score"
              />
              <div className="text-xs text-gray-400 mt-2">
                {linguistic_analysis.formality_score > 70 ? "🎓 Language is predominantly formal and professional." :
                 linguistic_analysis.formality_score > 40 ? "💼 Language shows a mix of formal and informal elements." :
                 "💬 Language is mostly casual and informal."}
              </div>
            </div>

            <div className="space-y-4">
              <ProgressBar
                value={linguistic_analysis.complexity_score}
                color="indigo"
                label="Linguistic Complexity Score"
              />
              <div className="text-xs text-gray-400 mt-2">
                {linguistic_analysis.complexity_score > 70 ? "🔬 Highly sophisticated language and sentence structures." :
                 linguistic_analysis.complexity_score > 40 ? "📚 Moderately complex language used." :
                 "📝 Language structure is relatively simple."}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Card for Emotional State Analysis */}
      {emotion_analysis && Array.isArray(emotion_analysis) && emotion_analysis.length > 0 && (
        <Card className="bg-black/20 backdrop-blur-sm border border-cyan-400/30">
          <CardContent className="p-6">
            <h4 className="text-lg font-semibold text-cyan-300 mb-4">😊 Emotional Profile</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <MetricCard
                title="Dominant Emotion"
                value={emotion_analysis[0].label.toUpperCase()}
                description="Primary emotional state detected from the analysis."
                color="cyan"
                comparison={`Confidence: ${(emotion_analysis[0].score * 100).toFixed(1)}%`}
              />
              {/* Placeholder for emotional intensity if that data becomes available */}
              {emotion_analysis[0].intensity !== undefined ? ( // Check if intensity exists
                <MetricCard
                  title="Emotional Intensity"
                  value={(emotion_analysis[0].intensity * 100).toFixed(1)} // Assuming intensity is 0-1
                  unit="%"
                  description="Perceived strength of the dominant emotional expression."
                  color="pink"
                />
              ) : (
                 <MetricCard
                  title="Emotional Intensity"
                  value={"N/A"}
                  description="Strength of emotion not available."
                  color="pink"
                />
              )}
            </div>
            {/* Optional: Could list top few emotions if available beyond dominant one */}
            {emotion_analysis.length > 1 && (
              <div className="mt-4 pt-3 border-t border-cyan-400/30">
                <h5 className="text-sm font-semibold text-cyan-200 mb-2">Other Detected Emotions:</h5>
                <div className="flex flex-wrap gap-2">
                  {emotion_analysis.slice(1, 4).map((emo, idx) => ( // Show next 3
                    <span key={idx} className="text-xs bg-cyan-700/50 text-cyan-100 px-2 py-1 rounded-full">
                      {emo.label.toUpperCase()} ({(emo.score * 100).toFixed(0)}%)
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );

  /**
   * Renders the content for the "Deception Indicators" tab.
   * Focuses on overall deception risk and specific linguistic/behavioral cues related to deception.
   * @returns {JSX.Element} The JSX for the Deception Indicators tab content.
   */
  const renderDeceptionTab = () => (
    <div className="space-y-6">
      {/* Card for Overall Deception Risk Assessment */}
      <Card className="bg-black/20 backdrop-blur-sm border border-red-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-red-300 mb-4">🚨 Overall Deception Risk</h4>
          <div className="text-center mb-6">
            {/* Display Deception Probability / Risk Score */}
            <div className="text-6xl font-bold text-white mb-2">
              {/* Heuristic: Risk could be 100 - credibility_score or a direct `deception_probability` if available */}
              {(result.deception_probability?.toFixed(1) ?? (result.credibility_score !== undefined ? (100 - result.credibility_score) : "N/A"))}%
            </div>
            {/* Display Qualitative Risk Level */}
            <div className={`text-lg font-semibold ${
              result.deception_probability > 70 || (result.credibility_score !== undefined && result.credibility_score < 30) ? "text-red-300" :
              result.deception_probability > 40 || (result.credibility_score !== undefined && result.credibility_score < 60) ? "text-yellow-300" :
              "text-green-300"
            }`}>
              {result.deception_probability > 70 || (result.credibility_score !== undefined && result.credibility_score < 30) ? "🔴 HIGH RISK" :
               result.deception_probability > 40 || (result.credibility_score !== undefined && result.credibility_score < 60) ? "🟡 MODERATE RISK" :
               "🟢 LOW RISK"}
            </div>
          </div>
          {/* Progress Bar for Deception Risk */}
          <div className="w-full bg-black/30 rounded-full h-4 mb-4">
            <div
              className={`h-4 rounded-full transition-all duration-1000 ${
                result.deception_probability > 70 || (result.credibility_score !== undefined && result.credibility_score < 30) ? "bg-gradient-to-r from-red-600 to-red-400" :
                result.deception_probability > 40 || (result.credibility_score !== undefined && result.credibility_score < 60) ? "bg-gradient-to-r from-yellow-600 to-yellow-400" :
                "bg-gradient-to-r from-green-600 to-green-400"
              }`}
              style={{width: `${(result.deception_probability ?? (result.credibility_score !== undefined ? (100 - result.credibility_score) : 0))}%`}}
            ></div>
          </div>
          {/* Display Red Flags if available */}
          {result.red_flags_per_speaker && result.red_flags_per_speaker["Speaker 1"] && result.red_flags_per_speaker["Speaker 1"].length > 0 && (
            <div className="mt-4 pt-3 border-t border-red-400/30">
              <h5 className="text-sm font-semibold text-red-200 mb-2">Key Deception Indicators Observed:</h5>
              <ul className="list-disc list-inside space-y-1 text-red-100 text-xs">
                {result.red_flags_per_speaker["Speaker 1"].slice(0, 5).map((flag, idx) => <li key={idx}>{flag}</li>)} {/* Show top 5 */}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Card for Specific Deception-Related Behavioral Cues */}
      <Card className="bg-black/20 backdrop-blur-sm border border-orange-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-orange-300 mb-4">🎯 Behavioral Cues Related to Deception</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Stress & Nervousness Indicators */}
            <div className="space-y-3">
              <h5 className="text-sm font-semibold text-red-300">⚡ Stress & Nervousness Cues</h5>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Hesitation Frequency:</span>
                  <span className={`font-semibold ${
                    linguistic_analysis.hesitation_count > 10 ? "text-red-300" : // High
                    linguistic_analysis.hesitation_count > 5 ? "text-yellow-300" : // Moderate
                    "text-green-300" // Low
                  }`}>
                    {linguistic_analysis.hesitation_count > 10 ? "HIGH" :
                     linguistic_analysis.hesitation_count > 5 ? "MODERATE" :
                     "LOW"} ({linguistic_analysis.hesitation_count})
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Speech Rate Variance:</span>
                  <span className={`font-semibold ${ // Example logic: abnormal if too slow or too fast
                    linguistic_analysis.speech_rate_wpm < 120 || linguistic_analysis.speech_rate_wpm > 200 ? "text-yellow-300" : "text-green-300"
                  }`}>
                    {linguistic_analysis.speech_rate_wpm < 120 || linguistic_analysis.speech_rate_wpm > 200 ? "HIGH VARIANCE" : "NORMAL"}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Word/Phrase Repetitions:</span>
                  <span className={`font-semibold ${
                    linguistic_analysis.repetition_count > 5 ? "text-red-300" : // High
                    linguistic_analysis.repetition_count > 2 ? "text-yellow-300" : // Moderate
                    "text-green-300" // Low
                  }`}>
                    {linguistic_analysis.repetition_count > 5 ? "HIGH" :
                     linguistic_analysis.repetition_count > 2 ? "MODERATE" :
                     "LOW"} ({linguistic_analysis.repetition_count})
                  </span>
                </div>
              </div>
            </div>

            {/* Evasiveness & Confidence Indicators */}
            <div className="space-y-3">
              <h5 className="text-sm font-semibold text-blue-300">🛡️ Evasiveness & Confidence Cues</h5>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Linguistic Confidence:</span>
                  <span className={`font-semibold ${
                    linguistic_analysis.confidence_ratio > 0.7 ? "text-green-300" : // High confidence
                    linguistic_analysis.confidence_ratio > 0.4 ? "text-yellow-300" : // Moderate
                    "text-red-300" // Low
                  }`}>
                    {linguistic_analysis.confidence_ratio > 0.7 ? "HIGH" :
                     linguistic_analysis.confidence_ratio > 0.4 ? "MODERATE" :
                     "LOW"} ({(linguistic_analysis.confidence_ratio * 100).toFixed(0)}%)
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Use of Qualifiers (Uncertainty):</span>
                  <span className={`font-semibold ${
                    linguistic_analysis.qualifier_count > 8 ? "text-red-300" : // High
                    linguistic_analysis.qualifier_count > 4 ? "text-yellow-300" : // Moderate
                    "text-green-300" // Low
                  }`}>
                    {linguistic_analysis.qualifier_count > 8 ? "HIGH USAGE" :
                     linguistic_analysis.qualifier_count > 4 ? "MODERATE USAGE" :
                     "LOW USAGE"} ({linguistic_analysis.qualifier_count})
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Language Formality:</span>
                  {/* Formality might be relevant if inconsistent with context */}
                  <span className={`font-semibold ${
                    linguistic_analysis.formality_score > 70 ? "text-blue-300" :
                    linguistic_analysis.formality_score < 30 ? "text-yellow-300" : // Very informal might be a flag in some contexts
                    "text-gray-300"
                  }`}>
                    {linguistic_analysis.formality_score > 70 ? "FORMAL" :
                     linguistic_analysis.formality_score < 30 ? "VERY INFORMAL" :
                     "NEUTRAL"} ({(linguistic_analysis.formality_score).toFixed(0)}/100)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  /**
   * Renders the content for the "Session Analysis" tab.
   * Displays insights derived from the entire session history, if available.
   * @returns {JSX.Element} The JSX for the Session Analysis tab content.
   */
  const renderSessionTab = () => (
    <div className="space-y-6">
      {/* Display Session Insights if available from the result object */}
      {session_insights ? (
        <Card className="bg-black/20 backdrop-blur-sm border border-green-400/30">
          <CardContent className="p-6">
            <h4 className="text-lg font-semibold text-green-300 mb-4">📈 AI-Generated Session Insights</h4>
            <div className="space-y-4">
              {/* Display each type of session insight if available. */}
              {session_insights.consistency_analysis && (
                <div className="bg-white/5 p-4 rounded-lg border-l-4 border-green-400">
                  <span className="font-semibold text-green-300">🎯 Consistency Analysis:</span>
                  <p className="text-gray-200 mt-2 text-sm leading-relaxed whitespace-pre-wrap">
                    {session_insights.consistency_analysis}
                  </p>
                </div>
              )}

              {session_insights.behavioral_evolution && (
                <div className="bg-white/5 p-4 rounded-lg border-l-4 border-blue-400">
                  <span className="font-semibold text-blue-300">📊 Behavioral Evolution:</span>
                  <p className="text-gray-200 mt-2 text-sm leading-relaxed whitespace-pre-wrap">
                    {session_insights.behavioral_evolution}
                  </p>
                </div>
              )}

              {session_insights.risk_trajectory && (
                <div className="bg-white/5 p-4 rounded-lg border-l-4 border-yellow-400">
                  <span className="font-semibold text-yellow-300">⚠️ Risk Trajectory:</span>
                  <p className="text-gray-200 mt-2 text-sm leading-relaxed whitespace-pre-wrap">
                    {session_insights.risk_trajectory}
                  </p>
                </div>
              )}

              {session_insights.conversation_dynamics && (
                <div className="bg-white/5 p-4 rounded-lg border-l-4 border-purple-400">
                  <span className="font-semibold text-purple-300">💬 Conversation Dynamics:</span>
                  <p className="text-gray-200 mt-2 text-sm leading-relaxed whitespace-pre-wrap">
                    {session_insights.conversation_dynamics}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        // Fallback message if session_insights object is not available.
        <Card className="bg-black/20 backdrop-blur-sm border border-blue-400/30">
          <CardContent className="p-6">
            <h4 className="text-lg font-semibold text-blue-300 mb-4">📈 Session Analysis</h4>
            <div className="bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-lg p-4">
              <p className="text-blue-200 text-center">
                📊 Session-specific insights will become available after a few analysis segments within the same session.
                This is the first analysis, or session context is not yet processed.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Card for Current Analysis Summary within the session context */}
      <Card className="bg-black/20 backdrop-blur-sm border border-cyan-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-cyan-300 mb-4">📋 Current Segment Summary (Context for Session)</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <MetricCard
              title="Analysis Timestamp"
              // Display current time as this specific analysis's "timestamp".
              value={new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              description="Time this specific analysis segment was processed."
              color="cyan"
            />

            <MetricCard
              title="Audio Segment Duration"
              value={audio_quality?.duration?.toFixed(1)} // From audio_quality metrics
              unit=" sec"
              description="Length of the currently analyzed audio segment."
              color="blue"
            />

            <MetricCard
              title="Segment Word Density"
              // Calculate word density for the current segment.
              value={linguistic_analysis.speech_rate_wpm && audio_quality?.duration > 0 ?
                (linguistic_analysis.word_count / (audio_quality.duration / 60)).toFixed(1) : // Avoid division by zero
                "N/A"}
              unit=" words/min"
              description="Word density or effective speaking rate for this segment."
              color="green"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  /**
   * Determines which tab's content rendering function to call based on the `activeTab` state.
   * @returns {JSX.Element} The JSX content for the currently active tab.
   */
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverviewTab();
      case 'speech': return renderSpeechTab();
      case 'psychology': return renderPsychologyTab();
      case 'deception': return renderDeceptionTab();
      case 'session': return renderSessionTab();
      default: return renderOverviewTab(); // Default to overview tab.
    }
  };

  return (
    // Main container for the comprehensive analysis section.
    <div className="space-y-6">
      {/* Tab Navigation Buttons */}
      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-white mb-4">📊 Comprehensive Analysis Dashboard</h3>
          <div className="flex flex-wrap gap-2">
            {/* Map over the `tabs` array to create a TabButton for each. */}
            {tabs.map((tab) => (
              <TabButton
                key={tab.id}
                isActive={activeTab === tab.id} // Highlight if current tab is active.
                onClick={() => setActiveTab(tab.id)} // Set active tab on click.
                icon={tab.icon}
              >
                {tab.label}
              </TabButton>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Container for the content of the active tab. */}
      {/* min-h-[600px] ensures a minimum height for tab content area for consistent layout. */}
      <div className="min-h-[600px]">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default ComprehensiveAnalysisSection;
