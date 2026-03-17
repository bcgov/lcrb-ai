from typing import Dict, Any, Optional
import os
from openai import AzureOpenAI

AOAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AOAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AOAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AOAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

FALLBACK_THRESHOLD = float(os.getenv("CLASSIFIER_THRESHOLD", "0.7"))


def _aoai_client() -> Optional[AzureOpenAI]:
    if not (AOAI_ENDPOINT and AOAI_CHAT_DEPLOYMENT):
        return None
    return AzureOpenAI(
        azure_endpoint=AOAI_ENDPOINT,
        api_key=AOAI_API_KEY,
        api_version=AOAI_API_VERSION,
    )


def _classify_with_llm(text: str) -> Optional[Dict[str, Any]]:
    client = _aoai_client()
    if client is None:
        return None

    system = (
        "You are a strict classifier for a licensing assistant. "
        "Label the user's request as one of: START_APPLICATION, SCREEN_DOCUMENT, IN_FORM_HELP, QA. "
        "Extract obvious entities if present. "
        "Return STRICT JSON with keys: intent, confidence (0..1), entities (object). No prose."
    )
    user = f"Text: {text}\nRespond with JSON only."

    try:
        resp = client.chat.completions.create(
            model=AOAI_CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.0,
            max_tokens=150,
        )
        content = resp.choices[0].message.content or ""
        import json
        parsed = json.loads(content)
        out = {
            "intent": str(parsed.get("intent", "QA")).strip().upper(),
            "confidence": float(parsed.get("confidence", 0.5)),
            "entities": parsed.get("entities", {}) or {},
        }
        if out["intent"] not in {"START_APPLICATION", "SCREEN_DOCUMENT", "IN_FORM_HELP", "QA"}:
            out["intent"] = "QA"
        out["confidence"] = max(0.0, min(1.0, out["confidence"]))
        return out
    except Exception:
        return None


class Orchestrator:
    @staticmethod
    def intent_router(text: str) -> Dict[str, Any]:
        t = text.lower()

        if any(k in t for k in ["apply", "start application", "begin liquor primary"]):
            return {"intent": "START_APPLICATION", "confidence": 0.9, "entities": {}}
        if any(k in t for k in ["upload", "floorplan", "screen"]):
            return {"intent": "SCREEN_DOCUMENT", "confidence": 0.9, "entities": {}}
        if any(k in t for k in ["help", "what is", "how do i"]):
            return {"intent": "IN_FORM_HELP", "confidence": 0.8, "entities": {}}
        if any(k in t for k in ["dashboard", "home"]):
            return {"intent": "NAV_DASHBOARD", "confidence": 0.9, "entities": {}}
        if any(k in t for k in ["account", "settings", "profile"]):
            return {"intent": "NAV_ACCOUNT", "confidence": 0.9, "entities": {}}
        if any(k in t for k in ["next field", "what's next", "next step", "next required"]):
            return {"intent": "NEXT_FIELD", "confidence": 0.9, "entities": {}}

        llm = _classify_with_llm(text)
        if llm and llm.get("confidence", 0.0) >= FALLBACK_THRESHOLD:
            return {
                "intent": llm.get("intent", "QA"),
                "confidence": llm.get("confidence", 0.7),
                "entities": llm.get("entities", {}),
            }

        return {"intent": "QA", "confidence": 0.95, "entities": {}}
