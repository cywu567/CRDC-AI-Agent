from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from fedlead_agent_crewai.utils.session_manager import get_page, set_page
from fedlead_agent_crewai.utils.smart_click import smart_click
import time


class NavigateToolInput(BaseModel):
    """Input schema for NavigateTool."""
    destination: str = Field(..., description="Where to go, like 'start a new submission request'")


class NavigateTool(BaseTool):
    name: str = "navigate"
    description: str = (
        "Navigate through the CRDC portal. "
        "Based on the destination description, it clicks the right buttons to get there. "
        "This tool uses reasoning to figure out which UI elements to interact with."
    )
    args_schema: Type[BaseModel] = NavigateToolInput

    def _run(self, destination: str) -> str:
        try:
            page = get_page()

            # Use smart_click with the destination goal
            result = smart_click(page, destination)
            set_page(page)
            return f"Navigation result: {result}\nFinal URL: {page.url}"

        except Exception as e:
            return f"NavigateTool error: {str(e)}"

