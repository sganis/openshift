from flask import Flask, request, jsonify
import os
import time
from dotenv import load_dotenv

# Load .env file from the mounted volume
load_dotenv("/app/volume/.env.service")

app = Flask(__name__)

# Environment variables
SERVICE_PASSWORD = os.getenv("DB_PASSWORD", "")

# Dictionary to track failed attempts: {client_ip: {"count": int, "lock_time": float}}
failed_attempts = {}

# Constants
MAX_ATTEMPTS = 3
LOCKOUT_TIME = 60  # 1 minute

@app.route("/data", methods=["GET"])
def get_data():
    client_ip = request.remote_addr
    auth_header = request.headers.get("Authorization")

    # Check if client is locked
    if client_ip in failed_attempts:
        attempts = failed_attempts[client_ip]
        if attempts["count"] >= MAX_ATTEMPTS and time.time() - attempts["lock_time"] < LOCKOUT_TIME:
            return jsonify({
                "error": "Account locked. Try again later.",
                'failed attempts': failed_attempts[client_ip]["count"],
                'lock time remaining': LOCKOUT_TIME - (time.time() - attempts["lock_time"]),    
            }), 403
        elif time.time() - attempts["lock_time"] >= LOCKOUT_TIME:
            # Reset lock after time expires
            failed_attempts[client_ip] = {"count": 0, "lock_time": 0}

    # Validate password
    if not auth_header or auth_header.split(" ")[-1] != SERVICE_PASSWORD:
        failed_attempts[client_ip] = failed_attempts.get(client_ip, {"count": 0, "lock_time": 0})
        failed_attempts[client_ip]["count"] += 1
        failed_attempts[client_ip]["lock_time"] = time.time()
        
        if failed_attempts[client_ip]["count"] >= MAX_ATTEMPTS:
            return jsonify({
                "error": "Account locked due to multiple failed attempts.",
                'failed attempts': failed_attempts[client_ip]["count"],
                'lock time remaining': LOCKOUT_TIME - (time.time() - failed_attempts[client_ip]["lock_time"]),
            }), 403
        else:
            return jsonify({
                "error": "Unauthorized", 
                'db password': SERVICE_PASSWORD,
                'failed attempts': failed_attempts[client_ip]["count"],
            }), 401

    # Successful authentication, reset failed attempts
    failed_attempts.pop(client_ip, None)
    
    return jsonify({
        "app": "Service",
        "data": "Secret Data from Service!",
     })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
