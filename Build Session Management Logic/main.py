from session_manager import SessionManager
import time

# Initialize with 10s expiry for demo
manager = SessionManager(session_lifetime=10)

# Create a session
session_id = manager.create_session(user_id="user123")
print("New Session:", session_id)

# Access it before expiry (auto-refresh sliding expiration)
time.sleep(5)
print("Accessing session (refreshing):", manager.get_session(session_id))

# Wait again, still within refreshed lifetime
time.sleep(8)
print("Accessing again:", manager.get_session(session_id))

# Force cleanup
manager.cleanup_expired_sessions()
print("After cleanup:", manager.get_session(session_id))
