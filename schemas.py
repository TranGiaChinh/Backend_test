from pydantic import BaseModel
from typing import Optional, List

# --- USER ---
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "full_name": user["full_name"]
    }

# --- PROJECT ---
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

def project_helper(project) -> dict:
    return {
        "id": str(project["_id"]),
        "name": project["name"],
        "description": project.get("description")
    }

# --- TASK ---
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    project_id: str  
    tags: List[str] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

def task_helper(task) -> dict:
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task.get("description"),
        "status": task["status"],
        "project_id": task["project_id"],
        "tags": task.get("tags", []),
        "created_at": task.get("created_at")
    }

# --- COMMENT ---
class CommentCreate(BaseModel):
    task_id: str
    user_id: str
    content: str

def comment_helper(comment) -> dict:
    return {
        "id": str(comment["_id"]),
        "task_id": comment["task_id"],
        "user_id": comment["user_id"],
        "content": comment["content"],
        "created_at": comment.get("created_at")
    }

# --- LOG ---
def log_helper(log) -> dict:
    return {
        "id": str(log["_id"]),
        "event_type": log.get("event_type"),
        "target_entity": log.get("target_entity"),
        "entity_id": log.get("entity_id"),
        "created_at": log.get("created_at")
    }