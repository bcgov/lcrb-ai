from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from orchestrator.schemas.feedback_schema import FeedbackSubmission, FeedbackResponse
from orchestrator.core.store import DB_FEEDBACK

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackSubmission):
    """
    Submit feedback (thumbs up/down) for an AI assistant response.

    This endpoint stores user feedback on assistant messages for analysis and improvement.
    When migrating to CosmosDB, this will write to a feedback container.
    """
    # Generate a unique feedback ID
    feedback_id = f"feedback-{len(DB_FEEDBACK) + 1}-{feedback.timestamp}"

    # Create feedback record
    feedback_record = {
        "id": feedback_id,
        "session_id": feedback.session_id,
        "feedback_type": feedback.feedback_type,
        "assistant_message": feedback.assistant_message,
        "user_message": feedback.user_message,
        "intent": feedback.intent,
        "timestamp": feedback.timestamp,
        "created_at": datetime.utcnow().isoformat(),
    }

    # Store in memory (will be CosmosDB)
    DB_FEEDBACK.append(feedback_record)

    return FeedbackResponse(
        ok=True,
        feedback_id=feedback_id,
        message="Feedback recorded successfully"
    )


@router.get("")
async def get_feedback(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    feedback_type: Optional[str] = Query(None, description="Filter by type: thumbs_up or thumbs_down"),
    limit: int = Query(100, description="Maximum number of records to return"),
    skip: int = Query(0, description="Number of records to skip (for pagination)")
):
    """
    Retrieve feedback records for analysis.

    Returns all feedback or filtered by session_id/feedback_type.
    Supports pagination via limit and skip parameters.
    """
    # Start with all feedback
    results = DB_FEEDBACK.copy()

    # Apply filters
    if session_id:
        results = [f for f in results if f.get("session_id") == session_id]

    if feedback_type:
        results = [f for f in results if f.get("feedback_type") == feedback_type]

    # Sort by timestamp (newest first)
    results.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    # Apply pagination
    total = len(results)
    results = results[skip:skip + limit]

    return {
        "feedback": results,
        "total": total,
        "returned": len(results),
        "skip": skip,
        "limit": limit
    }


@router.get("/stats")
async def get_feedback_stats():
    """
    Get aggregate statistics on feedback.

    Returns counts of thumbs up/down and overall satisfaction metrics.
    """
    thumbs_up = len([f for f in DB_FEEDBACK if f.get("feedback_type") == "thumbs_up"])
    thumbs_down = len([f for f in DB_FEEDBACK if f.get("feedback_type") == "thumbs_down"])
    total = len(DB_FEEDBACK)

    satisfaction_rate = (thumbs_up / total * 100) if total > 0 else 0

    return {
        "total_feedback": total,
        "thumbs_up": thumbs_up,
        "thumbs_down": thumbs_down,
        "satisfaction_rate": round(satisfaction_rate, 2),
        "by_intent": _get_feedback_by_intent()
    }


def _get_feedback_by_intent():
    """Helper to aggregate feedback by intent"""
    intent_stats = {}

    for feedback in DB_FEEDBACK:
        intent = feedback.get("intent") or "unknown"
        if intent not in intent_stats:
            intent_stats[intent] = {"thumbs_up": 0, "thumbs_down": 0, "total": 0}

        intent_stats[intent]["total"] += 1
        if feedback.get("feedback_type") == "thumbs_up":
            intent_stats[intent]["thumbs_up"] += 1
        elif feedback.get("feedback_type") == "thumbs_down":
            intent_stats[intent]["thumbs_down"] += 1

    return intent_stats
