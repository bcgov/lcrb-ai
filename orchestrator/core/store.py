from typing import Dict, Any, List

# In-memory session store (swap Cosmos later)
DB_SESSIONS: Dict[str, Dict[str, Any]] = {}
DB_APPLICATIONS: Dict[str, Dict[str, Any]] = {}
DB_FEEDBACK: List[Dict[str, Any]] = []  # Will be migrated to CosmosDB

def get_state(session_id: str) -> Dict[str, Any]:
    """Return or initialize session state."""
    return DB_SESSIONS.setdefault(session_id, {
        "selected_business_id": None,
        "active_application_id": None,
        "consent": {"pii_ok": False, "analytics_ok": False},
    })
