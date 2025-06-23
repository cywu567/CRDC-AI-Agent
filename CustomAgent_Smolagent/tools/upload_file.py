from smolagents.tools import Tool
from typing import Type
from pydantic import BaseModel, Field
import mimetypes
import requests


class UploadFileInput(BaseModel):
    batch: dict = Field(..., description="The batch object returned from `create_batch`.")
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
    
    def forward(self, batch: dict, file_name: str, file_path: str) -> str:
        """
        The forward method extracts the signed URL from the batch and uploads the file to it via HTTP PUT.
        """
        presigned_url = None
        for file_info in batch["files"]:
            if file_info["fileName"] == file_name:
                presigned_url = file_info["signedURL"]
                break

        if presigned_url is None:
            raise ValueError(f"File {file_name} not found in batch.")
        
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        headers = {
            "Content-Type": mime_type
        }
        with open(file_path, "rb") as f:
            file_data = f.read()

        res = requests.put(presigned_url, data=file_data, headers=headers)
        if not res.ok:
            raise Exception(f"Error uploading file {file_path}: {res.text}")
        
        return f"Uploaded {file_path}"

    def _run(self, args: UploadFileInput) -> str:
        """
        The _run method is responsible for invoking the forward method with arguments.
        """
        return self.forward(
            batch=args.batch,
            file_name=args.file_name,
            file_path=args.file_path
        )