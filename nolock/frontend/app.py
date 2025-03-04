from flask import Flask, jsonify
import requests
import os
import hashlib
import redis

app = Flask(__name__)

# Environment variables
SERVICE_URL = os.getenv("SERVICE_URL", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASS = int(os.getenv("REDIS_PASS", ))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
print(f"SERVICE_URL: {SERVICE_URL}")
print(f"DB_PASSWORD: {DB_PASSWORD}")
print(f"REDIS_HOST: {REDIS_HOST}")
print(f"REDIS_PORT: {REDIS_PORT}")
print(f"REDIS_DB: {REDIS_DB}")
print(f"REDIS_PASS: {REDIS_PASS}")

# Redis client for distributed tracking
redis_client = redis.StrictRedis(
    host=REDIS_HOST, password=REDIS_PASS,
    port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
PASSWORD_FAILED_KEY = "password_failed_hash"

def get_password_hash(password):
    """Generate a simple hash for the current password."""
    return hashlib.sha256(password.encode()).hexdigest()

def has_password_failed():
    """Check if the last password attempt failed and if the stored password hash matches the current password."""
    stored_hash = redis_client.get(PASSWORD_FAILED_KEY)
    return stored_hash == get_password_hash(DB_PASSWORD) if stored_hash else False

def mark_password_as_failed():
    """Mark the current password as failed to prevent unnecessary retries."""
    redis_client.set(PASSWORD_FAILED_KEY, get_password_hash(DB_PASSWORD))

def reset_password_failure():
    """Clear the failure status when a valid password is used."""
    redis_client.delete(PASSWORD_FAILED_KEY)

@app.route("/")
def index():
    hostname = os.getenv("HOSTNAME", "Unknown")
    logs = []  # Collect logs in an array to return in the JSON response

    if has_password_failed():
        logs.append(f"Skipping password retry on {hostname}, last attempt failed with the same password.")
        return jsonify({
            "hostname": hostname,
            "error": "Unauthorized - Password is incorrect, but account is not locked",
            "logs": logs
        }), 401

    logs.append(f"Trying password on {hostname}.")
    headers = {"Authorization": f"Bearer {DB_PASSWORD}"}
    response = requests.get(f"{SERVICE_URL}/data", headers=headers)

    if response.status_code == 200:
        logs.append(f"Password worked on {hostname}. Resetting failure status.")
        reset_password_failure()
        return jsonify({
            "hostname": hostname,
            "response": response.json(),
            "logs": logs
        })

    logs.append(f"Password failed on {hostname}. Marking it as failed.")
    mark_password_as_failed()

    return jsonify({
        "hostname": hostname,
        "error": "Unauthorized - Password is incorrect, but account is not locked",
        "logs": logs
    }), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
