from smolagents.tools import Tool
from pydantic import BaseModel, Field
from typing import Literal
from db.db import log_feedback

class LogFeedbackInput(BaseModel):
    file_id: int = Field(..., description="Row ID in `files` (or step index)")
    source: Literal["user", "system"] = Field(..., description="'user' or 'system'")
    is_accepted: bool = Field(..., description="True for YES, False for NO")
    comments: str = Field(..., description="Optional free-text")

class LogFeedbackTool(Tool):
    name        = "log_feedback"
    description = "Persist feedback (yes/no + comment) into feedback.db"
    input_type  = LogFeedbackInput
    output_type = "string"
    inputs      = LogFeedbackInput.model_json_schema()["properties"]

    def forward(self, file_id, source, is_accepted, comments):
        log_feedback(
            file_id=file_id,
            source=source,
            is_accepted=is_accepted,
            comments=comments
        )
        return "Feedback recorded."
