from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.pool import NullPool
import os

app = Flask(__name__)

# ===== Flask config =====
# Secret key for signing session cookies (set a better one in .env for real use)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# How long "permanent" sessions last (used when session.permanent = True)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

# Turn off extra overhead
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ===== Local SQLite DB =====
# This creates a file named users.db next to app.py
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db = SQLAlchemy(app)


# Allow frontend http://localhost:5173 to talk to this API with cookies
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173"],
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)


@app.post("/api/signup")
def signup():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already taken"}), 409

    password_hash = generate_password_hash(password)
    user = User(username=username, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201


@app.post("/api/login")
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    # create a session
    session.permanent = True  # uses PERMANENT_SESSION_LIFETIME
    session["user_id"] = user.id

    return jsonify({"message": "Login successful"}), 200


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200

@app.get("/")
def index():
    return "Backend is running"

@app.get("/api/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"user": None}), 200

    user = User.query.get(user_id)
    if not user:
        return jsonify({"user": None}), 200

    return jsonify({"user": {"id": user.id, "username": user.username}}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8000, debug=True)
