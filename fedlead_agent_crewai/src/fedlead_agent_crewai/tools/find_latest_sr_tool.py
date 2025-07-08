from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from fedlead_agent_crewai.utils.session_manager import get_page, set_page
from fedlead_agent_crewai.utils.smart_click import smart_click

class FindLatestSubmissionInput(BaseModel):
    submitter_name: str = Field(..., description="Submitter name to search (e.g. 'crdc.cw4')")

class FindLatestSubmissionTool(BaseTool):
    name: str = "review_latest_submission"
    description: str = "Searches for the submitter and clicks the first 'Review' button for their latest submission."
    args_schema: Type[BaseModel] = FindLatestSubmissionInput

    def _run(self, submitter_name: str) -> str:
        try:
            page = get_page()
            page.wait_for_timeout(1000)

            # Type submitter name into the search input
            search_box = page.query_selector("input[placeholder*='Minimum 3 characters required']")
            if not search_box:
                return "Could not find the Submitter Name search input box."

            search_box.fill(submitter_name)
            page.keyboard.press("Enter")
            page.wait_for_timeout(2000)

            # Find the first "Review" button in the filtered list
            review_buttons = page.query_selector_all("table tbody tr button:has-text('Review')")
            if review_buttons:
                review_buttons[0].click()
                page.wait_for_timeout(1500)
                set_page(page)
                return f"Clicked Review for latest submission from {submitter_name}. URL: {page.url}"
            else:
                return f"No Review button found for {submitter_name}."

        except Exception as e:
            return f"ReviewLatestSubmissionTool error: {str(e)}"
