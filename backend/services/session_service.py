import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any

class ConversationHistory:
    """
    Manages conversation sessions and their analysis history.

    This class is responsible for creating and tracking multiple conversation sessions.
    For each session, it stores a history of analysis results, including transcripts,
    key metrics from various analyses (credibility, emotion, risk, linguistic patterns),
    and timestamps.

    It provides methods to:
    - Create or retrieve a session.
    - Add new analysis results to a session's history.
    - Retrieve session history in different formats (for API responses vs. internal insights generation).
    - Delete a session.
    - Get a summarized context of a session for generating insights (e.g., recent transcripts, trends).

    The session history is capped at a certain number of entries to manage memory usage.
    The structure of `self.sessions` is:
    {
        "session_id_1": {
            "created_at": datetime_object,
            "history": [
                {
                    "timestamp": datetime_object,
                    "transcript": "speaker's text...",
                    "analysis": { ... summarized analysis results ... },
                    "analysis_number": 1
                },
                ...
            ],
            "analysis_count": N
        },
        "session_id_2": { ... },
        ...
    }
    """
    def __init__(self):
        """
        Initializes the ConversationHistory service.
        Sets up an in-memory dictionary to store all active conversation sessions.
        """
        # self.sessions stores all ongoing conversation sessions.
        # Each key is a session_id (UUID string).
        # Each value is a dictionary containing session metadata and its analysis history.
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """
        Retrieves an existing session by its ID or creates a new one if the ID is not provided
        or does not exist.

        If a new session is created, it's initialized with a creation timestamp,
        an empty history list, and an analysis count of 0.

        Args:
            session_id: Optional. The ID of the session to retrieve or create.
                        If None, a new session ID (UUID4) is generated.

        Returns:
            The session ID (either the one provided or the newly generated one).
        """
        if not session_id: # If no session_id is provided, generate a new one.
            session_id = str(uuid.uuid4()) # Generate a new UUID if no ID is given.

        # If the session ID does not exist in our dictionary, create a new session entry.
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now(),  # Timestamp of session creation.
                "history": [],                 # List to store analysis entries for this session.
                "analysis_count": 0,           # Counter for analyses performed in this session.
            }
        return session_id # Return the session ID (existing or new).

    def add_analysis(self, session_id: str, transcript: str, analysis_result: Dict[str, Any]):
        """
        Adds a new analysis result to the specified session's history.

        If the session ID does not exist, it implicitly creates one (though this
        should ideally be handled by calling `get_or_create_session` first).
        A summarized version of the analysis result is stored to manage memory.
        The history is capped at the last 10 entries.

        Args:
            session_id: The ID of the session to add the analysis to.
            transcript: The transcript of the audio segment that was analyzed.
            analysis_result: A dictionary containing the full analysis results.
        """
        if session_id not in self.sessions:
            # This case should ideally not be hit if session_id is always obtained
            # from get_or_create_session by the calling code (e.g., API routes).
            # Creating it here ensures robustness but might indicate a logic flaw elsewhere.
            self.get_or_create_session(session_id)

        session = self.sessions[session_id]
        session["analysis_count"] += 1 # Increment the analysis counter for this session.

        # Create a summarized history entry to save memory.
        # This extracts key pieces of information from the full analysis_result.
        history_entry = {
            "timestamp": datetime.now(), # Timestamp for this specific analysis.
            "transcript": transcript,    # The analyzed transcript.
            "analysis": { # Summarized analysis data
                "credibility_score": analysis_result.get("credibility_score"),
                "confidence_level": analysis_result.get("confidence_level"),
                "overall_risk": analysis_result.get("risk_assessment", {}).get("overall_risk") if analysis_result.get("risk_assessment") else None,
                # Assuming emotion_analysis is a list, get the label of the first (top) emotion.
                "top_emotion": analysis_result.get("emotion_analysis", [{}])[0].get("label") if analysis_result.get("emotion_analysis") else None,
                # Count red flags for "Speaker 1" (assuming single speaker focus for this summary).
                "red_flags_count": len(analysis_result.get("red_flags_per_speaker", {}).get("Speaker 1", [])) if analysis_result.get("red_flags_per_speaker") else 0,
                # Store a preview of the Gemini summary.
                "gemini_summary_preview": str(analysis_result.get("gemini_summary", ""))[:200] + "..." if analysis_result.get("gemini_summary") else None,
                # Include key linguistic analysis data needed for generating session insights later.
                "hesitation_count": analysis_result.get("linguistic_analysis", {}).get("hesitation_count", 0),
                "speech_rate_wpm": analysis_result.get("linguistic_analysis", {}).get("speech_rate_wpm", 150), # Default if not found
                "formality_score": analysis_result.get("linguistic_analysis", {}).get("formality_score", 50), # Default if not found
                "deception_flags": analysis_result.get("deception_flags", []) # List of deception flags
            },
            "analysis_number": session["analysis_count"] # Sequence number of this analysis in the session.
        }
        session["history"].append(history_entry)

        # Memory management: Keep only the last 10 analysis entries in the history.
        # This prevents the session history from growing indefinitely.
        if len(session["history"]) > 10:
            session["history"] = session["history"][-10:] # Slice to keep the newest 10 entries.

    def get_session_history_for_api(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves the analysis history for a given session, formatted for API responses.

        This typically returns the list of summarized history entries as stored.

        Args:
            session_id: The ID of the session whose history is to be retrieved.

        Returns:
            A list of dictionaries, where each dictionary is a summarized
            history entry. Returns an empty list if the session is not found.
        """
        session = self.sessions.get(session_id)
        if not session:
            return [] # Session not found, return empty list.
        return session.get("history", []) # Return the list of history entries.

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves session history and reconstructs parts of the analysis data
        specifically for use by the SessionInsightsGenerator.

        This method transforms the summarized history entries into a format that
        the insights generator expects, which might involve adding back certain
        structures or default values if fields were omitted in the summary.

        Args:
            session_id: The ID of the session.

        Returns:
            A list of dictionaries, with each entry partially reconstructed for
            insights generation. Returns an empty list if the session is not found.
        """
        session = self.sessions.get(session_id)
        if not session:
            return [] # Session not found.
        
        history_for_insights = []
        # Iterate through the stored summarized history.
        for entry in session.get("history", []):
            analysis_summary = entry.get("analysis", {})
            # Reconstruct a dictionary that aligns with what SessionInsightsGenerator might expect.
            # This might involve creating placeholder structures for complex fields like 'emotion_analysis'.
            reconstructed_entry = {
                "timestamp": entry.get("timestamp"),
                "transcript": entry.get("transcript"),
                "analysis": { # Reconstructing the 'analysis' part for insights
                    "credibility_score": analysis_summary.get("credibility_score"),
                    "confidence_level": analysis_summary.get("confidence_level"), 
                    "overall_risk": analysis_summary.get("overall_risk"), # This was already from risk_assessment.overall_risk
                    # Reconstruct emotion_analysis as a list of dicts, using the stored top_emotion.
                    "emotion_analysis": [{"label": analysis_summary.get("top_emotion"), "score": 1.0}] if analysis_summary.get("top_emotion") else [],
                    # Reconstruct linguistic_analysis with stored values.
                    "linguistic_analysis": {
                        "hesitation_count": analysis_summary.get("hesitation_count", 0),
                        "speech_rate_wpm": analysis_summary.get("speech_rate_wpm", 150),
                        "formality_score": analysis_summary.get("formality_score", 50)
                    },
                    # Reconstruct risk_assessment structure.
                    "risk_assessment": {"overall_risk": analysis_summary.get("overall_risk")} if analysis_summary.get("overall_risk") else {},
                    "deception_flags": analysis_summary.get("deception_flags", [])
                }
            }
            history_for_insights.append(reconstructed_entry)
        
        return history_for_insights

    def delete_session(self, session_id: str) -> bool:
        """
        Deletes a session and all its associated history.

        Args:
            session_id: The ID of the session to delete.

        Returns:
            True if the session was found and deleted, False otherwise.
        """
        if session_id in self.sessions:
            del self.sessions[session_id] # Delete the session entry from the dictionary.
            return True
        return False # Session not found.

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieves a context summary for a given session, used for generating insights.

        The context includes:
        - Number of previous analyses in the session.
        - Total duration of the session in minutes.
        - Transcripts of the last 3 analysis segments.
        - Extracted patterns from the last 5 analysis segments (e.g., recurring flags, emotion trends).

        Args:
            session_id: The ID of the session.

        Returns:
            A dictionary containing the session context. Returns an empty dictionary
            if the session is not found.
        """
        if session_id not in self.sessions:
            return {} # Session not found.

        session = self.sessions[session_id]
        session_history = session.get("history", [])

        # Reconstruct a simplified history focused on patterns needed by _extract_patterns.
        # This is similar to get_session_history but tailored for _extract_patterns.
        history_for_pattern_extraction = []
        for h_entry in session_history:
            analysis_summary = h_entry.get("analysis", {})
            reconstructed_analysis_for_patterns = {
                "deception_flags": analysis_summary.get("deception_flags", []),
                "emotion_analysis": [{"label": analysis_summary.get("top_emotion", "unknown"), "score": 1.0}] if analysis_summary.get("top_emotion") else [],
                # For credibility trend, directly use the score if available.
                "gemini_analysis": {"credibility_score": analysis_summary.get("credibility_score")} if analysis_summary.get("credibility_score") is not None else {}
            }
            history_for_pattern_extraction.append({"analysis": reconstructed_analysis_for_patterns})

        # Calculate session duration in minutes.
        session_creation_time = session.get("created_at", datetime.now())
        current_time = datetime.now()
        session_duration_seconds = (current_time - session_creation_time).total_seconds()

        return {
            "previous_analyses": len(session_history), # Count of all analyses stored so far.
            "session_duration": session_duration_seconds / 60,  # Convert duration to minutes.
            # Get the last 3 transcripts. Slicing handles cases with fewer than 3 entries.
            "recent_transcripts": [h["transcript"] for h in session_history[-3:]],
            # Extract patterns from the last 5 entries of the specially prepared history.
            "recent_patterns": self._extract_patterns(history_for_pattern_extraction[-5:])
        }

    def _extract_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extracts recurring patterns from a list of historical analysis entries.

        Specifically, it counts:
        - Occurrences of each type of deception flag.
        - Trends in expressed top emotions.
        - A list of credibility scores for trend analysis.

        Args:
            history: A list of (potentially reconstructed) analysis entries.
                     Each entry is expected to have an "analysis" key containing
                     "deception_flags", "emotion_analysis", and "gemini_analysis" (with "credibility_score").

        Returns:
            A dictionary summarizing the extracted patterns.
        """
        patterns: Dict[str, Any] = {
            "recurring_deception_flags": {}, # Counts of each deception flag type
            "emotion_trends": {},            # Counts of each top emotion
            "credibility_trend": []          # List of credibility scores
        }

        for entry in history:
            analysis = entry.get("analysis", {}) # Get the analysis sub-dictionary

            # Process deception flags
            flags = analysis.get("deception_flags", [])
            for flag_item in flags: # Ensure flag_item is treated as a string
                flag_str = str(flag_item) # Convert to string if it's not already
                # Extract flag type (e.g., "Hesitation" from "Hesitation: Pauses detected")
                flag_type = flag_str.split(":")[0] if ":" in flag_str else flag_str
                patterns["recurring_deception_flags"][flag_type] = patterns["recurring_deception_flags"].get(flag_type, 0) + 1

            # Process emotion trends
            emotions = analysis.get("emotion_analysis", []) # Expected to be a list of dicts
            if emotions and isinstance(emotions, list) and len(emotions) > 0:
                # Assuming the first emotion in the list is the top one, or find max by score if multiple are present.
                # For simplicity, if multiple emotions are provided per entry, this takes the first one.
                # A more robust approach might be to ensure only one top emotion is passed or to average scores.
                top_emotion_details = emotions[0] # Taking the first one as representative
                if isinstance(top_emotion_details, dict):
                    emotion_name = top_emotion_details.get("label", "unknown")
                    patterns["emotion_trends"][emotion_name] = patterns["emotion_trends"].get(emotion_name, 0) + 1

            # Process credibility trend
            # Assuming 'gemini_analysis' might be the source of the primary credibility score for trends.
            gemini_analysis_data = analysis.get("gemini_analysis", {})
            if isinstance(gemini_analysis_data, dict) and "credibility_score" in gemini_analysis_data:
                if gemini_analysis_data["credibility_score"] is not None: # Ensure score is not None
                    patterns["credibility_trend"].append(gemini_analysis_data["credibility_score"])

        return patterns

# Global instance of ConversationHistory, can be imported and used by other modules.
# This allows other parts of the application to share the same conversation history state.
conversation_history_service = ConversationHistory()
