from smolagents.tools import Tool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests

API_URL = "https://hub-qa.datacommons.cancer.gov/api/graphql"
SUBMIT_TOKEN = os.getenv("SUBMITTER_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {SUBMIT_TOKEN}",
    "Content-Type": "application/json"
}


class CreateBatchInput(BaseModel):
    submission_id: str = Field(..., description="ID of the submission to associate the batch with.")
    file_names: list[str] = Field(..., description="List of file names to include in the batch.")
    batch_type: str = Field("metadata", description="Type of batch. Defaults to 'metadata_template'.")


class CreateBatchTool(Tool):
    name = "create_batch"
    description = (
        "Creates a batch in the submission to group files for upload, returning presigned URLs."
    )
    input_model = CreateBatchInput
    output_type = "object"
    inputs = input_model.model_json_schema()["properties"]
    
    def forward(self, batch_type: str, submission_id: str, file_names: list[str]) -> dict:
        """
        The forward method is expected to take parameters matching the `inputs` keys.
        """
        mutation = """
        mutation createBatch($submissionID: ID!, $type: String, $files: [String!]!) {
        createBatch(submissionID: $submissionID, type: $type, files: $files) {
            _id
            submissionID
            bucketName
            filePrefix
            type
            fileCount
            files {
            fileName
            signedURL
            }
            status
            createdAt
            updatedAt
        }
        }
        """
        variables = {
            "submissionID": submission_id,
            "type": batch_type,
            "files": file_names,
        }
        res = requests.post(API_URL, json={"query": mutation, "variables": variables}, headers=HEADERS)
        if not res.ok:
            raise Exception(f"Error creating batch: {res.text}")
        data = res.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        return data["data"]["createBatch"]

    def _run(self, args: CreateBatchInput) -> dict:
        """
        The `_run` method can remain as is, or it can be adapted to call `forward` directly.
        """
        return self.forward(
            batch_type=args.batch_type,
            submission_id=args.submission_id,
            file_names=args.file_names,
        )