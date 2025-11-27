import json
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, Any
from orchestrator.core.store import get_state, DB_APPLICATIONS
from orchestrator.core.orchestrator import Orchestrator
from orchestrator.agents import rag_agent
from orchestrator.agents.applications.liquor_primary_agent import create_draft, get_required_fields, upsert_field, review, compute_fees, submit, SLOT_MAP
from orchestrator.agents.applications.screening import screen
# from orchestrator.clients.portal_api import PortalApi
# from flask import request


app = FastAPI(title="Orchestrator Agent Service")
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
TESTS_DIR = BASE_DIR.parent / "tests"
SAMPLE_FLOORPLAN = TESTS_DIR / "floorplan_sample.pdf"


# Helpers
def _ensure_app(session_id: str) -> str:
    app_id = get_state(session_id).get("active_application_id")
    if not app_id:
        raise HTTPException(status_code = 400, detail = "No active application.")
    if app_id not in DB_APPLICATIONS:
        raise HTTPException(status_code = 404, detail = f"Application {app_id} not found")
    return app_id

def _ensure_attachments(app_id: str):
    DB_APPLICATIONS[app_id].setdefault("attachments", [])

def _compute_next_field(app_id: str):
    fields = get_required_fields(app_id)
    fields = [f for f in fields if f.get("type") != "file"]
    rev = review(app_id)
    form_ids = {f["id"] for f in fields}
    target = next((m for m in rev.get("missing", []) if m in form_ids), None)
    if not target:
        data = DB_APPLICATIONS[app_id].get("data", {})
        for f in fields:
            if f.get("required", True):
                val = data.get(f["id"]); t = f.get("type")
                if t == "boolean":
                    if f.get("required_true", False):
                        if val is not True: target = f["id"]; break
                    elif val is None: target = f["id"]; break
                elif t == "number":
                    if val in (None, ""): target = f["id"]; break
                else:
                    if val is None or (isinstance(val, str) and not val.strip()): target = f["id"]; break
    if not target: return None
    for f in fields:
        if f["id"] == target:
            return {"id": f["id"], "label": f.get("label"), "type": f.get("type"),
                    "required": f.get("required", True), "help": f.get("help_ref")}
    return None

class ChatTurn(BaseModel):
    session_id: str
    message: str
    selected_index: Optional[str] = None

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/debug")
def debug_apps():
    return {"apps": list(DB_APPLICATIONS.keys())}

@app.post("/chat")
async def chat(turn: ChatTurn, request: Request):
    state = get_state(turn.session_id)
    routing = Orchestrator.intent_router(turn.message)

    if routing["intent"] in ("QA", "IN_FORM_HELP"):
        qa = await rag_agent.answer(turn.message, turn.session_id, turn.selected_index)
        return {
            "intent": routing["intent"],
            "confidence": routing["confidence"],
            "entities": routing.get("entities", {}),
            "state": state,
            "rag": qa
        }

    if routing["intent"].startswith("NAV_"):
        ctas = []
        qa = await rag_agent.answer(turn.message, turn.session_id, turn.selected_index)
        if routing["intent"] == "NAV_DASHBOARD":
            ctas = [{"label": "Go to Dashboard", "routerLink": ["/dashboard"]}]
        elif routing["intent"] == "NAV_ACCOUNT":
            ctas = [{"label": "Account Settings", "routerLink": ["/account-profile"]}]
        elif routing["intent"] == "NAV_LICENCES":
            ctas = [{"label": "Licences Dashboard", "routerLink": ["/licences"]}]
        return {
            "intent": routing["intent"],
            "confidence": routing["confidence"],
            "entities": routing.get("entities", {}),
            "state": state,
            "message": "Here are quick links.",
            "ctas": ctas,
            "rag": qa
        }

    if routing["intent"] == "NEXT_FIELD":
        app_id = state.get("active_application_id")
        if not app_id:
            return {
                "intent": "NEXT_FIELD",
                "confidence": routing["confidence"],
                "entities": routing.get("entities", {}),
                "state": state,
                "message": "No active application. Say 'start application' first."
            }
        rev = review(app_id)
        next_field = _compute_next_field(app_id)
        res =  {
            "intent": "NEXT_FIELD",
            "confidence": routing["confidence"],
            "entities": routing.get("entities", {}),
            "state": state,
            "message": "Here’s the next required field." if next_field else "All required fields are filled.",
            "review": rev,
            "next_field": next_field,
            "application_id": app_id
        }
        if next_field is None and not rev.get("missing"):
            res.setdefault("ctas", []).append({"label": "Submit Application"})
        return res

    if routing["intent"] == "START_APPLICATION":
        state["selected_business_id"] = state.get("selected_business_id") or "B1"
        app_id = state.get("active_application_id")
        if not app_id:
            # app_id = create_draft(state["selected_business_id"])
            # auth_header = request.headers.get("Authorization", "")
            # token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header

            # portal = PortalApiClient(
            #     base_url="http://localhost:5000",
            #     token_provider=lambda: token
            # )

            app_id = create_draft(state["selected_business_id"])
            state["active_application_id"] = app_id

        rev = review(app_id)
        next_field = _compute_next_field(app_id)

        return {
            "application_id": app_id,
            "intent": "START_APPLICATION",
            "confidence": routing["confidence"],
            "entities": routing.get("entities", {}),
            "state": state,
            "message": f"Created Liquor Primary draft: {app_id}",
            "review": rev,
            "next_field": next_field,
            "ctas": [
                {"label": "Open Application", "href" : f"/assets/mock-app.html?session_id={turn.session_id}&app_id={app_id}"},
                {"label": "Upload floorplan"}
            ]
        }
    
    if routing["intent"] == "RENEWALS":
        return {
            "intent": "RENEWALS",
            "confidence": routing["confidence"],
            "entities": routing.get("entities", {}),
            "state": state,
            "message": "You do not have any licenses that are eligible for renewal. Your licence for Jo's Kitchen expires on Oct 30, 2026. *sample response",
            "ctas": [{"label": "Go to Licences Dashboard", "routerLink": ["/licences"]}]
        }
    
    if routing["intent"] == "APPLICATION_STATUS":
        mock_apps = [
            {
                "id": "FP-0001234",
                "name": "Jo's Kitchen",
                "type": "Food Primary",
                "status_code": "APPROVAL_IN_PRINCIPLE",
                "status_label": "Approval in Principle",
                "submitted_on": "2025-01-15",
                "last_updated": "2025-02-10"
            },
            {
                "id": "LP-0000456",
                "name": "Jo's Bar & Lounge",
                "type": "Liquor Primary",
                "status_code": "IN_DRAFT",
                "status_label": "In Draft",
                "submitted_on": "2025-02-01",
                "last_updated": "2025-02-20"
            }
        ]

        return {
            "intent": "APPLICATION_STATUS",
            "confidence": routing["confidence"],
            "entities": routing.get("entities", {}),
            "state": state,
            "message": "Here are your current applications and their status.",
            "applications": mock_apps
        }
    
    if routing["intent"] == "RECENT_FLOORPLAN":
        base_url = str(request.base_url).rstrip("/")
        url = f"{base_url}/samples/floorplan"

        return {
            "intent": "RECENT_FLOORPLAN",
            "confidence": routing["confidence"],
            "entities": routing.get("entities", {}),
            "state": state,
            "message": "Found 1 floorplan. Click on the quick action below to view your latest floorplan. ",
            "ctas": [
                {"label": "Open Floorplan", "href": url}
            ],
            "floorplan_url": url
        }

    return {
        "intent": routing["intent"],
        "confidence": routing["confidence"],
        "entities": routing.get("entities", {}),
        "state": state
    }


@app.get("/application/fields")
async def get_fields(session_id: str):
    app_id = get_state(session_id).get("active_application_id")
    if not app_id:
        raise HTTPException(status_code=400, detail="No active application. Start one via /chat.")
    return {"application_id": app_id, "fields": get_required_fields(app_id)}


@app.post("/application/upsert")
async def upsert(application_id: str = Form(...), field_id: str = Form(...), value: str = Form(...), session_id: Optional[str] = None):
    v: Any = value
    if field_id == "hours":
        v = json.loads(value)  # expects {"open":"10:00","close":"01:30","days":"daily"}
    if field_id == "floorplan_uploaded":
        v = value.lower() == "true"
    try:
        return upsert_field(application_id, field_id, v)
    except KeyError:
        # fallback: try the active app for this session (handles restarts/other workers)
        if session_id:
            sid_app = get_state(session_id).get("active_application_id")
            if sid_app:
                return upsert_field(sid_app, field_id, v)
        raise HTTPException(status_code=404, detail=f"Application {application_id} not found. Start an application again.")


@app.get("/application/review")
async def review_app(session_id: str):
    app_id = get_state(session_id).get("active_application_id")
    if not app_id:
        raise HTTPException(status_code=400, detail="No active application.")
    return review(app_id)


@app.get("/application/fees")
async def fees(session_id: str):
    app_id = get_state(session_id).get("active_application_id")
    if not app_id:
        raise HTTPException(status_code=400, detail="No active application.")
    return compute_fees(app_id)


@app.post("/application/submit")
async def submit_app(session_id: str, attestation: bool = Form(True)):
    app_id = get_state(session_id).get("active_application_id")
    if not app_id:
        raise HTTPException(status_code=400, detail="No active application.")
    return submit(app_id, attestation)


@app.post("/upload/floorplan")
async def upload_floorplan(session_id: str, file: UploadFile = File(...)):
    # app_id = get_state(session_id).get("active_application_id")
    # if not app_id:
    #     raise HTTPException(status_code=400, detail="No active application.")
    # content = await file.read()
    # result = screen(app_id, file.filename, content)
    # if result.get("passed"):
    #     DB_APPLICATIONS[app_id]["data"]["floorplan_uploaded"] = True
    # return result
    return await upload_attachment(session_id=session_id, slot="floor_plan", file=file)

@app.post("/attachments/upload")
async def upload_attachment(
    session_id: str,
    slot: str = Query(..., description="e.g., floor_plan | letter_of_intent | signage_photos"),
    file: UploadFile = File(...)
):
    app_id = _ensure_app(session_id)
    print(app_id)
    _ensure_attachments(app_id)
    content = await file.read()

    # Screen only the required floor plans (demo) - logic can be added later to support all different files
    screening = {}
    if slot == "floor_plan":
        screening = screen(app_id, file.filename, content)  or {}
        if screening.get("passed"):
            DB_APPLICATIONS[app_id].setdefault("data", {}).update({"floorplan_uploaded": True})
        
    att_id = f"att-{len(DB_APPLICATIONS[app_id]['attachments'])+1}"
    DB_APPLICATIONS[app_id]["attachments"].append({
        "id": att_id,
        "slot": slot, 
        "filename": file.filename,
        "mimetype": file.content_type,
        "size": len(content)
    })

    return {"ok": True, "attachment_id": att_id, "slot": slot, "screening": screening}

@app.get("/attachments")
async def list_attachments(session_id: str):
    app_id = _ensure_app(session_id)
    _ensure_attachments(app_id)
    return {"application_id": app_id, "attachments": DB_APPLICATIONS[app_id]["attachments"]}

@app.post("/validate/floorplan")
async def validate_floorplan(file: UploadFile = File(...)):
    content = await file.read()
    s = screen("N/A", file.filename, content) or {}
    return {"passed": bool(s.get("passed")), "reasons": [i.get("message") for i in (s.get("issues") or [])]}

@app.get("/samples/floorplan")
async def sample_floorplan():
    if not SAMPLE_FLOORPLAN.exists():
        raise HTTPException(status_code=404, detail="Sample floorplan not found.")
    return FileResponse(
        SAMPLE_FLOORPLAN,
        media_type="application/pdf",
        filename="floorplan_sample.pdf"
    )
