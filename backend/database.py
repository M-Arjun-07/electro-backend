import json
import os

DB_FILE = "db.json"

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"users": {}}, f, indent=4)

def get_data():
    init_db()
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        data = {}
    if "users" not in data:
        data["users"] = {}
    return data

def get_user(username: str):
    data = get_data()
    return data["users"].get(username)

def save_user(username: str, user_data: dict):
    data = get_data()
    data["users"][username] = user_data
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
