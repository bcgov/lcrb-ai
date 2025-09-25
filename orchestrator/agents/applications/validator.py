from typing import Any, Dict

def validate(license_type: str, field_id: str, value: Any, context: Dict[str, Any]) -> Dict[str, Any]:
    out = {"decision": "allow", "reasons": [], "policy_refs": []}
    if field_id == "hours":
        close = (value or {}).get("close", "00:00")
        if close > "01:00":
            out["decision"] = "warn"
            out["reasons"].append("Closing past 1:00 may require local government endorsement.")
            out["policy_refs"].append("policy_manual.lp.hours.section_3_2")
    if field_id == "minors_policy":
        if value in ("allow", True):
            out["decision"] = "block"
            out["reasons"].append("Liquor Primary generally restricts minors; adjust selection.")
            out["policy_refs"].append("policy_manual.lp.minors.section_4_1")
    return out
