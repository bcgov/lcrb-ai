import uuid
from typing import Any, Dict, List
from orchestrator.core.store import DB_APPLICATIONS
from orchestrator.schemas.liquor_primary_schema import FIELD_SCHEMA
from datetime import datetime
from .validator import validate
import os

REQUIRED_SLOTS = ["floor_plan", "site_plan"]
OPTIONAL_SLOTS = [
    "central_securities_register",
    "supporting_documents",
    "personal_history_summary",
    "shareholders",
    "letter_of_intent",
    "signage_documents"
]

def create_draft(business_id: str, app_type="liquor_primary") -> str:
    app_id = f"APP-{len(DB_APPLICATIONS)+1:07d}"
    DB_APPLICATIONS[app_id] = {
        "type": app_type,
        "business_id": business_id,
        "data": {},
        "attachments": [],
        "status": "Draft",
        "fees": None,
        "receipt_id": None}

    # Seed the default values (province, country, etc.)
    for f in FIELD_SCHEMA: 
        if "default" in f: 
            DB_APPLICATIONS[app_id]["data"][f["id"]] = f["default"]

    return app_id


def get_required_fields(_: str) -> List[Dict[str, Any]]:
    return FIELD_SCHEMA


def upsert_field(app_id: str, field_id: str, value: Any) -> Dict[str, Any]:
    draft = DB_APPLICATIONS[app_id]
    # Normalize common transformers
    if field_id == "establishmentAddressPostalCode" and isinstance(value, str):
        value = value.strip().upper().replace(" ", "")
        # insert space (A1A 1A1) if 6 chars
        if len(value) == 6:
            value = value[:3] + " " + value[3:]
    
    if field_id == "totalOccupantLoad":
        try:
            value = int(value) if value not in (None, "") else None
        except Exception:
            raise ValueError("totalOccupantLoad must be a number")

    # support ID/Name pairs from autocomplete components
    if field_id in ("indigenousNationId", "policeJurisdictionId"):
        value = (value or "").strip()

    draft["data"][field_id] = value
    return {"ok": True, "field_id": field_id, "value": value}


def review(app_id: str) -> Dict[str, Any]:
    app = DB_APPLICATIONS[app_id]
    data = app.get("data", {})
    atts = app.get("attachments", []) or []

    missing: List[str] = []
    warnings: List[str] = []

    # Required Fields
    for f in FIELD_SCHEMA:
        if f.get("required"):
            val = data.get(f["id"])
            t = f.get("type")
            if t == "boolean":
                # Required booleans must be set. If a specific boolean must be True (eg, declarations),
                # mark it in FIELD_SCHEMA with "required_true": True
                if f.get("required_true", False):
                    if val is not True:
                        missing.append(f["id"])
                elif val is None:
                    missing.append(f["id"])
            elif t == "number":
                if val in (None, ""):
                    missing.append(f["id"])
            else:
                if val is None or (isinstance(val, str) and not val.strip()):
                    missing.append(f["id"])
    
    # Required upload slots
    present_slots = {a.get("slot") for a in atts}
    for slot in REQUIRED_SLOTS:
        if slot not in present_slots:
            missing.append(slot)
    
    # Warnings and Soft Rules
    # 1) Hours pairing – if any daily "Open" is set, require matching "Close" for that day (warning only)
    day_pairs = [
        ("serviceHoursSundayOpen", "serviceHoursSundayClose"),
        ("serviceHoursMondayOpen", "serviceHoursMondayClose"),
        ("serviceHoursTuesdayOpen", "serviceHoursTuesdayClose"),
        ("serviceHoursWednesdayOpen", "serviceHoursWednesdayClose"),
        ("serviceHoursThursdayOpen", "serviceHoursThursdayClose"),
        ("serviceHoursFridayOpen", "serviceHoursFridayClose"),
        ("serviceHoursSaturdayOpen", "serviceHoursSaturdayClose"),
    ]
    for open_id, close_id in day_pairs:
        open_v, close_v = data.get(open_id), data.get(close_id)
        if (open_v and not close_v) or (close_v and not open_v):
            warnings.append(f"Hours pairing incomplete: {open_id} / {close_id}.")

    # 2) Zoning hint – if zoning not confirmed, warn (does not block)
    if data.get("isPermittedInZoning") is not True:
        warnings.append("Zoning declaration is not confirmed.")
    
    return {"missing": missing, "warnings": warnings}


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
