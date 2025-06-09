# Session Insights Service
# Provides intelligent session analysis based on conversation history and patterns

from typing import Dict, List, Any, Optional
import statistics
# from datetime import datetime # Datetime not currently used, can be removed or kept for future use

class SessionInsightsGenerator:
    """
    Generates intelligent insights about a conversation session by analyzing its history,
    current analysis data, and overall context.

    This class provides methods to assess consistency in credibility and emotion,
    track behavioral evolution (e.g., formality, stress indicators), analyze risk
    trajectory, and understand conversation dynamics like pace and engagement.

    The insights are derived by comparing current analysis metrics with historical data
    from the session, looking for trends, variances, and significant changes.
    """
    def __init__(self):
        """
        Initializes the SessionInsightsGenerator.
        Currently, no specific initialization parameters are required.
        """
        pass # No specific initialization needed yet
    
    def generate_session_insights(self, 
                                  session_context: Dict[str, Any], 
                                  current_analysis: Dict[str, Any], 
                                  session_history: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generates a dictionary of intelligent session insights based on the provided
        conversation history, current analysis, and overall session context.

        If this is the first analysis in the session, no insights are generated.
        Otherwise, it calls various private methods to analyze different aspects
        of the session (consistency, behavior, risk, dynamics).

        Args:
            session_context: A dictionary containing metadata about the session,
                             such as 'previous_analyses' count and 'session_duration'.
            current_analysis: A dictionary containing the results of the latest
                              analysis segment (e.g., credibility score, emotion).
            session_history: A list of dictionaries, where each dictionary represents
                             a past analysis segment in the current session.

        Returns:
            A dictionary where keys are insight categories (e.g., "consistency_analysis")
            and values are human-readable string descriptions of the insights.
            Returns an empty dictionary if it's the first analysis.
        """
        
        # If it's the first analysis (no previous analyses), no session insights can be generated yet.
        if session_context.get("previous_analyses", 0) == 0:
            return {}  # No insights for the very first analysis segment
            
        insights: Dict[str, str] = {} # Initialize dictionary to store generated insights
        
        # Call helper methods to generate specific categories of insights.
        # Each method returns a string summarizing its findings for that category.
        insights["consistency_analysis"] = self._analyze_consistency(session_context, current_analysis, session_history)
        insights["behavioral_evolution"] = self._analyze_behavioral_evolution(session_context, current_analysis, session_history)
        insights["risk_trajectory"] = self._analyze_risk_trajectory(session_context, current_analysis, session_history)
        insights["conversation_dynamics"] = self._analyze_conversation_dynamics(session_context, current_analysis, session_history)
        
        return insights
    
    def _analyze_consistency(self, session_context: Dict, current_analysis: Dict, session_history: List[Dict]) -> str:
        """
        Analyzes consistency patterns across the session, focusing on credibility scores
        and emotional states.

        It calculates variance and trend of credibility scores and assesses the
        variability of expressed emotions throughout the session.

        Args:
            session_context: Context of the current session. (Not directly used here but passed for signature consistency)
            current_analysis: The latest analysis data.
            session_history: List of past analyses in the session.

        Returns:
            A string describing the consistency patterns observed.
        """
        
        # Extract credibility scores from the session history
        credibility_scores: List[float] = []
        for entry in session_history:
            score = entry.get("analysis", {}).get("credibility_score")
            if score is not None: # Ensure score exists
                credibility_scores.append(float(score))
        
        # Add current analysis's credibility score to the list
        current_score_val = current_analysis.get("credibility_score")
        if current_score_val is not None:
            credibility_scores.append(float(current_score_val))
        
        # If fewer than 2 data points, it's too early to analyze consistency robustly.
        if len(credibility_scores) < 2:
            return "Initial analysis phase - consistency patterns will become clearer as the conversation develops."
        
        # Calculate statistical metrics for credibility scores
        score_variance = statistics.variance(credibility_scores) if len(credibility_scores) > 1 else 0.0
        avg_score = statistics.mean(credibility_scores)
        score_trend_slope = self._calculate_trend(credibility_scores) # Calculate linear trend
        
        # Analyze emotional consistency by looking at the variety of top emotions expressed.
        emotions_expressed: List[str] = []
        for entry in session_history:
            # Assuming 'emotion_analysis' is a list and the first item is the top emotion.
            emotion_data = entry.get("analysis", {}).get("emotion_analysis")
            if emotion_data and isinstance(emotion_data, list) and len(emotion_data) > 0:
                top_emotion = emotion_data[0].get("label")
                if top_emotion:
                    emotions_expressed.append(top_emotion)

        current_emotion_data = current_analysis.get("emotion_analysis")
        if current_emotion_data and isinstance(current_emotion_data, list) and len(current_emotion_data) > 0:
            current_top_emotion = current_emotion_data[0].get("label")
            if current_top_emotion:
                emotions_expressed.append(current_top_emotion)

        unique_emotions_count = len(set(emotions_expressed)) if emotions_expressed else 0

        # --- Generate insight string based on calculated patterns ---
        base_analysis_str = ""
        # Describe consistency level based on variance of credibility scores
        if score_variance < 100:  # Low variance -> high consistency
            consistency_level_str = "HIGH"
            if avg_score > 70:
                base_analysis_str = f"The speaker demonstrates {consistency_level_str} consistency, maintaining a stable and high credibility (average: {avg_score:.1f}/100). "
            elif avg_score > 40:
                base_analysis_str = f"The speaker shows {consistency_level_str} consistency within a moderate credibility range (average: {avg_score:.1f}/100). "
            else:
                base_analysis_str = f"The speaker maintains {consistency_level_str} consistency, though in a lower credibility range (average: {avg_score:.1f}/100). "
        elif score_variance < 400:  # Medium variance -> moderate consistency
            consistency_level_str = "MODERATE"
            base_analysis_str = f"The speaker shows {consistency_level_str} consistency, with some fluctuation in credibility scores (variance: {score_variance:.1f}). "
        else:  # High variance -> low consistency
            consistency_level_str = "LOW"
            base_analysis_str = f"The speaker exhibits {consistency_level_str} consistency, with significant swings in credibility scores (variance: {score_variance:.1f}). "

        # Add credibility trend analysis to the insight
        trend_analysis_str = ""
        if score_trend_slope > 0.2: # Threshold for a noticeable positive trend (slope interpretation depends on scale)
            trend_analysis_str = "There is an improving trend in credibility over the conversation. "
        elif score_trend_slope < -0.2: # Threshold for a noticeable negative trend
            trend_analysis_str = "A declining trend in credibility is observed throughout the session. "
        else:
            trend_analysis_str = "Credibility levels have remained relatively stable across statements. "

        # Add emotional consistency analysis to the insight
        emotion_analysis_str = ""
        if unique_emotions_count == 0:
            emotion_analysis_str = "Emotional state data is insufficient for a consistency analysis at this time. "
        elif unique_emotions_count <= 2: # Very few unique emotions -> high emotional consistency
            top_emotions_sample = list(set(emotions_expressed))[:2] # Get up to 2 unique emotions
            emotion_analysis_str = f"Emotional expression is highly consistent, primarily centered around ({', '.join(top_emotions_sample)}). "
        elif unique_emotions_count <= 4: # Moderate emotional variation
            emotion_analysis_str = f"There is moderate emotional variation, with {unique_emotions_count} distinct primary emotional states observed. "
        else: # High emotional variation
            emotion_analysis_str = f"A high degree of emotional variability is displayed, with {unique_emotions_count} different primary emotional states detected. "

        return base_analysis_str + trend_analysis_str + emotion_analysis_str
    
    def _analyze_behavioral_evolution(self, session_context: Dict, current_analysis: Dict, session_history: List[Dict]) -> str:
        """
        Analyzes how behavioral patterns (e.g., formality, stress indicators like
        hesitation, speech pace) have evolved over the course of the session.

        It considers the session duration and current linguistic metrics to provide
        a qualitative description of behavioral trends.
        (Note: Currently, it relies more on current state than deep historical trend for some metrics without explicit storage of all historical linguistic details).

        Args:
            session_context: Context of the current session (duration, number of analyses).
            current_analysis: The latest analysis data.
            session_history: List of past analyses in the session. (Currently underutilized for detailed trend without more data storage)

        Returns:
            A string describing the observed behavioral evolution.
        """
        
        # If there's no history, it's hard to analyze evolution.
        if not session_history: # len(session_history) < 1
            return "Behavioral patterns will become more apparent as the conversation progresses and more data is collected."

        # Extract current linguistic metrics for behavior assessment
        current_linguistic_metrics = current_analysis.get("linguistic_analysis", {})
        current_speech_rate_wpm = current_linguistic_metrics.get("speech_rate_wpm") # This can be None
        current_hesitation_count = current_linguistic_metrics.get("hesitation_count", 0)
        current_formality_score = current_linguistic_metrics.get("formality_score", 0.0) # Ensure float for comparison

        # Session context
        session_duration_minutes = session_context.get("session_duration", 0.0) # Assuming duration in minutes
        num_analyses_so_far = session_context.get("previous_analyses", 0) + 1

        # --- Generate insight string based on session context and current metrics ---
        duration_impact_statement = ""
        if session_duration_minutes < 5.0:
            duration_impact_statement = "In this brief interaction, "
        elif session_duration_minutes < 15.0:
            duration_impact_statement = "Over this moderate-length conversation, "
        else: # Long session
            duration_impact_statement = "Throughout this extended conversation, "

        # Describe formality level based on current score
        formality_description = ""
        if current_formality_score > 60.0:
            formality_description = "the speaker consistently maintains formal communication patterns"
        elif current_formality_score > 30.0:
            formality_description = "the speaker uses moderately formal language"
        else:
            formality_description = "the speaker employs a more casual communication style"

        # Describe stress/comfort based on current hesitation count (as a proxy)
        # More sophisticated analysis would compare to baseline or historical trend.
        comfort_level_description = ""
        if current_hesitation_count > 8: # High hesitation
            comfort_level_description = "showing increased verbal hesitation, which may suggest heightened stress, cognitive load, or uncertainty"
        elif current_hesitation_count > 3: # Moderate hesitation
            comfort_level_description = "displaying moderate hesitation patterns, often typical of thoughtful or considered responses"
        else: # Low hesitation
            comfort_level_description = "demonstrating fluid speech patterns, potentially indicating comfort and ease with the topic"

        # Describe speech pace, if available
        speech_pace_description = ""
        if current_speech_rate_wpm is not None:
            if current_speech_rate_wpm > 170: # Fast pace
                speech_pace_description = f" Speaking at a rapid pace of {current_speech_rate_wpm:.0f} WPM could indicate heightened engagement, nervousness, or an attempt to assert control."
            elif current_speech_rate_wpm < 110: # Slow pace
                speech_pace_description = f" Speaking at a slower pace of {current_speech_rate_wpm:.0f} WPM may suggest deliberate communication, careful articulation, or potential reluctance."
            else: # Normal pace
                speech_pace_description = f" The speaker maintains a normal speech pace around {current_speech_rate_wpm:.0f} WPM."
        else:
            speech_pace_description = " Speech pace data is currently unavailable for a more detailed behavioral assessment."
        
        # Comment on the evolution status based on the number of analyses
        evolution_status = 'initial' if num_analyses_so_far <= 2 else 'evolving'
        
        return (f"{duration_impact_statement}{formality_description}, while {comfort_level_description}.{speech_pace_description} "
                f"Analysis #{num_analyses_so_far} reflects {evolution_status} behavioral patterns observed during the session.")
    
    def _analyze_risk_trajectory(self, session_context: Dict, current_analysis: Dict, session_history: List[Dict]) -> str:
        """
        Analyzes the progression of risk levels and deception indicators throughout the session.

        It converts categorical risk levels (low, medium, high) to numerical values
        to calculate a trend and describes the trajectory of both overall risk and
        the count of deception flags.

        Args:
            session_context: Context of the current session. (Not directly used here but passed for signature consistency)
            current_analysis: The latest analysis data.
            session_history: List of past analyses in the session.

        Returns:
            A string describing the risk trajectory and trends in deception indicators.
        """
        
        # Extract historical risk levels and deception flag counts
        historical_risk_levels_str: List[str] = []
        historical_deception_flags_counts: List[int] = []
        
        for entry in session_history:
            analysis_data = entry.get("analysis", {})
            risk_assessment_data = analysis_data.get("risk_assessment", {})
            risk_level_str = risk_assessment_data.get("overall_risk")

            # Count deception flags (assuming structure: red_flags_per_speaker: {"Speaker 1": [...]})
            speaker_flags = analysis_data.get("red_flags_per_speaker", {}).get("Speaker 1", [])
            flags_count = len(speaker_flags)

            if risk_level_str: # Only include if risk level is present
                historical_risk_levels_str.append(risk_level_str)
            historical_deception_flags_counts.append(flags_count)

        # Add current analysis data to the lists
        current_risk_assessment = current_analysis.get("risk_assessment", {})
        current_risk_level_str = current_risk_assessment.get("overall_risk", "unknown")
        current_speaker_flags = current_analysis.get("red_flags_per_speaker", {}).get("Speaker 1", [])
        current_flags_count = len(current_speaker_flags)

        all_risk_levels_str_combined = historical_risk_levels_str + [current_risk_level_str]
        all_deception_flags_counts_combined = historical_deception_flags_counts + [current_flags_count]

        # Convert string risk levels to numerical values for trend calculation
        # Low = 1, Medium = 2, High = 3. Unknowns are skipped for trend.
        risk_values_numerical: List[float] = []
        for risk_str_val in all_risk_levels_str_combined:
            if risk_str_val == "low":
                risk_values_numerical.append(1.0)
            elif risk_str_val == "medium":
                risk_values_numerical.append(2.0)
            elif risk_str_val == "high":
                risk_values_numerical.append(3.0)

        # If not enough data for trend, provide current assessment.
        if len(risk_values_numerical) < 2:
            return f"Initial risk assessment: {current_risk_level_str.upper()} risk level with {current_flags_count} deception indicators noted."

        # Calculate trends for numerical risk values and deception flag counts
        risk_trend_slope = self._calculate_trend(risk_values_numerical)
        flags_trend_slope = self._calculate_trend([float(fc) for fc in all_deception_flags_counts_combined]) # Ensure float for trend

        # --- Generate insight string based on trends ---
        trajectory_classification_str = ""
        risk_trend_description = ""
        # Interpret risk trend slope
        if risk_trend_slope > 0.3:  # Threshold for what's considered an escalating trend
            trajectory_classification_str = "ESCALATING"
            risk_trend_description = "Risk levels appear to be increasing as the conversation unfolds"
        elif risk_trend_slope < -0.3: # Threshold for a decreasing trend
            trajectory_classification_str = "DECREASING"
            risk_trend_description = "Risk levels seem to be declining throughout the session"
        else: # Relatively stable
            trajectory_classification_str = "STABLE"
            risk_trend_description = "Risk levels have remained relatively consistent"

        # Interpret deception indicators trend
        flags_trend_description = ""
        if flags_trend_slope > 0.5: # Threshold for increasing number of flags
            flags_trend_description = f" The count of deception indicators is also trending upwards (currently {current_flags_count})."
        elif flags_trend_slope < -0.5: # Threshold for decreasing flags
            flags_trend_description = f" The count of deception indicators shows a downward trend (currently {current_flags_count})."
        else: # Stable flag count
            flags_trend_description = f" The count of deception indicators has remained relatively steady (currently {current_flags_count})."

        # Add context about the current risk level
        current_risk_context_str = ""
        if current_risk_level_str == "high":
            current_risk_context_str = " The latest analysis reveals multiple concerning patterns requiring immediate attention."
        elif current_risk_level_str == "medium":
            current_risk_context_str = " The latest analysis suggests moderate risk factors that should be carefully monitored."
        else: # "low" or "unknown"
            current_risk_context_str = " The latest analysis shows minimal or undetermined risk indicators."

        return f"{trajectory_classification_str} risk trajectory identified. {risk_trend_description}.{flags_trend_description}{current_risk_context_str}"
    
    def _analyze_conversation_dynamics(self, session_context: Dict, current_analysis: Dict, session_history: List[Dict]) -> str:
        """
        Analyzes the overall flow and dynamics of the conversation.

        This includes assessing the pace of interaction (analyses per minute),
        average length of responses (as a proxy for detail), variability in
        response length (as a proxy for engagement), and overall session progression.

        Args:
            session_context: Context of the current session.
            current_analysis: The latest analysis data.
            session_history: List of past analyses in the session.

        Returns:
            A string describing the conversation dynamics.
        """
        
        num_total_analyses = session_context.get("previous_analyses", 0) + 1
        session_duration_minutes = session_context.get("session_duration", 0.0) # Ensure float

        # Calculate conversation pace: number of analyzed segments per minute.
        analyses_per_minute = 0.0
        if session_duration_minutes > 0:
            analyses_per_minute = num_total_analyses / session_duration_minutes

        # Gather all transcripts (history + current) to analyze response lengths
        historical_transcripts = session_context.get("recent_transcripts", []) # List of past transcript strings
        current_transcript_str = current_analysis.get("transcript", "")
        all_transcripts_combined = historical_transcripts + [current_transcript_str]

        # Calculate average response length in words
        response_word_counts = [len(t.split()) for t in all_transcripts_combined if t and t.strip()]
        avg_response_word_count = statistics.mean(response_word_counts) if response_word_counts else 0.0

        # --- Generate insight string based on dynamics ---
        # Describe conversation pace
        pace_description = ""
        if analyses_per_minute > 1.5: # More than 1.5 segments analyzed per minute
            pace_description = "a rapid-fire conversation with quick exchanges"
        elif analyses_per_minute > 0.5: # Between 0.5 and 1.5 segments per minute
            pace_description = "a moderate conversation pace with regular interaction"
        else: # Fewer than 0.5 segments per minute (could be long responses or long pauses)
            pace_description = "a deliberate conversation, possibly with extended responses or significant pauses between analyzed segments"

        # Describe response detail level based on average word count
        detail_level_description = ""
        if avg_response_word_count > 120:
            detail_level_description = "providing detailed and comprehensive responses"
        elif avg_response_word_count > 40:
            detail_level_description = "giving moderate-length responses with adequate detail"
        else:
            detail_level_description = "providing brief and concise responses"

        # Analyze engagement pattern based on variance in response lengths
        engagement_pattern_description = ""
        if len(response_word_counts) > 1:
            length_variance = statistics.variance(response_word_counts)
            # A high variance relative to the mean length might indicate fluctuating engagement.
            # (Threshold is heuristic: if standard deviation is > 75% of mean length)
            if length_variance > (avg_response_word_count * 0.75) ** 2 and avg_response_word_count > 0 :
                engagement_pattern_description = "Response length varies significantly across turns, which could suggest fluctuating engagement levels or changes in topic depth."
            else:
                engagement_pattern_description = "Response length remains relatively consistent, indicating stable engagement or a consistent communication style."
        elif len(response_word_counts) == 1:
            engagement_pattern_description = "This is the first analyzed response segment, establishing an initial baseline for communication patterns."
        else: # No response data
            engagement_pattern_description = "No transcript data is available to assess engagement patterns from response lengths."

        # Describe session progression based on the number of analyses
        session_progression_description = ""
        if num_total_analyses <= 2:
            session_progression_description = "The conversation is in its early stages, with initial communication patterns just beginning to develop."
        elif num_total_analyses <= 5:
            session_progression_description = "The conversation has progressed, allowing for the establishment of clearer communication dynamics."
        else: # More than 5 analyses
            session_progression_description = "This extended conversation is revealing deeper and more established behavioral and interactional patterns."

        return (f"The session demonstrates {pace_description} over approximately {session_duration_minutes:.1f} minutes, "
                f"with the speaker typically {detail_level_description} (average {avg_response_word_count:.0f} words per segment). "
                f"{engagement_pattern_description} {session_progression_description} ({num_total_analyses} segments analyzed so far).")
    
    def _calculate_trend(self, values: List[float]) -> float:
        """
        Calculates a simple linear trend (slope) in a list of numerical values.
        The x-values are implicitly assumed to be sequential (0, 1, 2, ...).

        Args:
            values: A list of numbers (float or int) for which to calculate the trend.

        Returns:
            The slope of the linear trend line. Returns 0.0 if there are fewer than
            two data points, as a trend cannot be determined.
        """
        if len(values) < 2: # Need at least two points to determine a trend
            return 0.0
        
        # Using a simple linear regression slope formula: m = Cov(x,y) / Var(x)
        # Where x is the sequence [0, 1, ..., n-1]
        n = len(values)
        x_series_vals = list(range(n)) # X values representing time points or sequence
        x_mean = sum(x_series_vals) / n
        y_mean = sum(values) / n
        
        # Calculate the numerator of the slope formula (Covariance part)
        # Sum of (x_i - x_mean) * (y_i - y_mean)
        numerator = sum((x_series_vals[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        # Calculate the denominator of the slope formula (Variance of x part)
        # Sum of (x_i - x_mean)^2
        denominator = sum((x_series_vals[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0: # Should not happen if n >= 2, but as a safeguard
            return 0.0
        
        slope = numerator / denominator
        return slope

# Global instance of SessionInsightsGenerator that can be imported and used by other services.
session_insights_generator = SessionInsightsGenerator()
