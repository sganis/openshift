import os
from flask import Flask, request, jsonify
from jose import jwt, JWTError
from datetime import datetime

app = Flask(__name__)

# Config
JWT_SECRET = os.environ.get("JWT_SECRET", "your-dev-secret")
JWT_ISSUER = "api-a"
JWT_AUDIENCE = "api-b"
JWT_ALGORITHM = "HS256"

def verify_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], audience=JWT_AUDIENCE)
        if payload.get("iss") != JWT_ISSUER:
            raise JWTError("Invalid issuer")
        return payload
    except JWTError as e:
        return None

@app.route("/data", methods=["GET"])
def get_data():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(" ")[1]
    payload = verify_jwt(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401

    return jsonify({
        "message": "Authenticated request successful!",
        "from": payload.get("iss"),
        "scope": payload.get("scope"),
        "iat": datetime.fromtimestamp(payload.get("iat")).isoformat(),
        "exp": datetime.fromtimestamp(payload.get("exp")).isoformat(),
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)