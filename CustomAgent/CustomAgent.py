import requests
import uuid
import os
import shutil
import json
import time
from datetime import datetime
import mimetypes
from smolagents.models import AmazonBedrockServerModel
from smolagents.agents import CodeAgent
from smolagents.tools import tool

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


@tool
def generate_submission_name() -> str:
    """
    Generate a unique submission name that starts with 'sub_' followed by the current date and time
    in the format YYMMDD_HHMMSS. This ensures the submission name is unique and does not exceed
    25 characters, which is required by the submission API.

    Returns:
        str: A submission name string like 'sub_250618_111826'.
    """
    from datetime import datetime
    return "sub_" + datetime.now().strftime("%y%m%d_%H%M%S")


@tool
def prepare_sample_metadata(sample_path: str, base_dir: str, submission_name: str) -> dict:
    """
    Prepares sample metadata by creating a new submission folder inside a 'submissions' directory,
    using the provided submission_name for the folder and submission_id prefix.

    Args:
        sample_path (str): Path to the sample metadata template file (JSON format).
        base_dir (str): Base directory where the 'submissions' folder resides or will be created.
        submission_name (str): Unique submission name generated externally (e.g., 'sub_250618_111826').

    Returns:
        dict: Contains paths for 'submission_folder', 'metadata_folder', and 'updated_file_path'.
    """
    import os
    import shutil
    base_dir = os.path.normpath(base_dir)
    if os.path.basename(base_dir) == "submissions":
        submissions_root = base_dir
    elif os.path.basename(base_dir) == "CustomAgent":
        submissions_root = os.path.join(base_dir, "submissions")
    else:
        submissions_root = os.path.join(base_dir, "CustomAgent", "submissions")
    os.makedirs(submissions_root, exist_ok=True)

    # Use submission_name as folder name
    submission_folder = os.path.join(submissions_root, submission_name)
    os.makedirs(submission_folder, exist_ok=True)

    metadata_folder = os.path.join(submission_folder, "metadata")
    os.makedirs(metadata_folder, exist_ok=True)

    base_name = os.path.basename(sample_path)
    # Keep original file extension but rename with timestamp for uniqueness
    new_file_name = f"{os.path.splitext(base_name)[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(base_name)[1]}"
    dest_path = os.path.join(metadata_folder, new_file_name)

    shutil.copy(sample_path, dest_path)

    # Use submission_name as prefix for submission_id to keep IDs consistent
    unique_fields = {
        "submission_id": f"{submission_name}_{int(time.time())}",
        "created_at": datetime.now().isoformat()
    }

    return {
        "submission_folder": submission_folder,
        "metadata_folder": metadata_folder,
        "updated_file_path": dest_path
    }


@tool
def prepare_all_sample_metadata_in_folder(folder_path: str, base_dir: str, submission_name: str) -> list[dict]:
    """
    Copies all files from the specified folder into a new submission metadata folder,
    renames each file with a timestamp for uniqueness, and returns metadata information 
    for each copied file.

    For each file, the returned dictionary contains:
      - 'submission_folder' (str): Path to the submission folder created.
      - 'metadata_folder' (str): Path to the metadata folder inside the submission folder.
      - 'updated_file_path' (str): Full path to the copied and renamed metadata file.
      - 'fileName' (str): Base name of the copied file (extracted from updated_file_path).
      - 'fullPath' (str): Alias for 'updated_file_path'.

    Args:
        folder_path (str): Path to the folder containing sample metadata files to prepare.
        base_dir (str): Base directory where the 'submissions' folder is or will be created.
        submission_name (str): Unique submission name used to create folders and prefix files.

    Returns:
        list of dict: List of metadata dictionaries for each copied file with details as above.
    """
    import os
    results = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            md = prepare_sample_metadata(file_path, base_dir, submission_name)
            base = os.path.basename(md["updated_file_path"])
            md["fileName"] = base
            md["fullPath"] = md["updated_file_path"]
            results.append(md)
    return results


@tool
def get_my_studies() -> list[str]:
    """
    Returns a list of study IDs the user has access to.

    Returns:
        list of str: Study IDs belonging to the user.
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


@tool
def create_submission(study_id: str, data_commons: str, name: str, intention: str, data_type: str) -> dict:
    """
    Creates a submission request in the data commons system.

    Args:
        study_id (str): The ID of the study to submit data to.
        data_commons (str): The name of the data commons (e.g., 'ICDC').
        name (str): Name for the submission.
        intention (str): Submission intention ('New/Update' or 'Delete').
        data_type (str): Type of submission ('Metadata Only' or 'Metadata and Data Files').

    Returns:
        dict: A dictionary containing the submission ID, status, and creation time.
    """
    import time
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
    return data["data"]["createSubmission"]


@tool
def create_batch(submission_id: str, file_names: list[str], batch_type: str = "metadata") -> dict:
    """
    Creates a batch in the submission to group files for upload, returning presigned URLs.

    Args:
        submission_id (str): ID of the submission to associate the batch with.
        file_names (list of str): List of file names to include in the batch.
        batch_type (str, optional): Type of batch. Defaults to 'metadata_template'.

    Returns:
        dict: Batch details including batch ID and presigned upload URLs.
    """
    mutation = """
    mutation createBatch($submissionID: ID!, $type: String, $files: [String!]!) {
      createBatch(submissionID: $submissionID, type: $type, files: $files) {
        _id
        submissionID
        bucketName
        filePrefix
        type
        fileCount
        files {
          fileName
          signedURL
        }
        status
        createdAt
        updatedAt
      }
    }
    """
    variables = {
        "submissionID": submission_id,
        "type": batch_type,
        "files": file_names,
    }
    res = requests.post(API_URL, json={"query": mutation, "variables": variables}, headers=HEADERS)
    if not res.ok:
        raise Exception(f"Error creating batch: {res.text}")
    data = res.json()
    if "errors" in data:
        raise Exception(f"GraphQL errors: {data['errors']}")
    return data["data"]["createBatch"]

@tool
def extract_presigned_url(batch: dict, file_name: str) -> str:
    """
    Extracts the signed URL for a specific file name from the batch object.

    Args:
        batch (dict): The batch object returned from `create_batch`.
        file_name (str): The name of the file to find.

    Returns:
        str: The signed URL for the file.
    """
    for file_info in batch["files"]:
        if file_info["fileName"] == file_name:
            return file_info["signedURL"]
    raise ValueError(f"File {file_name} not found in batch.")

@tool
def upload_file_to_presigned_url(file_path: str, presigned_url: str) -> str:
    """
    Uploads a local file to a presigned URL via HTTP PUT.

    Args:
        file_path (str): Path to the local file to upload.
        presigned_url (str): Presigned URL to upload the file to.

    Returns:
        str: Confirmation message upon successful upload.

    Raises:
        Exception: If upload fails.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    headers = {
        "Content-Type": mime_type
    }
    with open(file_path, "rb") as f:
        file_data = f.read()
    res = requests.put(presigned_url, data=file_data, headers=headers)
    if not res.ok:
        raise Exception(f"Error uploading file {file_path}: {res.text}")
    return f"Uploaded {file_path}"


@tool
def update_batch(batch_id: str, file_names: list[str]) -> dict:
    """
    Updates the batch after file uploads with required UploadResult fields.

    Args:
        batch_id (str): The ID of the batch to update.
        file_names (list of str): List of uploaded file names to mark as succeeded.

    Returns:
        dict: The updated batch information as returned by the GraphQL API.

    Raises:
        Exception: If the HTTP request fails or the GraphQL API returns errors.
    """
    mutation = """
    mutation updateBatch($batchID: ID!, $files: [UploadResult]!) {
      updateBatch(batchID: $batchID, files: $files) {
        _id
        submissionID
        type
        fileCount
        files {
          filePrefix
          fileName
          size
          status
          errors
          createdAt
          updatedAt
        }
        status
        createdAt
        updatedAt
      }
    }
    """
    files_payload = [{"fileName": f, "succeeded": True, "errors": None} for f in file_names]

    variables = {
        "batchID": batch_id,
        "files": files_payload
    }
    res = requests.post(API_URL, json={"query": mutation, "variables": variables}, headers=HEADERS)
    if not res.ok:
        raise Exception(f"Error updating batch: {res.text}")
    data = res.json()
    if "errors" in data:
        raise Exception(f"GraphQL errors: {data['errors']}")
    return data["data"]["updateBatch"]



@tool
def list_batches(submission_id: str, first: int = 10, offset: int = 0) -> list[dict]:
    """
    Retrieves a paginated list of batches associated with a submission.

    Args:
        submission_id (str): ID of the submission to query batches for.
        first (int, optional): Number of batches to retrieve. Defaults to 10.
        offset (int, optional): Pagination offset. Defaults to 0.

    Returns:
        list of dict: List of batches with their details (ID, status, timestamps, files).
    """
    query = """
    query ListBatches($submissionID: ID!, $first: Int, $offset: Int) {
      listBatches(submissionID: $submissionID, first: $first, offset: $offset) {
        batches {
          _id
          status
          createdAt
          updatedAt
          files {
            fileName
            status
            errors
          }
        }
      }
    }
    """
    variables = {"submissionID": submission_id, "first": first, "offset": offset}
    res = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    if not res.ok:
        raise Exception(f"Error listing batches: {res.text}")
    data = res.json()
    if "errors" in data:
        raise Exception(f"GraphQL errors: {data['errors']}")
    return data["data"]["listBatches"]["batches"]


agent = CodeAgent(
    model=model,
    tools=[get_my_studies,
       create_batch,
       upload_file_to_presigned_url,
       update_batch,
       list_batches,
       extract_presigned_url,
       prepare_sample_metadata,
       create_submission,
       generate_submission_name,
       prepare_all_sample_metadata_in_folder
],
    max_steps=5,
    additional_authorized_imports=['os', 'shutil', 'json', 'requests', 'time', 'datetime', 'uuid', 'pathlib', 'posixpath']
)


print(agent.run(
    "Important: Whenever you receive an object with an identifier, always access the ID using the key '_id', not 'id'. "
    "1. Generate a unique submission name using the generate_submission_name tool. "
    "2. Use prepare_all_sample_metadata_in_folder to prepare sample metadata for all files in the folder "
    "'/Users/celinewu/Desktop/ESI 2025/CRDC/inject3_metadata_batch2/'. Set the base directory to '/Users/celinewu/Desktop/ESI 2025/CRDC/CustomAgent'."
    "The tool will automatically create a submissions folder inside it if not present."
    "3. From the list returned, use the 'fileName' field as the file name string and 'fullPath' field as the full path for each file. "
    "4. Retrieve the latest study ID using get_my_studies and pick the most recent one. "
    "5. Create a submission in the 'CDS' data commons with intention 'New/Update', data type 'Metadata Only', and the generated submission name. "
    "6. Use the submission ID to create a batch with batch_type='metadata' using the list of file names (strings) from step 3. "
    "7. For each file, use its fileName to get the presigned URL and upload the file located at fullPath to that URL. "
    "   Do not guess or construct file paths; always use the 'fullPath' directly. "
    "8. Update the batch using update_batch with a list of file name strings only (e.g., ['file1.tsv', 'file2.tsv']). "
    "Return all relevant submission and batch IDs and status updates at the end."
))