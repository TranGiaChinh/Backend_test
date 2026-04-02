import asyncio
import json
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient

# 1. Kết nối DB và Redis y hệt như main.py
MONGO_URL = "mongodb://mongodb:27017"
REDIS_URL = "redis://redis:6379"

async def main():
    # Kết nối MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["task_management"]
    activity_logs_collection = db["activity_logs"]
    
    # Kết nối Redis
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    pubsub = redis_client.pubsub()
    
    # 2. Đăng ký Lắng nghe (Subscribe) kênh 'task_events'
    await pubsub.subscribe("task_events")
    print("Background Worker đang chạy và lắng nghe sự kiện từ Redis...")

    # 3. Vòng lặp vô tận dể lắng nghe sự kiện
    async for message in pubsub.listen():
        if message["type"] == "message":
            # Khi có tín hiệu bắn tới, lấy dữ liệu ra
            event_data = json.loads(message["data"])
            action = event_data.get("action")
            task_id = event_data.get("task_id")
            
            print(f" Nhận được event: {action} cho Task ID: {task_id}")
            
            # Ghi lịch sử xuống MongoDB (Intermediate Requirement)
            log_entry = {
                "event_type": action,
                "target_entity": "task",
                "entity_id": task_id,
                "created_at": event_data.get("timestamp")
            }
            await activity_logs_collection.insert_one(log_entry)
            print("Đã ghi Log vào Database thành công!")

if __name__ == "__main__":
    # Khởi chạy Worker
    asyncio.run(main())