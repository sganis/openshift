import os
import time
import json
import redis
from pymongo import MongoClient

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_QUEUE = "log_queue"

# MongoDB Configuration
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")  # Use the service name in Kubernetes/OpenShift
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "logs_db")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "logs")
MONGO_USER = os.getenv("MONGO_USER", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")

# Redis client
redis_client = redis.StrictRedis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    db=REDIS_DB, 
    password=REDIS_PASSWORD if REDIS_PASSWORD else None, 
    decode_responses=True
)

# MongoDB client with authentication
mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}?authSource=admin"
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client[MONGO_DB_NAME]
mongo_collection = mongo_db[MONGO_COLLECTION_NAME]

def save_log_to_mongo(log_entry):
    """Save log to MongoDB"""
    log_entry["timestamp"] = time.time()  # Add timestamp for sorting
    mongo_collection.insert_one(log_entry)
    print(f"✅ Log saved to MongoDB: {log_entry}")

def process_log(log_entry):
    """Process log message and save to MongoDB"""
    print(f"📩 Processing log: {log_entry}")
    save_log_to_mongo(log_entry)

def start_worker():
    """Continuously pull messages from Redis and process them"""
    print("👷 Worker started. Listening for messages in Redis...")

    while True:
        log_entry = redis_client.lpop(REDIS_QUEUE)

        if log_entry:
            log_data = json.loads(log_entry)
            process_log(log_data)
        else:
            print('🔴 No messages in Redis. Waiting...')
            time.sleep(1)  # Sleep for a second if no messages

if __name__ == "__main__":
    start_worker()
