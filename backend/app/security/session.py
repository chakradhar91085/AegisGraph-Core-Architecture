from typing import Dict, List
import time
import logging
from app.core.config import settings
from app.security.models import SessionState, QueryRecord

logger = logging.getLogger(__name__)

class SessionStore:
    def __init__(self):
        # In-memory session store for Phase 4A
        self.sessions: Dict[str, SessionState] = {}

    def get_or_create_session(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id=session_id)
        return self.sessions[session_id]

    def cleanup_old_history(self, session_id: str, current_time: float):
        """
        Removes query records that fall outside the configured temporal window.
        """
        if session_id not in self.sessions:
            return
            
        state = self.sessions[session_id]
        window = settings.SECURITY_TEMPORAL_WINDOW_SECONDS
        
        cutoff_time = current_time - window
        
        # Keep only records within the window
        # We always keep at least the very last record if it exists for semantic drift,
        # but semantic drift only uses the IMMEDIATELY previous query.
        # So we can keep history for temporal/entity signals, and the last query for semantic drift.
        # Actually, semantic drift just needs the last embedding. We can extract it before filtering, 
        # but to keep it simple, we just use the last item in the history list regardless of window,
        # OR we just say semantic drift only applies if the previous query was within the window.
        # Let's keep it strictly within the window for now, or just retain the last query explicitly.
        
        new_history = [q for q in state.history if q.timestamp >= cutoff_time]
        
        # Always retain the absolute last query so we can compute semantic drift
        # even if it was just outside the temporal window.
        if state.history and not new_history:
            new_history = [state.history[-1]]
            
        state.history = new_history

    def add_query_record(self, session_id: str, record: QueryRecord):
        state = self.get_or_create_session(session_id)
        state.history.append(record)

    def update_smoothed_risk(self, session_id: str, risk: float):
        state = self.get_or_create_session(session_id)
        state.last_smoothed_risk = risk

    def get_previous_query(self, session_id: str) -> QueryRecord | None:
        state = self.get_or_create_session(session_id)
        if not state.history:
            return None
        return state.history[-1]

session_store = SessionStore()
