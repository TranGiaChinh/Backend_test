from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import users_collection, tasks_collection
from routers import users, projects, tasks, comments, logs

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Thiết lập Index lúc khởi động Server
    await users_collection.create_index("email", unique=True)
    await tasks_collection.create_index([("title", 1), ("project_id", 1)], unique=True)
    print("Đã thiết lập Unique Index (Data Consistency)")

    await tasks_collection.create_index([("project_id", 1), ("status", 1)])
    print("Đã thiết lập Compound Index (Performance Optimization)")
    
    yield
    print("Server đang tắt...")

# Khởi tạo App
app = FastAPI(title="Task Management API", lifespan=lifespan)

# Lắp ghép các Module (Routers) vào mạch chính
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(logs.router)