from smolagents.tools import Tool
from db.db import log_feedback
from typing import Type
from pydantic import BaseModel, Field
import time
import os
import requests

API_URL = "https://hub-qa.datacommons.cancer.gov/api/graphql"
SUBMIT_TOKEN = os.getenv("SUBMITTER_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {SUBMIT_TOKEN}",
    "Content-Type": "application/json"
        }

class CreateSubmissionInput(BaseModel):
    study_id: str = Field(..., description="The ID of the study to submit data to.")
    data_commons: str = Field(..., description="The name of the data commons (e.g., 'ICDC').")
    name: str = Field(..., description="Name for the submission.")
    intention: str = Field(..., description="Submission intention ('New/Update' or 'Delete').")
    data_type: str = Field(..., description="Type of submission ('Metadata Only' or 'Metadata and Data Files').")
    

class CreateSubmissionTool(Tool):
    name = "create_submission"
    description = (
       "Creates a submission request in the data commons system."
    )
    input_model = CreateSubmissionInput
    output_type = "string"
    inputs = input_model.model_json_schema()["properties"]
    
    def forward(self, study_id: str, data_commons: str, name: str, intention: str, data_type: str) -> dict:
        dummy_file_id = -1

        mutation = """
        mutation createSubmission($studyID: String!, $dataCommons: String!, $name: String!, $intention: String!, $dataType: String!) {
            createSubmission(
                studyID: $studyID
                dataCommons: $dataCommons
                name: $name
                intention: $intention
                dataType: $dataType
            ) {
                _id
                status
                createdAt
            }
        }
        """

        variables = {
            "studyID": study_id,
            "dataCommons": data_commons,
            "name": name,
            "intention": intention,
            "dataType": data_type,
        }

        try:
            res = requests.post(API_URL, json={"query": mutation, "variables": variables}, headers=HEADERS)
            res.raise_for_status()
            data = res.json()

            if "errors" in data:
                raise Exception(f"GraphQL errors: {data['errors']}")

            result = data["data"]["createSubmission"]

            log_feedback(
                file_id=dummy_file_id,
                source="system",
                tool="CreateSubmission",
                is_accepted=True,
                comments=f"Submission created successfully: {result['_id']}"
            )

            return result

        except Exception as e:
            log_feedback(
                file_id=dummy_file_id,
                source="system",
                tool="CreateSubmission",
                is_accepted=False,
                comments=f"Submission creation failed: {str(e)}"
            )
            raise
                

