from fastapi import APIRouter, Query
from database import activity_logs_collection
from schemas import log_helper

router = APIRouter(prefix="/logs", tags=["Activity Log"])

@router.get("/")
async def get_activity_logs(limit: int = Query(50, ge=1, le=100)):
    cursor = activity_logs_collection.find().sort("created_at", -1).limit(limit)
    logs = await cursor.to_list(length=limit)
    return [log_helper(log) for log in logs]