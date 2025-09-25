from typing import Dict

def screen(application_id: str, filename: str, content_bytes: bytes) -> Dict:
    if "bad" in filename.lower():
        return {
            "passed": False,
            "issues": [
                {"code": "MISSING_OCCUPANT_LOAD_STAMP", "message": "No occupant-load stamp detected.", "fix_tip": "Upload a plan with a stamped occupant load."},
                {"code": "NO_SCALE_BAR", "message": "No scale bar detected.", "fix_tip": "Include a printed scale (e.g., 1:100)."},
            ],
        }
    return {"passed": True, "issues": []}
