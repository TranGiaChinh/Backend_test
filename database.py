import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient

# 1. Khai báo kết nối Database (MongoDB)
MONGO_URL = "mongodb://mongodb:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["task_management"]

# Các Collections
users_collection = db["users"]
projects_collection = db["projects"]
tasks_collection = db["tasks"]
comments_collection = db["comments"]
activity_logs_collection = db["activity_logs"]

# 2. Khai báo kết nối Redis
REDIS_URL = "redis://redis:6379"
redis_client = redis.from_url(REDIS_URL, decode_responses=True)