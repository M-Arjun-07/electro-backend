from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gemini_agent import get_chat_response
from tools import get_election_timeline
from firebase_admin_config import db, verify_token # Renamed to avoid confusion with firebase_admin package
import uvicorn
from datetime import date
import os
import json
import random

app = FastAPI(title="The Voter's Campaign API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Helper for Firebase Auth
def get_uid(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    try:
        token = authorization.split("Bearer ")[1]
        decoded = verify_token(token)
        if not decoded:
            raise HTTPException(status_code=401, detail="Invalid Token")
        return decoded['uid']
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Authorization Format")

class ChatRequest(BaseModel):
    message: str
    state: str
    session_id: str

class UserProfileUpdate(BaseModel):
    name: str = ""
    email: str = ""
    mobile: str = ""
    location: dict = {}
    profile: dict = {}

class XPRequest(BaseModel):
    points: int

class QuizResult(BaseModel):
    module: str
    score: int
    total: int

@app.get("/user/me")
async def get_user_profile(uid: str = Depends(get_uid)):
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    return user_doc.to_dict()

@app.post("/user/update")
async def update_user_profile(profile: UserProfileUpdate, uid: str = Depends(get_uid)):
    user_ref = db.collection("users").document(uid)
    user_ref.update(profile.dict(exclude_unset=True))
    return {"status": "success"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest, uid: str = Depends(get_uid)):
    result = get_chat_response(uid, req.message, req.state)
    if result["unlock"]:
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get().to_dict()
        modules = user_doc.get("progress", {}).get("modules", [])
        if result["unlock"] not in modules:
            modules.append(result["unlock"])
            user_ref.update({"progress.modules": modules})
    return result

@app.get("/api/daily-drop/{username}")
async def get_daily_drop(username: str, uid: str = Depends(get_uid)):
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get().to_dict()
    
    today_str = date.today().isoformat()
    if user_doc.get("daily", {}).get("daily_drop_date") == today_str:
        return user_doc["daily"]
        
    # Load questions from local JSON instead of AI
    try:
        with open("daily_questions.json", "r") as f:
            data = json.load(f)
        
        all_questions = data.get("questions", [])
        all_quests = data.get("quests", [])
        
        # Select 3 random questions and 1 random quest
        selected_questions = random.sample(all_questions, min(len(all_questions), 3))
        selected_quest = random.choice(all_quests) if all_quests else {}
        
        daily_data = {
            "daily_drop_date": today_str,
            "daily_quest": selected_quest,
            "daily_quiz": selected_questions
        }
        
        user_ref.update({"daily": daily_data})
        return daily_data
    except Exception as e:
        print(f"Error loading daily questions: {e}")
        # Fallback to a simple quest if file fails
        return {
            "daily_drop_date": today_str,
            "daily_quest": {"title": "Daily Challenge", "description": "Complete today's tasks!", "xp_reward": 50},
            "daily_quiz": []
        }

@app.get("/timeline/{state}")
def timeline_endpoint(state: str):
    return get_election_timeline(state)

@app.get("/leaderboard")
async def get_leaderboard():
    users_ref = db.collection("users")
    # Order by XP descending, limit to 10
    query = users_ref.order_by("gamification.xp", direction="DESCENDING").limit(10)
    results = query.stream()
    
    leaderboard = []
    for doc in results:
        data = doc.to_dict()
        leaderboard.append({
            "username": data.get("username"),
            "points": data.get("gamification", {}).get("xp", 0),
            "level": data.get("gamification", {}).get("level", 1),
            "state": data.get("location", {}).get("state", "India")
        })
    return leaderboard

@app.post("/add-xp")
async def add_xp(req: XPRequest, uid: str = Depends(get_uid)):
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get().to_dict()
    current_xp = user_doc.get("gamification", {}).get("xp", 0)
    new_xp = current_xp + req.points
    user_ref.update({"gamification.xp": new_xp})
    return {"status": "success", "new_points": new_xp}

@app.post("/complete-task")
async def complete_task(data: dict, uid: str = Depends(get_uid)):
    task_id = data.get("task_id")
    xp = data.get("xp", 10)
    
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get().to_dict()
    
    modules = user_doc.get("progress", {}).get("modules", [])
    if task_id not in modules:
        modules.append(task_id)
        current_xp = user_doc.get("gamification", {}).get("xp", 0)
        user_ref.update({
            "progress.modules": modules,
            "gamification.xp": current_xp + xp
        })
    
    return user_ref.get().to_dict()

@app.post("/complete-video")
async def complete_video(req: dict, uid: str = Depends(get_uid)):
    video_id = req.get("video_id")
    xp = req.get("xp", 20)
    
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get().to_dict()
    
    watched = user_doc.get("progress", {}).get("watched_videos", [])
    if video_id not in watched:
        watched.append(video_id)
        current_xp = user_doc.get("gamification", {}).get("xp", 0)
        user_ref.update({
            "progress.watched_videos": watched,
            "gamification.xp": current_xp + xp
        })
    
    return {"status": "success", "watched_videos": watched, "points": user_ref.get().to_dict()["gamification"]["xp"]}

@app.post("/quiz-result")
async def post_quiz_result(req: QuizResult, uid: str = Depends(get_uid)):
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get().to_dict()
    
    knowledge = user_doc.get("progress", {}).get("knowledge", {})
    new_score = int((req.score / req.total) * 100)
    knowledge[req.module] = max(knowledge.get(req.module, 0), new_score)
    
    xp_bonus = 40 if req.score >= 3 else 0
    current_xp = user_doc.get("gamification", {}).get("xp", 0)
    
    user_ref.update({
        "progress.knowledge": knowledge,
        "gamification.xp": current_xp + xp_bonus
    })
    
    return {"status": "success", "knowledge": knowledge, "points": current_xp + xp_bonus}

@app.post("/mark-learned")
async def mark_learned(data: dict, uid: str = Depends(get_uid)):
    card_id = data.get("card_id")
    xp = data.get("xp", 5)
    
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get().to_dict()
    
    learned = user_doc.get("progress", {}).get("learned_cards", [])
    if card_id not in learned:
        learned.append(card_id)
        current_xp = user_doc.get("gamification", {}).get("xp", 0)
        user_ref.update({
            "progress.learned_cards": learned,
            "gamification.xp": current_xp + xp
        })
        
    return {"learned_cards": learned, "points": user_ref.get().to_dict()["gamification"]["xp"]}

# Static Data Endpoints (Remain largely same but can be moved to Firestore if needed)
@app.get("/videos/all")
def get_all_videos():
    with open("videos.json", "r") as f: return json.load(f)

@app.get("/videos/{module}")
def get_videos(module: str):
    try:
        with open("videos.json", "r") as f:
            all_videos = json.load(f)
        return all_videos.get(module, [])
    except Exception:
        return []

@app.get("/states")
def get_states():
    from mock_api import get_all_states
    return get_all_states()

@app.get("/districts/{state}")
def get_districts(state: str):
    from mock_api import get_districts_by_state
    return get_districts_by_state(state)

@app.get("/polling-booth")
def get_polling_booth(district: str = "", taluk: str = "", pincode: str = ""):
    from mock_api import get_mock_polling_booth
    return get_mock_polling_booth(district, taluk, pincode)

@app.get("/candidates")
def get_candidates(district: str = "", pincode: str = ""):
    from mock_api import get_mock_candidates
    return get_mock_candidates(district)

@app.post("/ai/simplify")
def simplify_card(data: dict):
    from gemini_agent import get_chat_response # Assuming simplification logic in gemini_agent
    # Placeholder for simplification logic
    return {"reply": "Simplified version of: " + data.get("content", "")}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False if os.environ.get("PORT") else True)
