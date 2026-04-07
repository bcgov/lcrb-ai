from pydantic import BaseModel
from typing import Optional


class FeedbackSubmission(BaseModel):
    """Model for submitting feedback on AI assistant responses."""
    session_id: str
    feedback_type: str          # "thumbs_up" or "thumbs_down"
    assistant_message: str
    user_message: Optional[str] = None
    intent: Optional[str] = None
    timestamp: int
    # Enrichment fields — populated by proxying apps
    message_id: Optional[str] = None   # DB message ID from the source app
    source_app: Optional[str] = None   # e.g. "accelerator", "orchestrator"
    tags: Optional[list] = None        # reason tags from thumbs-down modal
    details: Optional[str] = None      # optional free-text from thumbs-down modal


class FeedbackResponse(BaseModel):
    """Response model after feedback submission."""
    ok: bool
    feedback_id: str
    message: str = "Feedback recorded successfully"
