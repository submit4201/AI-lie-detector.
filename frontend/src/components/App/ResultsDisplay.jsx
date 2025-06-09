import React from 'react';
import './ResultsDisplay.css'; // Import the CSS file for styling
// Import enhanced result section components
import KeyHighlightsSection from './results/KeyHighlightsSection';
import ComprehensiveAnalysisSection from './results/ComprehensiveAnalysisSection';
import SessionInsightsSection from './results/SessionInsightsSection';
import TabbedSecondarySection from './results/TabbedSecondarySection';
import DataDiagnosticPanel from './results/DataDiagnosticPanel';
import LoadingSpinner from './results/LoadingSpinner';
import ErrorDisplay from './results/ErrorDisplay';
import ErrorBoundary from './results/ErrorBoundary';
import ValidationStatus from './results/ValidationStatus';

// Helper component for displaying a score with a label
const ScoreDisplay = ({ label, score, unit = '%' }) => {
  let scoreText;
  if (typeof score === 'number' && !isNaN(score)) {
    if (unit === '%') {
      scoreText = `${score.toFixed(0)}${unit}`;
    } else if (unit && unit.trim() === 'WPM') {
      scoreText = `${score.toFixed(1)}${unit}`;
    } else {
      scoreText = `${score.toFixed(2)}${unit || ''}`;
    }
  } else {
    scoreText = 'N/A';
  }

  return (
    <div className="score-item">
      <span className="score-label">{label}:</span>
      <span className="score-value">{scoreText}</span>
    </div>
  );
};

// Helper component for list items
const ListItem = ({ item }) => <li className="list-item-detail">{item}</li>;

// Helper component for key-value pairs in summaries
const SummaryItem = ({ itemKey, value }) => (
  <p className="summary-item">
    <strong className="summary-item-key">{itemKey}:</strong> {typeof value === 'object' ? JSON.stringify(value) : value}
  </p>
);

const ResultsDisplay = ({ 
  analysisResults, 
  isLoading, 
  getCredibilityColor, 
  getCredibilityLabel, 
  sessionHistory, 
  sessionId, 
  error,
  isStreaming = false,
  streamingProgress = null,
  partialResults = null
}) => {
  console.log('=== ResultsDisplay Debug ===');
  console.log('analysisResults received:', analysisResults);
  console.log('typeof analysisResults:', typeof analysisResults);
  console.log('analysisResults === null:', analysisResults === null);
  console.log('isStreaming:', isStreaming);
  console.log('partialResults:', partialResults);
  console.log('analysisResults === undefined:', analysisResults === undefined);
  console.log('isLoading:', isLoading);
  console.log('error:', error);
  console.log('=== End Debug ===');

  if (error) {
    return (
      <div className="results-display-container">
        <ErrorDisplay 
          error={error}
          title="Analysis Error"
          description="There was an error processing your audio analysis."
          onRetry={() => window.location.reload()}
        />
      </div>
    );
  }
  if (isLoading) {
    return (
      <div className="results-display-container">
        <LoadingSpinner 
          size="lg" 
          message={streamingProgress || "Analyzing your audio... This may take a few moments."}
        />
        {isStreaming && (
          <div className="mt-4 bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
              <span className="text-blue-200 font-medium">Streaming Analysis Active</span>
            </div>
            {streamingProgress && (
              <p className="text-blue-300 text-sm mt-2">{streamingProgress}</p>
            )}
          </div>
        )}
      </div>
    );
  }

  // Show partial results during streaming
  if (isStreaming && partialResults && Object.keys(partialResults).length > 0) {
    return (
      <div className="results-display-container">
        <div className="mb-4 bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
            <span className="text-blue-200 font-medium">Streaming Results (Partial)</span>
          </div>
          {streamingProgress && (
            <p className="text-blue-300 text-sm mt-2">{streamingProgress}</p>
          )}
        </div>
        
        <ErrorBoundary>
          <div className="results-content">
            <KeyHighlightsSection analysisResults={partialResults} />
            {partialResults.comprehensive_analysis && (
              <ComprehensiveAnalysisSection analysisResults={partialResults} />
            )}
            {partialResults.secondary_analysis && (
              <TabbedSecondarySection analysisResults={partialResults} />
            )}
          </div>
        </ErrorBoundary>
      </div>
    );
  }
  if (!analysisResults) {
    console.log('⚠️ No analysisResults - returning placeholder');
    return (
      <div className="results-display-container">
        <div className="results-placeholder bg-gradient-to-br from-purple-600/20 via-blue-600/20 to-indigo-600/20 backdrop-blur-lg border border-white/20 rounded-lg p-8 text-center">
          <div className="text-6xl mb-4">🎤</div>
          <h3 className="text-2xl font-semibold text-white mb-4">Ready to Analyze</h3>
          <p className="text-gray-300 mb-6">Upload an audio file or start recording to begin your AI-powered lie detection analysis.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-400">
            <div className="bg-black/20 p-4 rounded-lg">
              <div className="text-2xl mb-2">📊</div>
              <div className="font-medium text-white">Credibility Scoring</div>
              <div>Advanced AI analysis of speech patterns</div>
            </div>
            <div className="bg-black/20 p-4 rounded-lg">
              <div className="text-2xl mb-2">🎯</div>
              <div className="font-medium text-white">Risk Assessment</div>
              <div>Comprehensive deception indicators</div>
            </div>
            <div className="bg-black/20 p-4 rounded-lg">
              <div className="text-2xl mb-2">💡</div>
              <div className="font-medium text-white">Actionable Insights</div>
              <div>Detailed recommendations and guidance</div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  // Debug log the structure
  console.log('📊 Analysis results structure:', {
    transcript: !!analysisResults.transcript,
    speaker_transcripts: !!analysisResults.speaker_transcripts,
    audio_analysis: !!analysisResults.audio_analysis,
    emotion_analysis: !!analysisResults.emotion_analysis,
    credibility_score: analysisResults.credibility_score,
    confidence_level: analysisResults.confidence_level
  });

  const {
    transcript,
    session_insights,
    audio_analysis = {}
  } = analysisResults;

  console.log('Audio analysis:', audio_analysis);

  // Calculate filler word frequency for ComprehensiveAnalysisSection
  let fillerWordFrequencyText = 'N/A';
  if (analysisResults.linguistic_analysis) {
    const { linguistic_analysis } = analysisResults;
    if (typeof linguistic_analysis.filler_word_frequency === 'number' && !isNaN(linguistic_analysis.filler_word_frequency)) {
      fillerWordFrequencyText = `${linguistic_analysis.filler_word_frequency.toFixed(2)} per 100 words`;
    } else if (typeof linguistic_analysis.filler_count === 'number' && !isNaN(linguistic_analysis.filler_count) &&
               typeof linguistic_analysis.word_count === 'number' && !isNaN(linguistic_analysis.word_count) &&
               linguistic_analysis.word_count > 0) {
      const calculatedFrequency = (linguistic_analysis.filler_count / linguistic_analysis.word_count) * 100;
      fillerWordFrequencyText = `${calculatedFrequency.toFixed(2)} per 100 words`;
    }
  }  return (
    <div className="results-display-container space-y-6 fade-in">
      {/* Data Diagnostics Panel - Remove in production */}
      <ErrorBoundary fallback="Error loading diagnostics">
        <DataDiagnosticPanel 
          result={analysisResults}
          sessionHistory={sessionHistory}
          sessionId={sessionId}
        />
      </ErrorBoundary>

      {/* Key Highlights Section - Enhanced Overview */}
      <ErrorBoundary fallback="Error loading highlights">
        <KeyHighlightsSection 
          result={analysisResults}
          getCredibilityColor={getCredibilityColor}
          getCredibilityLabel={getCredibilityLabel}
        />
      </ErrorBoundary>

      {/* Comprehensive Analysis Section - Detailed Analysis with Tabs */}
      <ErrorBoundary fallback="Error loading comprehensive analysis">
        <ComprehensiveAnalysisSection 
          result={analysisResults}
          fillerWordFrequencyText={fillerWordFrequencyText}
        />
      </ErrorBoundary>      {/* Session Insights Section - Only show if session data is available */}
      {session_insights && (
        <ErrorBoundary fallback="Error loading session insights">
          <SessionInsightsSection 
            sessionInsights={session_insights}
            sessionHistory={sessionHistory}
          />
        </ErrorBoundary>
      )}

      {/* Secondary Features Section - Tabbed interface for Session History and Export */}
      <ErrorBoundary fallback="Error loading secondary features">
        <TabbedSecondarySection 
          result={analysisResults}
          sessionHistory={sessionHistory}
          sessionId={sessionId}
          onSelectHistoryItem={(item) => {
            console.log('Selected history item:', item);
          }}
        />
      </ErrorBoundary>

      {/* Validation Status - Show analysis completeness and any issues */}
      <ErrorBoundary fallback="Error loading validation status">
        <ValidationStatus result={analysisResults} className="mt-4" />
      </ErrorBoundary>

      {/* Legacy sections maintained for any missing data (can be removed later if all data is covered above) */}
      {/* This ensures backward compatibility while we migrate to enhanced components */}
      
      {/* Only show legacy sections if specific data is missing from enhanced components */}
      {transcript && !analysisResults.speaker_transcripts && (
        <div className="results-section section-core">
          <h3>Full Transcript</h3>
          <div className="transcript-section">
            <p>{transcript}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;
