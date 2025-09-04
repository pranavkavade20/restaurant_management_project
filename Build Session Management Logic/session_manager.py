import uuid
import time
import json
import os

# ---------------- Configuration Constants ---------------- #
SESSION_LIFETIME = 300  # Default: 5 minutes (can be adjusted as needed)
STORAGE_FILE = "sessions.json"


class SessionManager:
    def __init__(self, session_lifetime=SESSION_LIFETIME, storage_file=STORAGE_FILE):
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
        """
        Load sessions from a JSON file.
        Returns an empty dictionary if the file does not exist or is invalid.
        """
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_sessions(self):
        """
        Save current sessions to a JSON file for persistence.
        Ensures data is flushed properly to disk.
        """
        try:
            with open(self.storage_file, "w", encoding="utf-8") as file:
                json.dump(self.sessions, file, indent=4)  # pretty-print for readability
        except IOError as e:
            print(f"Error saving sessions: {e}")

    # ---------------- Session Operations ---------------- #
    def create_session(self, user_id):
        """
        Create a new session for a given user.
        :param user_id: Unique identifier for the user (str or int).
        :return: Newly created session_id as string.
        """
        if not isinstance(user_id, (str, int)) or not user_id:
            raise ValueError("Invalid user_id. Must be a non-empty string or integer.")

        session_id = str(uuid.uuid4())  # unique session ID
        now = time.time()

        self.sessions[session_id] = {
            "user_id": str(user_id),
            "created_at": now,
            "last_accessed": now
        }

        self._save_sessions()
        return session_id

    def get_session(self, session_id):
        """
        Retrieve a session if valid.
        Implements sliding expiration:
        - If session is valid, update last_accessed (auto-refresh).
        - If expired, remove it from storage.
        :param session_id: Session ID string
        :return: Session data dict if valid, else None
        """
        session = self.sessions.get(session_id)

        if session is None:
            return None

        now = time.time()
        # Check expiry using last_accessed for sliding expiration
        if now - session["last_accessed"] > self.session_lifetime:
            del self.sessions[session_id]
            self._save_sessions()
            return None

        # Session is valid → update last_accessed
        session["last_accessed"] = now
        self._save_sessions()
        return session

    def delete_session(self, session_id):
        """
        Delete a session (e.g., user logout).
        :param session_id: Session ID string
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()

    def cleanup_expired_sessions(self):
        """
        Remove all expired sessions.
        This can be scheduled periodically in production (e.g., cron or background thread).
        """
        now = time.time()
        expired = [
            sid for sid, data in self.sessions.items()
            if now - data["last_accessed"] > self.session_lifetime
        ]

        for sid in expired:
            del self.sessions[sid]

        if expired:
            self._save_sessions()
