### **CRDC Datahub Submission Request Approval Agent**

This project develops a custom AI agent to automate the approval process of CRDC Datahub submission requests using a Federal Lead account. Built with Python and Playwright for browser automation, this agent locates pending submissions, evaluates their content, and approves them by simulating actions taken by a Federal Lead reviewer.

Designed for seamless execution in QA environments, the agent supports remote deployment and leverages CrewAI for modular orchestration. Operating independently from the submission agent, it focuses on the review and approval stage of the submission lifecycle. Optional integration with vector databases allows for decision logging and refinement via AI feedback loops.


## Setup
1. **Create and activate a Python virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Export your submitter token manually in shell**

    ```bash
   export SUBMITTER_TOKEN = "your_submitter_api_token_here"
   ```

4. Adjust file paths in the code to match your local setup
5. To run, cd into the main folder, and run

```bash
PYTHONPATH=src python src/sragent_crewai/main.py   
```    

## Usage
Run CustomAgent.py to:

- Generate unique submission names
- Prepare and upload metadata files
- Create and update submission batches