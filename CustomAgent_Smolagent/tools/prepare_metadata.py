from smolagents.tools import Tool
from typing import List, Dict
from typing import Type
from pydantic import BaseModel, Field
from db.db import log_feedback, get_file_id, insert_file
from datetime import datetime
import time
import os
import shutil
    
class PrepareAllMetadataInput(BaseModel):
    folder_path: str = Field(..., description="Path to the folder containing sample metadata files to prepare.")
    base_dir: str = Field(..., description="Base directory where the 'submissions' folder resides or will be created.")
    submission_name: str = Field(..., description="Unique submission name generated externally (e.g., 'sub_250618_111826').")
    

class PrepareAllMetadataTool(Tool):
    name = "prepare_all_sample_metadata"
    description = (
        "Copies all files from the specified folder into a new submission metadata folder, "
        "renames each file with a timestamp for uniqueness, and returns metadata information "
        "for each copied file."
    )
    input_model = PrepareAllMetadataInput
    output_type = "array"
    inputs = input_model.model_json_schema()["properties"]
    
    def forward(self, folder_path: str, base_dir: str, submission_name: str) -> List[Dict]:
        base_dir = os.path.normpath(base_dir)

        # Determine the root directory for submissions
        if os.path.basename(base_dir) == "submissions":
            submissions_root = base_dir
        elif os.path.basename(base_dir) == "CustomAgent_Smolagent":
            submissions_root = os.path.join(base_dir, "submissions")
        else:
            submissions_root = os.path.join(base_dir, "CustomAgent_Smolagent", "submissions")

        os.makedirs(submissions_root, exist_ok=True)

        # Use submission_name as folder name
        submission_folder = os.path.join(submissions_root, submission_name)
        os.makedirs(submission_folder, exist_ok=True)

        metadata_folder = os.path.join(submission_folder, "metadata")
        os.makedirs(metadata_folder, exist_ok=True)

        results = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                base_name = os.path.basename(file_path)
                new_file_name = f"{os.path.splitext(base_name)[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(base_name)[1]}"
                dest_path = os.path.join(metadata_folder, new_file_name)
                shutil.copy(file_path, dest_path)
                results.append({
                    "submission_folder": submission_folder,
                    "metadata_folder": metadata_folder,
                    "updated_file_path": dest_path,
                    "fileName": new_file_name,
                    "fullPath": dest_path,
                    "submission_id": f"{submission_name}_{int(time.time())}",
                    "created_at": datetime.now().isoformat(),
                })
                
                try:
                    file_id = insert_file(submission_name, new_file_name, dest_path)
                except Exception as e:
                    print(f"Warning: could not insert file record for {new_file_name}: {e}")
                    file_id = -1

                # Try to get real file_id and log feedback per file
                try:
                    file_id = get_file_id(submission_name, new_file_name)
                    log_feedback(
                        file_id=file_id,
                        source="system",
                        is_accepted=True,
                        comments="File copied and metadata prepared.",
                        tool="PrepareMetadata"
                    )
                except Exception as fe:
                    # File not found or DB error — fallback to dummy log or print warning
                    print(f"Warning: could not log feedback for file {new_file_name}: {fe}")


        return results