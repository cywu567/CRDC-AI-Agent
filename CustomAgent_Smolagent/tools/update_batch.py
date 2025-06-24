from smolagents.tools import Tool
from typing import Type
from pydantic import BaseModel, Field
from db.db import log_feedback
import requests
import os

API_URL = "https://hub-qa.datacommons.cancer.gov/api/graphql"
SUBMIT_TOKEN = os.getenv("SUBMITTER_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {SUBMIT_TOKEN}",
    "Content-Type": "application/json"
}

class UpdateBatchInput(BaseModel):
    batch_id: str = Field(..., description="The ID of the batch to update.")
    file_names: list[str] = Field(..., description="List of uploaded file names to mark as succeeded.")
    

class UpdateBatchTool(Tool):
    name = "update_batch"
    description = (
        "Updates the batch after file uploads with required UploadResult fields."
    )
    input_model = UpdateBatchInput
    output_type = "string"
    inputs = input_model.model_json_schema()["properties"]
    
    def forward(self, batch_id: str, file_names: list[str]) -> dict:
        mutation = """
        mutation updateBatch($batchID: ID!, $files: [UploadResult]!) {
            updateBatch(batchID: $batchID, files: $files) {
                _id
                submissionID
                type
                fileCount
                files {
                    filePrefix
                    fileName
                    size
                    status
                    errors
                    createdAt
                    updatedAt
                }
                status
                createdAt
                updatedAt
            }
        }
        """
        files_payload = [{"fileName": f, "succeeded": True, "errors": None} for f in file_names]
        variables = {
            "batchID": batch_id,
            "files": files_payload
        }

        dummy_file_id = -1  # No file id available here

        try:
            res = requests.post(API_URL, json={"query": mutation, "variables": variables}, headers=HEADERS)
            res.raise_for_status()
            data = res.json()
            if "errors" in data:
                raise Exception(f"GraphQL errors: {data['errors']}")

            # Log success for each file
            for file_name in file_names:
                try:
                    log_feedback(
                        file_id=dummy_file_id,
                        source="system",
                        is_accepted=True,
                        comments="Batch file marked as succeeded.",
                        tool=self.name
                    )
                except Exception as fe:
                    print(f"Failed to log success feedback for file '{file_name}': {fe}")

            return data["data"]["updateBatch"]

        except Exception as e:
            # Log failure for each file
            for file_name in file_names:
                try:
                    log_feedback(
                        file_id=dummy_file_id,
                        source="system",
                        is_accepted=False,
                        comments=f"Batch update failed: {e}",
                        tool=self.name
                    )
                except Exception as fe:
                    print(f"Failed to log failure feedback for file '{file_name}': {fe}")
            raise