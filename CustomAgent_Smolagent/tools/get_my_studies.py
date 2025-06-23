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
        """
        The forward method performs the actual task of fetching study IDs.
        """
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
        res = requests.post(API_URL, json={"query": query}, headers=HEADERS)
        if not res.ok:
            raise Exception(f"Error fetching studies: {res.text}")
        data = res.json()
        return [s["_id"] for s in data["data"]["getMyUser"]["studies"]]

    def _run(self, args: EmptyInput) -> list[str]:
        """
        The _run method is responsible for invoking the forward method.
        """
        return self.forward()
