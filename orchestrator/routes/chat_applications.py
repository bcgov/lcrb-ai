from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi import Body
from typing import Dict, Any, Optional
import httpx
from .deps import get_portal_api, get_http_client
from orchestrator.flows.application_flow import AppState
from orchestrator.clients.portal_api import PortalApi

router = APIRouter(prefix="/chat/applications", tags=["applications"])

# naive in-memory store (swap for Redis)
APP_STATES: Dict[str, AppState] = {}

def cta(label: str, href: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    obj = {"label": label}
    if href: obj["href"] = href
    if params: obj["params"] = params
    return obj

def summarize(state: AppState) -> str:
    parts = []
    for k,v in state.values.items():
        if v: parts.append(f"- {k}: {v}")
    return "\n".join(parts) or "(no fields yet)"

def require_token(headers: Dict[str,str]) -> str:
    tok = headers.get("x-delegation-jwt") or headers.get("authorization") or headers.get("Authorization")
    if not tok:
        raise HTTPException(status_code=401, detail="Missing delegation token")
    if tok.lower().startswith("bearer "):
        tok = tok.split(" ", 1)[1]
    return tok

@router.post("/start")
async def start_application(
    payload: Dict[str, Any] = Body(...),
    portal: PortalApi = Depends(get_portal_api),
    client: httpx.AsyncClient = Depends(get_http_client),
    headers: Dict[str, str] = Depends(lambda: {})  # set via dependency in your app (Request.headers)
):
    """
    payload: { "app_type": "liquor_primary" }
    Requires header: X-Delegation-JWT: <token>
    """
    token = require_token(headers)
    app_type = payload.get("app_type") or "liquor_primary"

    app_id = await portal.create_application(client, token, app_type)
    state = AppState(app_id=app_id, app_type=app_type)
    state.compute_next()
    APP_STATES[app_id] = state

    msg = f"Created {app_type.replace('_',' ').title()} draft: {app_id}.\n" \
          f"Let’s get this filed. First, what is the **{state.next_field.replace('_',' ')}**?"

    return {
        "application_id": app_id,
        "intent": "START_APPLICATION",
        "state": state.__dict__,
        "message": msg,
        "ctas": [
            cta("Open Application", href=f"/lcrb/applications/{app_id}?type={app_type}")
        ]
    }

@router.post("/{app_id}/field")
async def set_field(
    app_id: str,
    payload: Dict[str, Any] = Body(...),  # {"field":"legal_name","value":"Acme Inc"}
    portal: PortalApi = Depends(get_portal_api),
    client: httpx.AsyncClient = Depends(get_http_client),
    headers: Dict[str, str] = Depends(lambda: {})
):
    token = require_token(headers)
    state = APP_STATES.get(app_id)
    if not state:
        raise HTTPException(status_code=404, detail="Application not tracked")

    field = payload.get("field")
    value = payload.get("value")
    if not field:
        raise HTTPException(status_code=400, detail="Missing 'field'")
    if value in (None, ""):
        return {"message": f"Got it—what should I put for **{field.replace('_',' ')}**?"}

    # Persist to portal
    await portal.patch_fields(client, token, app_id, {field: value})
    # Update state
    state.values[field] = value
    state.compute_next()

    if state.completed:
        msg = "All required fields are filled. You may upload your floorplan (PDF/PNG/JPG) and then **Submit**.\n\n" \
              + summarize(state)
        return {
            "application_id": app_id,
            "intent": "FIELDS_COMPLETE",
            "state": state.__dict__,
            "message": msg,
            "ctas": [
                cta("Open Application", href=f"/lcrb/applications/{app_id}?type={state.app_type}"),
                cta("Submit Now")
            ]
        }
    else:
        msg = f"Saved **{field.replace('_',' ')}**. Next, what is **{state.next_field.replace('_',' ')}**?"
        return {
            "application_id": app_id,
            "intent": "FIELD_SAVED",
            "state": state.__dict__,
            "message": msg,
            "ctas": [cta("Open Application", href=f"/lcrb/applications/{app_id}?type={state.app_type}")]
        }

@router.post("/{app_id}/upload")
async def upload_floorplan(
    app_id: str,
    file: UploadFile = File(...),
    portal: PortalApi = Depends(get_portal_api),
    client: httpx.AsyncClient = Depends(get_http_client),
    headers: Dict[str, str] = Depends(lambda: {})
):
    token = require_token(headers)
    state = APP_STATES.get(app_id)
    if not state:
        raise HTTPException(status_code=404, detail="Application not tracked")

    # Basic validation
    allowed = {"application/pdf", "image/png", "image/jpeg"}
    if (file.content_type or "").lower() not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF/PNG/JPG.")

    file_bytes = await file.read()
    if len(file_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 20MB).")

    doc_id = await portal.upload_document(
        client, token, app_id,
        file_bytes=file_bytes,
        filename=file.filename,
        content_type=file.content_type
    )

    # Save the reference so the flow advances
    state.values["floorplan_document_id"] = doc_id
    state.compute_next()

    msg = f"Uploaded **{file.filename}** successfully."
    if state.completed:
        msg += "\nAll required items are present. Ready to submit?"
        ctas = [cta("Open Application", href=f"/lcrb/applications/{app_id}?type={state.app_type}"),
                cta("Submit Now")]
    else:
        msg += f"\nNext, please provide **{state.next_field.replace('_',' ')}**."

        ctas = [cta("Open Application", href=f"/lcrb/applications/{app_id}?type={state.app_type}")]

    return {
        "application_id": app_id,
        "intent": "DOCUMENT_UPLOADED",
        "state": state.__dict__,
        "message": msg,
        "ctas": ctas
    }

@router.post("/{app_id}/submit")
async def submit_application(
    app_id: str,
    portal: PortalApi = Depends(get_portal_api),
    client: httpx.AsyncClient = Depends(get_http_client),
    headers: Dict[str, str] = Depends(lambda: {})
):
    token = require_token(headers)
    state = APP_STATES.get(app_id)
    if not state:
        raise HTTPException(status_code=404, detail="Application not tracked")

    # Gate on completion
    missing = [f for f in state.values.keys() if not state.values.get(f)]
    if state.next_field:
        raise HTTPException(status_code=400, detail=f"Missing required field: {state.next_field}")

    res = await portal.submit(client, token, app_id)

    msg = f"🎉 Application **{app_id}** submitted."
    return {
        "application_id": app_id,
        "intent": "SUBMITTED",
        "state": state.__dict__,
        "message": msg,
        "result": res,
        "ctas": [cta("View Receipt/Status", href=f"/lcrb/applications/{app_id}?type={state.app_type}")]
    }
