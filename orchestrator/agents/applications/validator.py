from typing import Any, Dict
import re

TIME_RE = re.compile(r"^\d{2}:\d{2}$")
ELEVEN_PM = "23:00"

def validate(license_type: str, field_id: str, value: Any, context: Dict[str, Any]) -> Dict[str, Any]:
    out = {"decision": "allow", "reasons": [], "policy_refs": []}

    # per-day scalar time strings, e.g. serviceHoursSundayOpen="09:00"
    if field_id.startswith("serviceHours") and (field_id.endswith("Open") or field_id.endswith("Close")):
        # must be "HH:MM"
        if value not in (None, "") and (not isinstance(value, str) or not TIME_RE.match(value)):
            out["decision"] = "block"
            out["reasons"].append(f"{field_id} must be a time string in HH:MM (e.g., 09:00).")
            return out

        # policy check: closing past 11:00 PM triggers a warning
        if field_id.endswith("Close") and isinstance(value, str) and value > ELEVEN_PM:
            out["decision"] = "warn"
            out["reasons"].append("Closing past 11:00 PM may require local government endorsement.")
            out["policy_refs"].append("policy_manual.lp.hours.section_3_2")
        return out

    # All other fields: allow by default; field-specific validation handled elsewhere
    return out