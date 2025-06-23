from smolagents.tools import Tool
from typing import Type
from pydantic import BaseModel, Field
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
        """
        The forward method updates the batch by marking the provided files as succeeded.
        """
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
        res = requests.post(API_URL, json={"query": mutation, "variables": variables}, headers=HEADERS)
        if not res.ok:
            raise Exception(f"Error updating batch: {res.text}")
        data = res.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        
        # Return the batch update data
        return data["data"]["updateBatch"]

    def _run(self, args: UpdateBatchInput) -> dict:
        """
        The _run method is responsible for invoking the forward method with arguments.
        """
        return self.forward(
            batch_id=args.batch_id,
            file_names=args.file_names
        )
