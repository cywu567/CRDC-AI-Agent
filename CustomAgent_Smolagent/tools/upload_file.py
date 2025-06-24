from smolagents.tools import Tool
from typing import Type
from pydantic import BaseModel, Field
import mimetypes
from db.db import log_feedback, get_file_id
import requests


class UploadFileInput(BaseModel):
    batch: dict = Field(..., description="The batch object returned from `create_batch`.")
    submission_name: str = Field(..., description="The submission name to look up file ID.")
    file_name: str = Field(..., description="The name of the file to find.")
    file_path: str = Field(..., description="Path to the local file to upload.")

class UploadFileTool(Tool):
    name = "upload_file"
    description = (
        "Extracts the signed URL for a specific file name from the batch object and uploads a local file to it via HTTP PUT."
    )
    input_model = UploadFileInput
    output_type = "string"
    inputs = input_model.model_json_schema()["properties"]
    
    def forward(self, batch: dict, submission_name: str, file_name: str, file_path: str) -> str:
        try:
            file_id = get_file_id(submission_name, file_name)
        except Exception as e:
            print(f"Warning: could not find file_id for {file_name} in submission {submission_name}: {e}")
            file_id = -1
        
        presigned_url = None
        for file_info in batch["files"]:
            if file_info["fileName"] == file_name:
                presigned_url = file_info["signedURL"]
                break

        if presigned_url is None:
            error_msg = f"File {file_name} not found in batch."
            log_feedback(
                file_id=file_id,
                source="system",
                is_accepted=False,
                comments=error_msg,
                tool=self.name
            )
            raise ValueError(error_msg)
        
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        headers = {
            "Content-Type": mime_type
        }

        try:
            with open(file_path, "rb") as f:
                file_data = f.read()

            res = requests.put(presigned_url, data=file_data, headers=headers)
            if not res.ok:
                raise Exception(f"Error uploading file {file_path}: {res.text}")

            log_feedback(
                file_id=file_id,
                source="system",
                is_accepted=True,
                comments=f"Uploaded file {file_path} successfully.",
                tool=self.name
            )

            return f"Uploaded {file_path}"

        except Exception as e:
            log_feedback(
                file_id=file_id,
                source="system",
                is_accepted=False,
                comments=f"Failed to upload file {file_path}: {str(e)}",
                tool=self.name
            )
            raise