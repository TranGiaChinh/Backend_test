from fastapi import APIRouter
from database import projects_collection
from schemas import ProjectCreate, ProjectResponse, project_helper

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate):
    project_dict = project.dict()
    result = await projects_collection.insert_one(project_dict)
    new_project = await projects_collection.find_one({"_id": result.inserted_id})
    return project_helper(new_project)