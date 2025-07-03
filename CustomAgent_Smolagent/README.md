### **CRDC Datahub Metadata Submission Agent**

This project develops a custom AI agent to automate the end-to-end CRDC metadata submission workflow using the CRDC Datahub API. Built with modular Python tools handling tasks like retrieving studies, generating submission names, preparing metadata, and managing file uploads, the system is designed for cloud-native execution on AWS Bedrock. This eliminates local dependencies and enables scalable, reliable remote operation with all CRDC API interactions and file handling performed entirely in the cloud to ensure high availability and performance.

A key feature is an integrated feedback loop that collects system and user feedback, stores it in a vector database, and allows the agent to learn from execution outcomes and adapt over time, transforming it from a static script into an intelligent, self-improving assistant. The frontend user interface for interacting with the agent and visualizing feedback will be built using LangChain. The orchestration and multi-agent workflow management leverage the Smolagent framework to efficiently coordinate tasks and tools.


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
