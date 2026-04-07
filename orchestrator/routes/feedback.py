import uuid
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from orchestrator.schemas.feedback_schema import FeedbackSubmission, FeedbackResponse
from orchestrator.clients.cosmos_feedback_client import get_feedback_client
from orchestrator.core.store import DB_FEEDBACK

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["feedback"])


# ---------------------------------------------------------------------------
# Helpers — write/read via CosmosDB when available, otherwise in-memory
# ---------------------------------------------------------------------------

async def _store(record: dict) -> None:
    client = get_feedback_client()
    if client:
        await client.upsert(record)
    else:
        DB_FEEDBACK.append(record)


async def _query(
    session_id: Optional[str],
    feedback_type: Optional[str],
    source_app: Optional[str],
    limit: int,
    skip: int,
):
    client = get_feedback_client()
    if client:
        return await client.query(
            session_id=session_id,
            feedback_type=feedback_type,
            source_app=source_app,
            limit=limit,
            skip=skip,
        )

    # In-memory fallback
    results = DB_FEEDBACK.copy()
    if session_id:
        results = [f for f in results if f.get("session_id") == session_id]
    if feedback_type:
        results = [f for f in results if f.get("feedback_type") == feedback_type]
    if source_app:
        results = [f for f in results if f.get("source_app") == source_app]
    results.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    total = len(results)
    return results[skip: skip + limit], total


async def _stats() -> dict:
    client = get_feedback_client()
    if client:
        return await client.get_stats()

    # In-memory fallback
    thumbs_up = sum(1 for f in DB_FEEDBACK if f.get("feedback_type") == "thumbs_up")
    thumbs_down = sum(1 for f in DB_FEEDBACK if f.get("feedback_type") == "thumbs_down")
    total = len(DB_FEEDBACK)
    satisfaction = round(thumbs_up / total * 100, 2) if total > 0 else 0
    return {
        "total_feedback": total,
        "thumbs_up": thumbs_up,
        "thumbs_down": thumbs_down,
        "satisfaction_rate": satisfaction,
        "by_intent": _intent_stats_from_memory(),
    }


def _intent_stats_from_memory() -> dict:
    intent_stats: dict = {}
    for feedback in DB_FEEDBACK:
        intent = feedback.get("intent") or "unknown"
        intent_stats.setdefault(intent, {"thumbs_up": 0, "thumbs_down": 0, "total": 0})
        intent_stats[intent]["total"] += 1
        if feedback.get("feedback_type") == "thumbs_up":
            intent_stats[intent]["thumbs_up"] += 1
        elif feedback.get("feedback_type") == "thumbs_down":
            intent_stats[intent]["thumbs_down"] += 1
    return intent_stats


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackSubmission):
    """
    Submit feedback (thumbs up/down) for an AI assistant response.

    Accepts submissions from any source app — the orchestrator itself, the
    accelerator portal, or future channels — and writes to the unified
    CosmosDB feedback container (falls back to in-memory when not configured).
    """
    feedback_id = str(uuid.uuid4())

    record = {
        "id": feedback_id,
        "type": "feedback",
        "session_id": feedback.session_id,
        "feedback_type": feedback.feedback_type,
        "assistant_message": feedback.assistant_message,
        "user_message": feedback.user_message,
        "intent": feedback.intent,
        "timestamp": feedback.timestamp,
        "created_at": datetime.utcnow().isoformat(),
        "message_id": feedback.message_id,
        "source_app": feedback.source_app,
        "tags": feedback.tags or [],
        "details": feedback.details or "",
    }

    await _store(record)

    return FeedbackResponse(ok=True, feedback_id=feedback_id)


@router.get("")
async def get_feedback(
    session_id: Optional[str] = Query(None),
    feedback_type: Optional[str] = Query(None),
    source_app: Optional[str] = Query(None),
    limit: int = Query(100),
    skip: int = Query(0),
):
    """Retrieve feedback records, optionally filtered by session, type, or source app."""
    results, total = await _query(
        session_id=session_id,
        feedback_type=feedback_type,
        source_app=source_app,
        limit=limit,
        skip=skip,
    )
    return {"feedback": results, "total": total, "returned": len(results), "skip": skip, "limit": limit}


@router.get("/stats")
async def get_feedback_stats():
    """Aggregate feedback statistics, broken down by intent and source app."""
    return await _stats()
