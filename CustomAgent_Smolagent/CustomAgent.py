from smolagents.models import AmazonBedrockServerModel
from smolagents.agents import CodeAgent
from tools.generate_submission_name import GenerateSubmissionNameTool
from tools.create_batch import CreateBatchTool
from tools.create_submission import CreateSubmissionTool
from tools.get_my_studies import GetMyStudiesTool
from tools.prepare_metadata import PrepareAllMetadataTool
from tools.update_batch import UpdateBatchTool
from tools.upload_file import UploadFileTool
import os

API_URL = "https://hub-qa.datacommons.cancer.gov/api/graphql"
SUBMIT_TOKEN = os.getenv("SUBMITTER_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {SUBMIT_TOKEN}",
    "Content-Type": "application/json"
}

model = AmazonBedrockServerModel(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    client_kwargs={"region_name":"us-east-1"},
    inferenceConfig={"maxTokens":2048}
)

agent = CodeAgent(
    model=model,
    tools=[CreateBatchTool(),
           CreateSubmissionTool(),
           GenerateSubmissionNameTool(),
           GetMyStudiesTool(),
           PrepareAllMetadataTool(),
           UpdateBatchTool(),
           UploadFileTool(),
    ],
    max_steps=1,
    additional_authorized_imports=['os', 'shutil', 'json', 'requests', 'time', 'datetime', 'pathlib']
)

print(agent.run(
    "Important: Whenever you receive an object with an identifier, always access the ID using the key '_id', not 'id'. "
    "1. Generate a unique submission name using the GenerateSubmissionNameTool. "
    "2. Use PrepareAllMetadataTool to prepare sample metadata for all files in the folder "
    "'/Users/celinewu/Desktop/ESI 2025/CRDC/inject3_metadata_batch2/'. Set the base directory to '/Users/celinewu/Desktop/ESI 2025/CRDC/CustomAgent_Smolagent'."
    "The tool will automatically create a submissions folder inside it if not present."
    "3. From the list returned, use the 'fileName' field as the file name string and 'fullPath' field as the full path for each file. "
    "4. Retrieve the latest study ID using GetMyStudiesTool and pick the most recent one. "
    "5. Create a submission in the 'CDS' data commons with intention 'New/Update', data type 'Metadata Only', and the generated submission name. "
    "Ensure that the submission ID is a valid string, not a list of file names"
))
#this is the prompt for full implemnetation
#print(agent.run(
#    "Important: Whenever you receive an object with an identifier, always access the ID using the key '_id', not 'id'. "
#    "1. Generate a unique submission name using the GenerateSubmissionNameTool. "
#    "2. Use PrepareAllMetadataTool to prepare sample metadata for all files in the folder "
#    "'/Users/celinewu/Desktop/ESI 2025/CRDC/inject3_metadata_batch2/'. Set the base directory to '/Users/celinewu/Desktop/ESI 2025/CRDC/CustomAgent_Smolagent'."
#    "The tool will automatically create a submissions folder inside it if not present."
#    "3. From the list returned, use the 'fileName' field as the file name string and 'fullPath' field as the full path for each file. "
#    "4. Retrieve the latest study ID using GetMyStudiesTool and pick the most recent one. "
#    "5. Create a submission in the 'CDS' data commons with intention 'New/Update', data type 'Metadata Only', and the generated submission name. "
#    "Ensure that the submission ID is a valid string, not a list of file names"
#    "6. Use the submission ID to create a batch with batch_type='metadata' using the list of file names (strings) from step 3. "
#    "7. For each file, use its fileName to get the presigned URL and upload the file located at fullPath to that URL. "
#    "   Do not guess or construct file paths; always use the 'fullPath' directly. "
#    "8. Update the batch using UpdateBatchTool with a list of file name strings only (e.g., ['file1.tsv', 'file2.tsv']). "
#    "Return all relevant submission and batch IDs and status updates at the end."
#))