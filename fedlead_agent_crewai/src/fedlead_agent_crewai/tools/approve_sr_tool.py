from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from fedlead_agent_crewai.utils.session_manager import get_page

class ApproveSRToolInput(BaseModel):
    pass

class ApproveSRTool(BaseTool):
    name: str = "approve_sr_tool"
    description: str = "Approves the submission request"
    args_schema: Type[BaseModel] = ApproveSRToolInput

    def _run(self) -> str:
        try:
            page = get_page()
            all_results = []

            while True:
                next_button = page.query_selector("button:has-text('Next')")
                if next_button and next_button.is_enabled():
                    next_button.click()
                    page.wait_for_timeout(1000)
                else:
                    break
            
            approve_button = page.query_selector("button:has-text('Approve')")
            approve_button.click()
            page.wait_for_timeout(1000)
            
            reason_box = page.query_selector('div[data-testid="review-comment"] textarea:not([aria-hidden="true"])')
            if not reason_box:
                return "Could not find the text box to give a reason for approval."
            reason_box.fill("testing")

            approve_button = page.query_selector("button:has-text('Confirm to Approve')")
            approve_button.click()
            return "Submission request approved"
        
        except Exception as e:
            return f"ApproveSRTool error: {str(e)}"
