from pydantic import BaseModel
from typing import Optional


class FeedbackSubmission(BaseModel):
    """Model for submitting feedback on AI assistant responses"""
    session_id: str
    feedback_type: str  # "thumbs_up" or "thumbs_down"
    assistant_message: str
    user_message: Optional[str] = None
    intent: Optional[str] = None
    timestamp: int


class FeedbackResponse(BaseModel):
    """Response model after feedback submission"""
    ok: bool
    feedback_id: str
    message: str = "Feedback recorded successfully"
