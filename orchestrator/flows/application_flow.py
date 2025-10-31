from dataclasses import dataclass, field
from typing import Dict, Optional, List

REQUIRED_FIELDS = [
    # order matters for the chat flow
    "legal_name",
    "premises_address",
    "contact_email",
    "contact_phone",
    "floorplan_document_id",  # filled by the upload step
]

@dataclass
class AppState:
    app_id: str
    app_type: str
    next_field: Optional[str] = None
    values: Dict[str, str] = field(default_factory=dict)
    completed: bool = False

    def compute_next(self) -> Optional[str]:
        for f in REQUIRED_FIELDS:
            if not self.values.get(f):
                self.next_field = f
                return f
        self.next_field = None
        self.completed = True
        return None
