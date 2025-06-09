# Session Service Documentation (`session_service.py`)

This document provides an overview of the `ConversationHistory` class from `backend/services/session_service.py`. This class is responsible for managing conversation sessions, including storing transcripts, analysis results, and providing methods to access this data for ongoing session insights.

**Note:** The class is named `ConversationHistory` in the source file, not `SessionService`. A global instance `conversation_history_service` is provided for direct use.

## Class: `ConversationHistory`

### Overall Purpose
The `ConversationHistory` class serves as an in-memory store for managing data related to different conversation sessions. For each session, it maintains a history of interactions, including transcripts and summaries of their corresponding analyses. This history is then used by services like the `SessionInsightsGenerator` to derive higher-level insights. It supports creating new sessions, adding analysis data, and retrieving session-specific information.

---

### `__init__(self)`

#### Purpose
The constructor initializes the `ConversationHistory` service.

#### Initialization
*   **`self.sessions: Dict[str, Dict[str, Any]]`**: An in-memory dictionary is initialized to store all session data. The keys of this dictionary are session IDs. Each value is another dictionary holding the data for that session, such as `created_at`, `history` (a list of analysis entries), and `analysis_count`.

---

### Public Methods

#### `get_or_create_session(self, session_id: Optional[str] = None) -> str`
*   **Purpose**: Retrieves an existing session by its ID or creates a new one if the ID is not provided or not found.
*   **Input Parameters**:
    *   `session_id: Optional[str]` (Default: `None`): The ID of the session to retrieve or create. If `None`, a new UUID will be generated.
*   **Return Value**:
    *   `str`: The session ID (either the one provided or the newly generated one).
*   **Key Operations**:
    *   If `session_id` is not provided, a new UUID is generated.
    *   If the `session_id` is not found in `self.sessions`, a new entry is created with:
        *   `"created_at"`: Current datetime.
        *   `"history"`: An empty list to store analysis segments.
        *   `"analysis_count"`: Initialized to 0.

#### `add_analysis(self, session_id: str, transcript: str, analysis_result: Dict[str, Any])`
*   **Purpose**: Adds a new transcript segment and its corresponding analysis result to a specified session's history.
*   **Input Parameters**:
    *   `session_id: str`: The ID of the session to update. If the session doesn't exist, it will be created implicitly (though ideally, `get_or_create_session` should be called first).
    *   `transcript: str`: The transcript segment for this analysis entry.
    *   `analysis_result: Dict[str, Any]`: A dictionary containing the full analysis results for the given transcript.
*   **Key Operations**:
    *   Retrieves the session or creates it if it doesn't exist.
    *   Increments the session's `analysis_count`.
    *   Creates a `history_entry` dictionary containing:
        *   `"timestamp"`: Current datetime.
        *   `"transcript"`: The provided transcript.
        *   `"analysis"`: A *summary* of the `analysis_result`, extracting key metrics like credibility score, confidence, overall risk, top emotion, red flags count, a preview of Gemini summary, and some linguistic metrics (hesitation count, speech rate, formality score), and deception flags.
        *   `"analysis_number"`: The current `analysis_count`.
    *   Appends this `history_entry` to the session's `"history"` list.
    *   **Memory Management**: Truncates the `"history"` list to keep only the last 10 entries to prevent memory bloat.

#### `get_session_history_for_api(self, session_id: str) -> List[Dict[str, Any]]`
*   **Purpose**: Retrieves the summarized history of analysis entries for a given session, suitable for API responses.
*   **Input Parameters**:
    *   `session_id: str`: The ID of the session.
*   **Return Value**:
    *   `List[Dict[str, Any]]`: A list of history entries (summaries) for the session. Returns an empty list if the session is not found.

#### `get_session_history(self, session_id: str) -> List[Dict[str, Any]]`
*   **Purpose**: Retrieves the session history in a format specifically reconstructed for use by the `SessionInsightsGenerator`.
*   **Input Parameters**:
    *   `session_id: str`: The ID of the session.
*   **Return Value**:
    *   `List[Dict[str, Any]]`: A list of history entries. Each entry contains the timestamp, transcript, and a reconstructed `"analysis"` dictionary suitable for insight generation. Returns an empty list if the session is not found.
*   **Key Operations**:
    *   Iterates through the stored summarized history.
    *   For each entry, it reconstructs a more detailed (though still somewhat summarized) `"analysis"` dictionary from the stored summary fields to match the expected structure for insight generation (e.g., `emotion_analysis` is a list with one item, `risk_assessment` is a dict).

#### `delete_session(self, session_id: str) -> bool`
*   **Purpose**: Deletes all data associated with a given session ID.
*   **Input Parameters**:
    *   `session_id: str`: The ID of the session to delete.
*   **Return Value**:
    *   `bool`: `True` if the session was found and deleted, `False` otherwise.

#### `get_session_context(self, session_id: str) -> Dict[str, Any]`
*   **Purpose**: Gathers and returns a context dictionary for a given session, primarily for use by the `SessionInsightsGenerator`.
*   **Input Parameters**:
    *   `session_id: str`: The ID of the session.
*   **Return Value**:
    *   `Dict[str, Any]`: A dictionary containing session context:
        *   `"previous_analyses"`: Total count of historical analyses.
        *   `"session_duration"`: Current session duration in minutes.
        *   `"recent_transcripts"`: List of the last 3 transcripts.
        *   `"recent_patterns"`: Results from `_extract_patterns` on the last 5 history entries.
    *   Returns an empty dictionary if the session is not found.
*   **Key Operations**:
    *   Calculates session duration.
    *   Extracts recent transcripts.
    *   Calls `_extract_patterns` to identify recurring patterns in recent history.

---

### Private Helper Methods

#### `_extract_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]`
*   **Purpose**: Analyzes a list of (reconstructed) history entries to find recurring deception flags, emotion trends, and credibility score trends.
*   **Input Parameters**:
    *   `history: List[Dict[str, Any]]`: A list of reconstructed history entries (typically the last 5).
*   **Return Value**:
    *   `Dict[str, Any]`: A dictionary containing:
        *   `"recurring_deception_flags"`: Counts of different flag types.
        *   `"emotion_trends"`: Counts of different top emotions.
        *   `"credibility_trend"`: A list of credibility scores.
*   **Key Operations**:
    *   Iterates through the provided history.
    *   Aggregates counts for deception flags and emotions.
    *   Collects credibility scores.

---

**Global Instance:**
A global instance `conversation_history_service = ConversationHistory()` is created within the module, making it easy to import and use this service as a singleton across the application.
