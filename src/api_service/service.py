import json
from fastapi import FastAPI, Depends, HTTPException
# from pydantic import BaseModel
from pathlib import Path
from typing import List
from starlette.middleware.cors import CORSMiddleware
from routers import llm_chat_routers
from pydantic import BaseModel
from routers.llm_chat_routers import verify_auth_key

# Setup FastAPI app
app = FastAPI(title="API Server", description="API Server", version="v1")

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


DATA_PATH = Path("data/notes.json")


class Note(BaseModel):
    type: str
    datetime: str
    chat_id: str
    content: str


@app.post("/save-notes", summary="Save notes", description="Saves a list of notes to the server.")
async def save_notes(
    notes: List[Note],
    _: str = Depends(verify_auth_key)  # Authorization dependency
):
    """
    Saves notes received from the frontend to a JSON file, appending only non-duplicate notes.


    Args:
        notes: List of notes received from the frontend.
        _: Authorization token (validated by verify_auth_key).


    Returns:
        A success message or raises an HTTPException for errors.
    """
    # Ensure the data/ directory exists
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Load existing notes from the file if it exists
    existing_notes = []
    if DATA_PATH.exists():
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                existing_notes = json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Corrupted notes file.")

    # Filter out duplicates
    new_notes = []
    for note in notes:
        if note.model_dump() not in existing_notes:
            new_notes.append(note.model_dump())

    # Append new notes to the existing ones
    all_notes = existing_notes + new_notes

    # Save back to the JSON file
    try:
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(all_notes, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save notes: {e}")

    return {"message": f"{len(new_notes)} new notes saved successfully."}

DATA_PATH = Path("data/notes.json")


@app.get("/get-notes", summary="Retrieve all notes", description="Fetches all notes stored in the JSON file.")
async def get_notes():
    """
    Fetches all notes stored in the JSON file.

    Returns:
        A list of notes or raises an HTTPException if the file is missing or corrupted.
    """
    if not DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Notes file not found.")

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            notes = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Corrupted notes file.")

    return {"notes": notes}


class authRequest(BaseModel):
    password: str


class authKey(BaseModel):
    key: str


# Mock password validation function
def validate_password(password):
    return password == "cheese"


@app.post("/login", response_model=authKey)
async def chat_query(request: authRequest):
    """
    Validates user password and returns auth key
    """
    user_password = request.password.strip()
    if not validate_password(user_password):
        # Raise a 401 Unauthorized error if the password is invalid
        raise HTTPException(status_code=401, detail="Invalid password")

    # Return an auth key for successful login
    return {"key": "parmesan"}


@app.get("/test")
async def get_index():
    return {"message": "also testing"}

# Additional routers here
app.include_router(llm_chat_routers.router, prefix="/llm", tags=["LLM Chat"])
