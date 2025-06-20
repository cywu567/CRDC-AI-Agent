### **CRDC Datahub Submission Agent**

This custom agent automates testing of the CRDC Datahub API's QA process by creating data submissions with metadata. It uses the 'CodeAgent' from the 'smolagents' library with specialized tools for each task. The agent runs on AWS Bedrock leveraging the Claude-Haiku model.

## Setup
1. **Create and activate a Python virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Export your submitter token manually in shell**

    ```bash
   export SUBMITTER_TOKEN = "your_submitter_api_token_here"
   ```

4. Adjust file paths in the code to match your local setup

## Usage
Run CustomAgent.py to:

- Generate unique submission names
- Prepare and upload metadata files
- Create and update submission batches
