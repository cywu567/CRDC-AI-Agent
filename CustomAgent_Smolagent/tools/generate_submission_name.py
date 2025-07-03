from smolagents.tools import Tool
from pydantic import BaseModel
from db.db import log_feedback, insert_submission, get_feedback_for_tool
from typing import Type
from datetime import datetime

class EmptyInput(BaseModel):
    pass

class GenerateSubmissionNameTool(Tool):
    name = "generate_submission_name"
    description = (
        "Generate a unique submission name that starts with 'sub_' followed by the current date and time"
        "in the format YYMMDD_HHMMSS. This ensures the submission name is unique and does not exceed"
        "25 characters, which is required by the submission API."
    )
    input_model = EmptyInput
    output_type = "string"
    inputs = input_model.model_json_schema()["properties"]
    
    def forward(self):
        feedback = get_feedback_for_tool(tool="GenerateSubmissionName")
        #can use below for future learning
        #for _, is_accepted, comment in feedback:
        #    if not is_accepted and "submission name" in comment.lower():
        #        print(f"⚠️ Noted past rejected pattern: {comment}")
        
        submission_name = "sub_" + datetime.now().strftime("%y%m%d_%H%M%S")
        insert_submission(submission_name)
        dummy_file_id = -1
        log_feedback(
            file_id=dummy_file_id,
            source="system",
            tool="GenerateSubmissionName",
            is_accepted=True,
            comments=f"Generated submission name: {submission_name}"
        )

        return submission_name
