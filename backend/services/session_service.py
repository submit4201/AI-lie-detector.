import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any

class ConversationHistory:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now(),
                "history": [],
                "analysis_count": 0,
            }
        return session_id

    def add_analysis(self, session_id: str, transcript: str, analysis_result: Dict[str, Any]):
        if session_id not in self.sessions:
            # This case should ideally not be hit if session_id is always obtained from get_or_create_session
            self.get_or_create_session(session_id)

        session = self.sessions[session_id]
        session["analysis_count"] += 1

        # Storing a summary for history
        history_entry = {
            "timestamp": datetime.now(),
            "transcript": transcript,
            "analysis_summary": {
                "credibility_score": analysis_result.get("credibility_score"),
                "overall_risk": analysis_result.get("risk_assessment", {}).get("overall_risk"),
                "top_emotion": analysis_result.get("emotion_analysis", [{}])[0].get("label") if analysis_result.get("emotion_analysis") else None,
            },
            "analysis_number": session["analysis_count"]
        }
        session["history"].append(history_entry)

        # Keep only last 10 analyses to prevent memory bloat
        if len(session["history"]) > 10:
            session["history"] = session["history"][-10:]

    def get_session_history_for_api(self, session_id: str) -> List[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        if not session:
            return []
        return session.get("history", [])

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            return {}

        session = self.sessions[session_id]
        history_for_patterns = []
        for h_entry in session.get("history", []):
            reconstructed_analysis = {
                "deception_flags": h_entry.get("analysis_summary",{}).get("deception_flags", []),
                "emotion_analysis": [{"label": h_entry.get("analysis_summary",{}).get("top_emotion", "unknown"), "score": 1.0}] if h_entry.get("analysis_summary",{}).get("top_emotion") else [],
                "gemini_analysis": {"credibility_score": h_entry.get("analysis_summary",{}).get("credibility_score")} if h_entry.get("analysis_summary",{}).get("credibility_score") is not None else {}
            }
            history_for_patterns.append({"analysis": reconstructed_analysis})

        return {
            "previous_analyses": len(session.get("history", [])),
            "session_duration": (datetime.now() - session.get("created_at", datetime.now())).total_seconds() / 60,  # minutes
            "recent_transcripts": [h["transcript"] for h in session.get("history", [])[-3:]],
            "recent_patterns": self._extract_patterns(history_for_patterns[-5:])
        }

    def _extract_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        patterns: Dict[str, Any] = {
            "recurring_deception_flags": {},
            "emotion_trends": {},
            "credibility_trend": []
        }

        for entry in history:
            analysis = entry.get("analysis", {})

            flags = analysis.get("deception_flags", [])
            for flag in flags:
                flag_type = flag.split(":")[0] if ":" in flag else flag
                patterns["recurring_deception_flags"][flag_type] = patterns["recurring_deception_flags"].get(flag_type, 0) + 1

            emotions = analysis.get("emotion_analysis", [])
            if emotions and isinstance(emotions, list) and len(emotions) > 0:
                top_emotion = max(emotions, key=lambda x: x.get("score", 0)) if emotions else None
                if top_emotion:
                    emotion_name = top_emotion.get("label", "unknown")
                    patterns["emotion_trends"][emotion_name] = patterns["emotion_trends"].get(emotion_name, 0) + 1

            gemini_analysis = analysis.get("gemini_analysis", {})
            if isinstance(gemini_analysis, dict) and "credibility_score" in gemini_analysis:
                patterns["credibility_trend"].append(gemini_analysis["credibility_score"])

        return patterns

# Global instance of ConversationHistory, can be imported by other modules
conversation_history_service = ConversationHistory()
