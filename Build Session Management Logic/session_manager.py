import uuid
import time
import json
import os

class SessionManager:
    def __init__(self, session_lifetime=300, storage_file="sessions.json"):
        """
        Initialize the session manager.
            :param session_lifetime: Time (in seconds) before session expires.
            :param storage_file: Path to JSON file for persistence.
        """
        self.session_lifetime = session_lifetime
        self.storage_file = storage_file
        self.sessions = self._load_sessions()

    # ---------------- Persistence Helpers ---------------- #
    def _load_sessions(self):
        """Load sessions from JSON file if available, otherwise return empty dict."""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_sessions(self):
        """Save current sessions dictionary to JSON file."""
        with open(self.storage_file, "w") as f:
            json.dump(self.sessions, f)

    # ---------------- Session Operations ---------------- #
    def create_session(self, user_id):
        """
        Create a new session for a given user.
        Generates a UUID token and stores session data.
        """
        session_id = str(uuid.uuid4())  # unique session ID
        now = time.time()
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": now,
            "last_accessed": now
        }
        self._save_sessions()  # persist to file
        return session_id

    def get_session(self, session_id):
        """
        Retrieve session if valid. Supports sliding expiration:
        - If session is valid, update last_accessed (auto-refresh).
        - If expired, delete it.
        """
        session = self.sessions.get(session_id)

        if not session:
            return None

        now = time.time()
        # check expiry using last_accessed for sliding expiration
        if now - session["last_accessed"] > self.session_lifetime:
            del self.sessions[session_id]   # expired → remove
            self._save_sessions()
            return None

        # session is valid → update last_accessed
        session["last_accessed"] = now
        self._save_sessions()
        return session

    def delete_session(self, session_id):
        """Manually delete a session (logout)."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()

    def cleanup_expired_sessions(self):
        """Remove expired sessions (good for periodic cleanup)."""
        now = time.time()
        expired = [sid for sid, data in self.sessions.items()
                   if now - data["last_accessed"] > self.session_lifetime]

        for sid in expired:
            del self.sessions[sid]

        if expired:
            self._save_sessions()

