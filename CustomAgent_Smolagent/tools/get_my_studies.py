from smolagents.tools import Tool
from typing import Type
from db.db import log_feedback
from pydantic import BaseModel, Field
import requests
import os

API_URL = "https://hub-qa.datacommons.cancer.gov/api/graphql"
SUBMIT_TOKEN = os.getenv("SUBMITTER_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {SUBMIT_TOKEN}",
    "Content-Type": "application/json"
}
        
        
class EmptyInput(BaseModel):
    pass


class GetMyStudiesTool(Tool):
    name = "get_my_studies"
    description = (
        "Fetches study IDs for the user using the CRDC GraphQL API."
    )
    input_model = EmptyInput
    output_type = "array"
    inputs = input_model.model_json_schema()["properties"]
    
    def forward(self) -> list[str]:
        query = """
        query getMyUser {
          getMyUser {
            _id
            studies {
              _id
            }
          }
        }
        """
        dummy_file_id = -1
        try:
            res = requests.post(API_URL, json={"query": query}, headers=HEADERS)
            res.raise_for_status()
            data = res.json()
            study_ids = [s["_id"] for s in data["data"]["getMyUser"]["studies"]]
            log_feedback(
                file_id=dummy_file_id,
                source="system",
                tool="GetMyStudies",
                is_accepted=True,
                comments=f"Fetched {len(study_ids)} study IDs."
            )
            return study_ids
        except Exception as e:
            log_feedback(
                file_id=dummy_file_id,
                source="system",
                tool="GetMyStudies",
                is_accepted=False,
                comments=f"Error fetching studies: {str(e)}"
            )
            raise