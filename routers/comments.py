from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from database import comments_collection
from schemas import CommentCreate, comment_helper

router = APIRouter(tags=["Comments"])

@router.post("/comments", status_code=201)
async def create_comment(comment: CommentCreate):
    if not ObjectId.is_valid(comment.task_id) or not ObjectId.is_valid(comment.user_id):
        raise HTTPException(status_code=400, detail="ID không hợp lệ")

    comment_dict = comment.dict()
    comment_dict["created_at"] = datetime.now()
    
    result = await comments_collection.insert_one(comment_dict)
    new_comment = await comments_collection.find_one({"_id": result.inserted_id})
    return comment_helper(new_comment)

@router.get("/tasks/{task_id}/comments")
async def get_task_comments(task_id: str):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Task ID không hợp lệ")
        
    cursor = comments_collection.find({"task_id": task_id}).sort("created_at", -1)
    comments = await cursor.to_list(length=100)
    return [comment_helper(c) for c in comments]