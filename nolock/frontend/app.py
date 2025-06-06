import os
import time
import json
from flask import Flask, jsonify, request
import redis
from pymongo import MongoClient
import requests
from jose import jwt, JWTError, ExpiredSignatureError

app = Flask(__name__)

# Cache token in memory
_cached_token = None


# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_QUEUE = "log_queue"

HOST_KEY = "last_hostname"
VERSION_KEY = "app_version"

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")  # MongoDB service name in Kubernetes/OpenShift
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "logs_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "logs")
MONGO_USER = os.getenv("MONGO_USER", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", None)

print(f"REDIS_HOST: {REDIS_HOST}")
print(f"REDIS_PORT: {REDIS_PORT}")
print(f"REDIS_DB: {REDIS_DB}")
print(f"REDIS_PASSWORD: {REDIS_PASSWORD}")
print(f"MONGO_HOST: {MONGO_HOST}")
print(f"MONGO_PORT: {MONGO_PORT}")
print(f"MONGO_DB: {MONGO_DB}")
print(f"MONGO_COLLECTION: {MONGO_COLLECTION}")
print(f"MONGO_USER: {MONGO_USER}")
print(f"MONGO_PASSWORD: {MONGO_PASSWORD}")

# Redis client
redis_client = redis.StrictRedis(
    host=REDIS_HOST, 
    password=REDIS_PASSWORD if REDIS_PASSWORD else None,
    port=REDIS_PORT,
    db=REDIS_DB, 
    decode_responses=True
)

# MongoDB client
mongo_client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/")
mongo_db = mongo_client[MONGO_DB]
mongo_collection = mongo_db[MONGO_COLLECTION]


# Config
JWT_SECRET = os.environ.get("JWT_SECRET", "your-dev-secret")
JWT_ISSUER = "api-a"
JWT_AUDIENCE = "api-b"
JWT_EXP_SECONDS = 30  # Token is valid for 3 seconds
EXTERNAL_API_URL = "http://external:5001"  # Replace path as needed

def generate_jwt():
    now = int(time.time())
    payload = {
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + JWT_EXP_SECONDS,
        "scope": "internal-call"
    }
    token = jwt.encode(claims=payload, key=JWT_SECRET, algorithm="HS256")
    return token

def get_valid_token():
    global _cached_token
    if _cached_token:
        try:
            jwt.decode(_cached_token, JWT_SECRET, algorithms=["HS256"], audience=JWT_AUDIENCE)
            return _cached_token
        except ExpiredSignatureError:
            print("⚠️ Token expired, regenerating.")
        except JWTError as e:
            print(f"⚠️ Invalid token: {e}")
    _cached_token = generate_jwt()
    return _cached_token

@app.route("/external", methods=["GET"])
def call_external_api():
    token = get_valid_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(f'{EXTERNAL_API_URL}/data', headers=headers) 

        if response.status_code == 401:
            print("🔄 Auth error, possibly expired token. Retrying...")
            # Try once more with a fresh token
            _cached_token = generate_jwt()
            headers["Authorization"] = f"Bearer {_cached_token}"
            response = requests.get(EXTERNAL_API_URL, headers=headers)
            
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(e)
        return {"error": str(e)}


@app.route("/")
def index():
    # Get current hostname
    hostname = os.getenv("HOSTNAME", "Unknown")

    # Get last hostname and version from Redis
    last_hostname = redis_client.get(HOST_KEY)
    version = redis_client.get(VERSION_KEY)

    if version is None:
        version = 1
        redis_client.set(VERSION_KEY, version)
    else:
        version = int(version)

    # Compare and update version if hostname changed
    if last_hostname is None or last_hostname != hostname:
        version += 1
        redis_client.set(VERSION_KEY, version)
        redis_client.set(HOST_KEY, hostname)

    hits = redis_client.incr("hits")
    
    # Get the length of the Redis queue
    queue_length = redis_client.llen(REDIS_QUEUE)

    log_entry = {
        "hostname": hostname,
        "hits": hits
    }

    redis_client.rpush(REDIS_QUEUE, json.dumps(log_entry))

    external_data = call_external_api()

    return jsonify({
        "status": "queued", 
        "version": version, 
        "queue_length": queue_length,
        "message": log_entry,
        "external_data": external_data
    }), 200


@app.route("/logs/<int:n>", methods=["GET"])
def get_logs(n):
    """Retrieve the last N logs from MongoDB."""
    hits = redis_client.incr("hits")
    try:
        logs = list(mongo_collection.find().sort("timestamp", -1).limit(n))

        # Convert MongoDB ObjectId to string
        for log in logs:
            log["_id"] = str(log["_id"])

        return jsonify({"logs": logs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
