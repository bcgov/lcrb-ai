import uuid
from typing import Any, Dict, List
from orchestrator.core.store import DB_APPLICATIONS
from .validator import validate

FIELDS: List[Dict[str, Any]] = [
    {"id": "business_name", "label": "Business Name", "type": "text", "required": True},
    {"id": "establishment_address", "label": "Establishment Address", "type": "text", "required": True},
    {"id": "establishment_name", "label": "Establishment Name", "type": "text", "required": True},
    {"id": "hours", "label": "Operating Hours", "type": "compound", "required": True, "help_ref": "policy_manual.lp.hours"},
    {"id": "minors_policy", "label": "Minors Policy", "type": "select", "required": True},
    {"id": "floorplan_uploaded", "label": "Floorplan Uploaded", "type": "boolean", "required": False},
]

def create_draft(business_id: str, app_type="liquor_primary") -> str:
    app_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
    DB_APPLICATIONS[app_id] = {"type": app_type, "business_id": business_id, "data": {}, "status": "Draft", "fees": None, "receipt_id": None}
    return app_id


def get_required_fields(_: str) -> List[Dict[str, Any]]:
    return FIELDS


def upsert_field(application_id: str, field_id: str, value: Any) -> Dict[str, Any]:
    draft = DB_APPLICATIONS[application_id]
    draft["data"][field_id] = value
    if field_id in ("hours", "minors_policy"):
        v = validate("liquor_primary", field_id, value, draft["data"])
        return {"ok": True, "errors": [], "warnings": v["reasons"] if v["decision"] != "allow" else [], "decision": v["decision"]}
    return {"ok": True, "errors": [], "warnings": [], "decision": "allow"}


def review(application_id: str) -> Dict[str, Any]:
    draft = DB_APPLICATIONS[application_id]
    data = draft["data"]
    missing = [f["id"] for f in FIELDS if f.get("required", True) and f["id"] not in data]
    warnings = []
    if "hours" in data:
        v = validate("liquor_primary", "hours", data["hours"], data)
        if v["decision"] == "warn":
            warnings.extend(v["reasons"])
    return {"missing": missing, "warnings": warnings, "summary": data}


def compute_fees(application_id: str) -> Dict[str, Any]:
    lines = [{"desc": "Liquor Primary Application", "amount": 110.00}]
    total = sum(l["amount"] for l in lines)
    DB_APPLICATIONS[application_id]["fees"] = total
    return {"line_items": lines, "total": total}


def submit(application_id: str, attestation: bool) -> Dict[str, Any]:
    if not attestation:
        return {"ok": False, "error": "Attestation required."}
    draft = DB_APPLICATIONS[application_id]
    if not draft["data"].get("floorplan_uploaded"):
        return {"ok": False, "error": "Floorplan missing. Please upload a stamped floorplan."}
    receipt = f"R-{uuid.uuid4().hex[:6].upper()}"
    draft["status"] = "Submitted"
    draft["receipt_id"] = receipt
    return {"ok": True, "receipt_id": receipt, "status": "Submitted"}
