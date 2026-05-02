import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import tools
import json

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = None
if api_key and api_key != "your_key_here":
    client = genai.Client(api_key=api_key)

chats = {}

def get_chat_response(session_id: str, message: str, state: str):
    if not client:
        return {"reply": "WARNING: Please set your GEMINI_API_KEY in the .env file to activate AI.", "unlock": None}

    if session_id not in chats:
        chats[session_id] = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=[tools.get_voter_id_rules, tools.get_election_timeline, tools.update_progress, tools.solve_user_issue],
                system_instruction=(
                    "You are a strict Game Master for 'The Voter's Campaign' in India. "
                    "CRITICAL RULE: You MUST ONLY answer questions related to elections, voting, voter IDs, democracy in India, and the game itself. "
                    "If the user asks about ANYTHING ELSE (e.g., coding, weather, recipes, general knowledge), you MUST politely refuse and steer them back to the election game. "
                    "Focus on the Election Commission of India, EPIC cards, and NVSP portal. "
                    "If the user says they have completed a step (registering, getting ID, voting), call 'update_progress' to unlock the node. "
                    "Keep responses gamified, energetic, and concise. Use terms like XP, Level up, Quests."
                ),
                temperature=0.3
            )
        )
    
    tools.latest_unlocked_step = None
    full_message = f"[User Profile: State={state}] User says: {message}"
    
    try:
        response = chats[session_id].send_message(full_message)
        reply_text = response.text
    except Exception as e:
        reply_text = f"Error communicating with Gemini AI: {str(e)}"
    
    unlocked = tools.latest_unlocked_step
    return {"reply": reply_text, "unlock": unlocked}



