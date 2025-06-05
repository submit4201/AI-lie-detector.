import React from 'react';
import { Card, CardContent } from "@/components/ui/card";

// Placeholder for individual card components, to be created or defined later if needed
const TranscriptCard = ({ transcript }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">📝 Transcript</h3>
      <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 max-h-60 overflow-y-auto">
        <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{transcript}</p>
      </div>
    </CardContent>
  </Card>
);

const EmotionAnalysisCard = ({ emotionAnalysis }) => {
  let emotions = emotionAnalysis;
  if (emotions && Array.isArray(emotions[0])) {
    emotions = emotions[0];
  }

  if (!emotions || !Array.isArray(emotions) || emotions.length === 0) {
    return (
      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-white mb-4">😊 Emotion Analysis</h3>
          <div className="bg-yellow-500/20 backdrop-blur-sm border border-yellow-400/30 rounded-lg p-4">
            <p className="text-yellow-200">No emotion analysis data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-white mb-4">😊 Emotion Analysis</h3>
        <div className="space-y-3">
          {emotions.slice(0, 5).map((emotion, index) => (
            <div key={index} className="flex justify-between items-center bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
              <span className="text-gray-200 capitalize font-medium">{emotion.label}</span>
              <div className="flex items-center gap-3">
                <div className="w-24 bg-white/20 rounded-full h-2">
                  <div
                    className="h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
                    style={{width: `${(emotion.score * 100).toFixed(1)}%`}}
                  ></div>
                </div>
                <span className="text-white font-semibold min-w-[50px]">{(emotion.score * 100).toFixed(1)}%</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

const DeceptionIndicatorsCard = ({ deceptionFlags }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">🚩 Deception Indicators</h3>
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
          <p className="text-green-200">✅ No significant deception indicators detected</p>
        </div>
      )}
    </CardContent>
  </Card>
);

const AdvancedAnalysisResultsCard = ({ advancedAnalysis }) => {
  if (!advancedAnalysis) return null;

  return (
    <>
      {/* Confidence Scores */}
      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-white mb-4">📊 Confidence Scores</h3>
          <div className="space-y-3">
            {Object.entries(advancedAnalysis.confidence_scores).map(([category, score], index) => (
              <div key={index} className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-200 capitalize font-medium">{category.replace('_', ' ')}</span>
                  <span className={`font-semibold ${score > 70 ? 'text-red-400' : score > 40 ? 'text-yellow-400' : 'text-green-400'}`}>
                    {score.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-white/20 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${score > 70 ? 'bg-red-500' : score > 40 ? 'bg-yellow-500' : 'bg-green-500'}`}
                    style={{width: `${score}%`}}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Risk Assessment */}
      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-white mb-4">⚡ Risk Assessment</h3>
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <div className="flex items-center justify-center">
              <span className={`text-2xl font-bold px-6 py-3 rounded-lg ${
                advancedAnalysis.overall_risk === 'high' ? 'bg-red-500/30 text-red-200' :
                advancedAnalysis.overall_risk === 'medium' ? 'bg-yellow-500/30 text-yellow-200' :
                'bg-green-500/30 text-green-200'
              }`}>
                {advancedAnalysis.overall_risk.toUpperCase()} RISK
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </>
  );
};

const AudioQualityCard = ({ audioQuality }) => {
  if (!audioQuality) return null;
  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-white mb-4">🎵 Audio Quality</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
            <span className="text-gray-300 text-sm">Duration</span>
            <p className="text-white font-semibold">{audioQuality.duration.toFixed(1)}s</p>
          </div>
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
            <span className="text-gray-300 text-sm">Quality Score</span>
            <p className={`font-semibold ${audioQuality.quality_score > 70 ? 'text-green-400' : audioQuality.quality_score > 40 ? 'text-yellow-400' : 'text-red-400'}`}>
              {audioQuality.quality_score}/100
            </p>
          </div>
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
            <span className="text-gray-300 text-sm">Sample Rate</span>
            <p className="text-white font-semibold">{audioQuality.sample_rate} Hz</p>
          </div>
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-3">
            <span className="text-gray-300 text-sm">Loudness</span>
            <p className="text-white font-semibold">{audioQuality.loudness.toFixed(1)} dBFS</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};


const BasicAnalysisSection = ({ result }) => {
  if (!result) return null;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white mb-4">📊 Basic Analysis</h2>

      {result.transcript && <TranscriptCard transcript={result.transcript} />}
      {result.emotion_analysis && <EmotionAnalysisCard emotionAnalysis={result.emotion_analysis} />}
      {result.deception_flags && <DeceptionIndicatorsCard deceptionFlags={result.deception_flags} />}
      {result.advanced_analysis && <AdvancedAnalysisResultsCard advancedAnalysis={result.advanced_analysis} />}
      {result.audio_quality && <AudioQualityCard audioQuality={result.audio_quality} />}
    </div>
  );
};

export default BasicAnalysisSection;
