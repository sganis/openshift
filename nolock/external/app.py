from flask import Flask, request, jsonify
import os
import time

app = Flask(__name__)

# Environment variables
DB_PASSWORD = os.getenv("DB_PASSWORD", "hello")
print(f'DB_PASSWORD: {DB_PASSWORD}')

# Dictionary to track failed attempts: {client_ip: {"count": int, "lock_time": float}}
failed_attempts = {}

# Constants
MAX_ATTEMPTS = 3
LOCKOUT_TIME = 60  # 1 minute

@app.route("/data", methods=["GET"])
def get_data():
    client_ip = request.remote_addr
    auth_header = request.headers.get("Authorization", "")

    # Check if client is locked
    if client_ip in failed_attempts:
        attempts = failed_attempts[client_ip]
        time_since_lock = time.time() - attempts["lock_time"]

        if attempts["count"] >= MAX_ATTEMPTS:
            if time_since_lock < LOCKOUT_TIME:
                return jsonify({
                    "error": "Account locked. Try again later.",
                    "failed attempts": attempts["count"],
                    "lock time remaining": round(LOCKOUT_TIME - time_since_lock, 2),
                }), 403
            else:
                # Reset failed attempts after lockout time expires
                del failed_attempts[client_ip]

    # Validate Authorization header
    if not auth_header.startswith("Bearer "):
        return jsonify({
            "error": "Unauthorized - Missing or malformed token.",
        }), 401

    token = auth_header.split(" ")[-1]
    
    # Validate password
    if token != DB_PASSWORD:
        failed_attempts[client_ip] = failed_attempts.get(client_ip, {"count": 0, "lock_time": time.time()})
        failed_attempts[client_ip]["count"] += 1

        if failed_attempts[client_ip]["count"] >= MAX_ATTEMPTS:
            failed_attempts[client_ip]["lock_time"] = time.time()
            return jsonify({
                "error": "Account locked due to multiple failed attempts.",
                "failed attempts": failed_attempts[client_ip]["count"],
                "lock time remaining": LOCKOUT_TIME,
            }), 403
        else:
            return jsonify({
                "error": "Unauthorized",
                "failed attempts": failed_attempts[client_ip]["count"],
            }), 401

    # Successful authentication, reset failed attempts
    failed_attempts.pop(client_ip, None)

    return jsonify({
        "app": "Service",
        "data": "Secret Data from Service!",
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
