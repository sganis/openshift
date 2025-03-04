from flask import Flask, jsonify
import requests
import os
import hashlib
from dotenv import load_dotenv

# Load .env file from the shared volume
load_dotenv("/app/volume/.env.app")

app = Flask(__name__)

# Environment variables
SERVICE_URL = os.getenv("SERVICE_URL", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Shared file for tracking failed attempts
PASSWORD_FAILED_FILE = "/app/volume/password_failed.txt"

def get_password_hash(password):
    """Generate a simple hash for the current password."""
    return hashlib.sha256(password.encode()).hexdigest()

def has_password_failed():
    """Check if the last password attempt failed and if the stored password hash matches the current password."""
    if not os.path.exists(PASSWORD_FAILED_FILE):
        return False  # No failure recorded

    try:
        with open(PASSWORD_FAILED_FILE, "r") as f:
            stored_hash = f.read().strip()

        return stored_hash == get_password_hash(DB_PASSWORD)  # Only fail if the hash matches
    except Exception:
        return False  # If there's any error, assume no failure

def mark_password_as_failed():
    """Mark the current password as failed to prevent unnecessary retries."""
    with open(PASSWORD_FAILED_FILE, "w") as f:
        f.write(get_password_hash(DB_PASSWORD))  # Store hash instead of raw password

def reset_password_failure():
    """Clear the failure status when a valid password is used."""
    if os.path.exists(PASSWORD_FAILED_FILE):
        os.remove(PASSWORD_FAILED_FILE)

@app.route("/")
def index():
    hostname = os.getenv("HOSTNAME", "Unknown")
    logs = []  # Collect logs in an array to return in the JSON response

    # If the password has failed before AND is still the same, skip retrying
    if has_password_failed():
        logs.append(f"Skipping password retry on {hostname}, last attempt failed with the same password.")
        return jsonify({
            "hostname": hostname,
            "error": "Unauthorized - Password is incorrect, but account is not locked",
            "logs": logs
        }), 401

    # Try the current password
    logs.append(f"Trying password on {hostname}.")
    headers = {"Authorization": f"Bearer {DB_PASSWORD}"}
    response = requests.get(f"{SERVICE_URL}/data", headers=headers)

    if response.status_code == 200:
        logs.append(f"Password worked on {hostname}. Resetting failure status.")
        reset_password_failure()  # Clear failure status
        return jsonify({
            "hostname": hostname,
            "response": response.json(),
            "logs": logs
        })

    # Mark password as failed
    logs.append(f"Password failed on {hostname}. Marking it as failed.")
    mark_password_as_failed()

    return jsonify({
        "hostname": hostname,
        "error": "Unauthorized - Password is incorrect, but account is not locked",
        "logs": logs
    }), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
