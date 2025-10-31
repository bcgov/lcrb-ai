from typing import Dict
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
import os, re, mimetypes

_di = DocumentIntelligenceClient(
    endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"),
    credential = AzureKeyCredential(os.getenv("DOCUMENT_INTELLIGENCE_KEY"))
)

SCALE_PATTERNS = [
    re.compile(r"\bscale\s*[:=]?\s*\d+\s*:\s*\d+\b", re.I),                         # Scale 1:100
    re.compile(r"\bscale\s*[:=]?\s*\d+(?:\.\d+)?\s*(mm|cm|m)\s*=\s*\d+(?:\.\d+)?\s*(mm|cm|m)\b", re.I),  # 1 mm = 100 mm
    re.compile(r"\bscale\s*[:=]?\s*(\d+/\d+)\s*\"?\s*=\s*1\s*'?[-]?\s*\d*\"?\b", re.I),         # 3/16" = 1'-0"
    re.compile(r"\b1\s*[:=]\s*\d{2,4}\b", re.I),                                                # bare ratio 1:100
]
def _has_scale(t: str) -> bool:
    if any(p.search(t) for p in SCALE_PATTERNS):
        return True
    for m in re.finditer(r"\bscale\b", t, flags=re.I):
        win = t[max(0, m.start()-80): m.end()+80]
        if re.search(r"\d+\s*:\s*\d+|\d+/\d+|1\s*'?\s*-\s*\d+\"?", win):
            return True
    return False

def screen(application_id: str, filename: str, content_bytes: bytes) -> Dict:
    # detect a proper content type; DI rejects generic octet-stream for images
    ctype = mimetypes.guess_type(filename)[0]
    if not ctype:
        if filename.lower().endswith(".pdf"):
            ctype = "application/pdf"
        elif filename.lower().endswith((".png", ".apng")):
            ctype = "image/png"
        elif filename.lower().endswith((".jpg", ".jpeg")):
            ctype = "image/jpeg"
        elif filename.lower().endswith((".tif", ".tiff")):
            ctype = "image/tiff"
        else:
            ctype = "application/octet-stream"

    if not content_bytes:
        raise ValueError("Empty upload content.")

    poller = _di.begin_analyze_document(
        model_id="prebuilt-layout",
        body=content_bytes,
        content_type=ctype
    )
    r = poller.result()
    text = (getattr(r, "content", "") or "").lower()
    if not text and getattr(r, "pages", None):
        text = " ".join([para.content for p in r.pages for para in (p.paragraphs or [])]).lower()

    issues = []
    if not re.search(r"(occupant\s*load|max(?:imum)?\s*occupanc\w*)[^0-9]{0,40}\d{1,5}", text):
        issues.append({
            "code": "MISSING_OCCUPANT_LOAD_STAMP",
            "message": "No occupant-load text detected.",
            "fix_tip": "Upload a plan with a clearly labeled occupant-load value."
        })
    if not _has_scale(text.lower()):
        issues.append({
            "code": "NO_SCALE_BAR",
            "message": "No scale information detected.",
            "fix_tip": "Include printed scale (e.g., 1:100 or 3/16\" = 1'-0\") or a bar scale."
        })

    if not any(k in text for k in ["p.eng", "professional engineer", "architect", "aibc", "seal", "registered"]):
        issues.append({
            "code": "NO_PROFESSIONAL_STAMP_HINT",
            "message": "No textual hint of a professional stamp found.",
            "fix_tip": "Ensure the drawing includes a legible professional stamp."
        })

    return {"passed": len(issues) == 0, "issues": issues}

