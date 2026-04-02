from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from typing import Optional
from datetime import datetime
import json
from database import tasks_collection, projects_collection, redis_client
from schemas import TaskCreate, TaskUpdate, task_helper

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", status_code=201)
async def create_task(task: TaskCreate):
    if not ObjectId.is_valid(task.project_id):
        raise HTTPException(status_code=400, detail="Project ID không hợp lệ")
        
    project = await projects_collection.find_one({"_id": ObjectId(task.project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")

    task_dict = task.dict()
    task_dict["created_at"] = datetime.now()
    
    result = await tasks_collection.insert_one(task_dict)
    new_task = await tasks_collection.find_one({"_id": result.inserted_id})
    
    event_data = {
        "action": "task.created",
        "task_id": str(result.inserted_id),
        "timestamp": str(datetime.now())
    }
    await redis_client.publish("task_events", json.dumps(event_data))
    return task_helper(new_task)

@router.get("/")
async def get_tasks(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    sort: Optional[str] = Query("created_at"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = {}
    if project_id: query["project_id"] = project_id
    if status: query["status"] = status
    skip = (page - 1) * limit
    
    cursor = tasks_collection.find(query).sort(sort, -1).skip(skip).limit(limit)
    tasks = await cursor.to_list(length=limit)
    return {"page": page, "limit": limit, "data": [task_helper(t) for t in tasks]}

@router.get("/{task_id}")
async def get_task_detail(task_id: str):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Task ID không hợp lệ")

    cache_key = f"task_detail:{task_id}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        print("⚡ Lấy dữ liệu siêu tốc từ Redis Cache!")
        return json.loads(cached_data)

    print(" Lấy dữ liệu từ MongoDB...")
    task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Không tìm thấy Task")

    task_data = task_helper(task)
    await redis_client.set(cache_key, json.dumps(task_data), ex=60)
    return task_data

@router.patch("/{task_id}")
async def update_task(task_id: str, task_data: TaskUpdate):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Task ID không hợp lệ")

    update_data = {k: v for k, v in task_data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu cập nhật")

    result = await tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy Task")

    updated_task = await tasks_collection.find_one({"_id": ObjectId(task_id)})
    await redis_client.delete(f"task_detail:{task_id}")
    
    event_data = {
        "action": "task.updated",
        "task_id": task_id,
        "timestamp": str(datetime.now())
    }
    await redis_client.publish("task_events", json.dumps(event_data))
    return task_helper(updated_task)

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Task ID không hợp lệ")
        
    result = await tasks_collection.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy Task")
        
    await redis_client.delete(f"task_detail:{task_id}")
    event_data = {
        "action": "task.deleted",
        "task_id": task_id,
        "timestamp": str(datetime.now())
    }
    await redis_client.publish("task_events", json.dumps(event_data))
    return {"message": "Đã xóa thành công"}