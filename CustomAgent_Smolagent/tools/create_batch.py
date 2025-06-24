from smolagents.tools import Tool
from db.db import log_feedback, get_file_id
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
    submission_name: str = Field(..., description="Name of the submission for DB lookup.")


class CreateBatchTool(Tool):
    name = "create_batch"
    description = (
        "Creates a batch in the submission to group files for upload, returning presigned URLs."
    )
    input_model = CreateBatchInput
    output_type = "object"
    inputs = input_model.model_json_schema()["properties"]
    
    def forward(self, batch_type: str, submission_id: str, submission_name: str, file_names: list[str]) -> dict:
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
        try:
            res = requests.post(API_URL, json={"query": mutation, "variables": variables}, headers=HEADERS)
            res.raise_for_status()
            data = res.json()
            if "errors" in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            # Use submission_name (not submission_id) for DB lookups
            for file_name in file_names:
                try:
                    file_id = get_file_id(submission_name, file_name)  # Changed here
                    log_feedback(
                        file_id=file_id,
                        source="system",
                        is_accepted=True,
                        comments="Batch created and file included successfully.",
                        tool="CreateBatch"
                    )
                except Exception as fe:
                    print(f"Failed to log system feedback for file '{file_name}': {fe}")
            
            return data["data"]["createBatch"]

        except Exception as e:
            for file_name in file_names:
                try:
                    file_id = get_file_id(submission_name, file_name)  # Changed here
                    log_feedback(
                        file_id=file_id,
                        source="system",
                        is_accepted=False,
                        comments=f"Batch creation failed: {e}",
                        tool="CreateBatch"
                    )
                except Exception as fe:
                    print(f"Failed to log failed feedback for file '{file_name}': {fe}")
            raise