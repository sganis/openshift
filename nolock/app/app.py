from flask import Flask, jsonify
import requests
import os
import hashlib

app = Flask(__name__)

# File path for storing password failure status
PASSWORD_FAILED_FILE = "/app/data/password_failed.txt"

# Ensure the directory exists
os.makedirs(os.path.dirname(PASSWORD_FAILED_FILE), exist_ok=True)

# Environment variables
SERVICE_URL = os.getenv("SERVICE_URL", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

def get_password_hash(password):
    """Generate a simple hash for the current password."""
    return hashlib.sha256(password.encode()).hexdigest()

def has_password_failed():
    """Check if the last password attempt failed by reading from the file."""
    if os.path.exists(PASSWORD_FAILED_FILE):
        with open(PASSWORD_FAILED_FILE, "r") as file:
            stored_hash = file.read().strip()
            return stored_hash == get_password_hash(DB_PASSWORD)
    return False

def mark_password_as_failed():
    """Mark the current password as failed by writing to a file."""
    with open(PASSWORD_FAILED_FILE, "w") as file:
        file.write(get_password_hash(DB_PASSWORD))

def reset_password_failure():
    """Clear the failure status when a valid password is used."""
    if os.path.exists(PASSWORD_FAILED_FILE):
        os.remove(PASSWORD_FAILED_FILE)

@app.route("/")
def index():
    hostname = os.getenv("HOSTNAME", "Unknown")

    if has_password_failed():
        return jsonify({
            "hostname": hostname,
            "error": "Unauthorized - Password is incorrect, but account is not locked"
        }), 401

    headers = {"Authorization": f"Bearer {DB_PASSWORD}"}
    response = requests.get(f"{SERVICE_URL}/data", headers=headers)

    if response.status_code == 200:
        reset_password_failure()
        return jsonify({
            "hostname": hostname,
            "response": response.json()
        })

    mark_password_as_failed()

    return jsonify({
        "hostname": hostname,
        "error": "Unauthorized - Password is incorrect, but account is not locked"
    }), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
