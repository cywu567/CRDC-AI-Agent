from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).parent
DB_PATH  = BASE_DIR / "feedback.db"
SCHEMA   = BASE_DIR / "feedback_schema.sql"

def connect():
    return sqlite3.connect(DB_PATH)

def init_schema():
    with connect() as conn, open(SCHEMA, "r") as ddl:
        conn.executescript(ddl.read())

def save_submission(submission_name: str, files: list[dict]) -> int:
    """
    Insert a row into `submissions` and its related file rows.
    `files` is a list of dicts with keys 'fileName' and 'fullPath'.
    Returns the new submission_id.
    """
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO submissions (submission_name) VALUES (?)",
            (submission_name,),
        )
        submission_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO files (submission_id, file_name, full_path) VALUES (?,?,?)",
            [(submission_id, f["fileName"], f["fullPath"]) for f in files],
        )
    return submission_id

def log_feedback(file_id: int, source: str, is_accepted: bool, comments: str, tool: str) -> None:
    """Insert a feedback record including tool and prompt_template."""
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO feedback (file_id, source, tool, is_accepted, comments)
            VALUES (?, ?, ?, ?, ?)
            """,
            (file_id, source, tool, is_accepted, comments),
        )
        
def get_file_id(submission_name: str, file_name: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT files.id
        FROM files
        JOIN submissions ON files.submission_id = submissions.id
        WHERE submissions.submission_name = ? AND files.file_name = ?
    """, (submission_name, file_name))
    
    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    else:
        raise ValueError(f"No file found for submission '{submission_name}' and file '{file_name}'")
    
def insert_file(submission_name: str, file_name: str, full_path: str) -> int:
    with connect() as conn:
        # Get submission id from submission_name
        cur = conn.execute("SELECT id FROM submissions WHERE submission_name = ?", (submission_name,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Submission name {submission_name} not found in database")
        submission_id = row[0]
        
        # Insert file record
        cur = conn.execute(
            "INSERT INTO files (submission_id, file_name, full_path) VALUES (?, ?, ?)",
            (submission_id, file_name, full_path)
        )
        return cur.lastrowid
    
    
def insert_submission(submission_name: str) -> int:
    """
    Insert a submission row with the given name and no files.
    Returns the submission_id.
    """
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO submissions (submission_name) VALUES (?)",
            (submission_name,)
        )
        return cur.lastrowid
    
    
def get_feedback_for_tool(tool: str, file_name: str | None = None) -> list[tuple[str, bool, str]]:
    """
    Returns a list of (source, is_accepted, comments) for a specific tool,
    optionally filtered by file name.
    """
    with connect() as conn:
        cursor = conn.cursor()
        
        if file_name:
            cursor.execute("""
                SELECT f.source, f.is_accepted, f.comments
                FROM feedback f
                JOIN files fi ON fi.id = f.file_id
                WHERE fi.file_name = ? AND f.tool = ?
            """, (file_name, tool))
        else:
            cursor.execute("""
                SELECT f.source, f.is_accepted, f.comments
                FROM feedback f
                WHERE f.tool = ?
            """, (tool,))
        
        return cursor.fetchall()

