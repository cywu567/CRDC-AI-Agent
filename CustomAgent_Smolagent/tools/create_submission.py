from smolagents.tools import Tool
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
        """
        The forward method now accepts the expected arguments, matching the `inputs`.
        """
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
        res = requests.post(API_URL, json={"query": mutation, "variables": variables}, headers=HEADERS)
        if not res.ok:
            raise Exception(f"Error creating submission: {res.text}")
        data = res.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors in create_submission: {data['errors']}")
        
        # Return the response data, which is a dictionary
        return data["data"]["createSubmission"]

    def _run(self, args: CreateSubmissionInput) -> dict:
        """
        The _run method is responsible for passing arguments to the `forward` method.
        """
        return self.forward(
            study_id=args.study_id,
            data_commons=args.data_commons,
            name=args.name,
            intention=args.intention,
            data_type=args.data_type,
        )
