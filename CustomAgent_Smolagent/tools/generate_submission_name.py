from smolagents.tools import Tool
from pydantic import BaseModel
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
    
    def forward(self) -> str:
        """
        The forward method is responsible for generating a unique submission name
        using the current date and time.
        """
        return "sub_" + datetime.now().strftime("%y%m%d_%H%M%S")

    def _run(self, args: EmptyInput) -> str:
        """
        The _run method is responsible for invoking the forward method.
        """
        return self.forward()
