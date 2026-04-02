from fastapi import FastAPI ,Request, HTTPException, Depends
from contextlib import asynccontextmanager
from database import users_collection, tasks_collection, redis_client
from routers import users, projects, tasks, comments, logs

# ==========================================
# CƠ CHẾ RATE LIMITING BẰNG REDIS
# ==========================================
async def rate_limiter(request: Request):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    # Tăng biến đếm số lần gọi API của IP này
    request_count = await redis_client.incr(key)
    
    # Nếu là lần gọi đầu tiên, khởi tạo đồng hồ đếm ngược 60 giây (1 phút)
    if request_count == 1:
        await redis_client.expire(key, 60)
        
    # Nếu quá 10 lần / phút -> Chặn ngay lập tức
    if request_count > 10:
        raise HTTPException(
            status_code=429, 
            detail="Quá nhiều request (Rate Limit Exceeded). Vui lòng thử lại sau 1 phút!"
        )


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
app = FastAPI(title="Task Management API", lifespan=lifespan,dependencies=[Depends(rate_limiter)])

# Lắp ghép các Module (Routers) vào mạch chính
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(logs.router)