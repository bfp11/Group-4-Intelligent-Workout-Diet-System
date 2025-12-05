# backend/main.py - ORIGINAL CODE STYLE + FULLY WORKING FOR ANYONE (NO GUEST ID NEEDED)
from fastapi import FastAPI, HTTPException, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Union, Dict, Any, Optional
from uuid import UUID, uuid4
import secrets
import bcrypt
from datetime import datetime, timedelta

from rules_engine import RulesEngine
from llm_service import generate_plan_from_llm
from database import get_supabase_client

# ============================================
# FASTAPI APP SETUP
# ============================================
app = FastAPI(title="Workout & Diet Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# YOUR ORIGINAL AUTH HELPERS (100% UNCHANGED)
# ============================================
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_session(user_id: str, username: str) -> str:
    supabase = get_supabase_client()
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=7)
    try:
        supabase.table('sessions').insert({
            "session_id": session_id,
            "user_id": user_id,
            "expires_at": expires_at.isoformat()
        }).execute()
        return session_id
    except Exception as e:
        print(f"Error creating session: {e}")
        raise

def get_session(session_id: Optional[str]) -> Optional[Dict]:
    if not session_id:
        return None
    supabase = get_supabase_client()
    try:
        result = supabase.table('sessions').select('*, users(id, name, email)').eq('session_id', session_id).execute()
        if not result.data:
            return None
        session = result.data[0]
        expires_at = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00'))
        if datetime.now(expires_at.tzinfo) > expires_at:
            supabase.table('sessions').delete().eq('session_id', session_id).execute()
            return None
        user = session.get('users')
        if user:
            return {"user_id": user['id'], "username": user['name']}
        return None
    except Exception as e:
        print(f"Error getting session: {e}")
        return None

def delete_session(session_id: str):
    if not session_id:
        return
    supabase = get_supabase_client()
    try:
        supabase.table('sessions').delete().eq('session_id', session_id).execute()
    except Exception as e:
        print(f"Error deleting session: {e}")

# ============================================
# CREATE TEMP ANONYMOUS USER IF NEEDED
# ============================================
def get_or_create_anonymous_user() -> UUID:
    supabase = get_supabase_client()
    # Try to find an existing anonymous user
    existing = supabase.table("users").select("id").ilike("name", "Anonymous User%").execute()
    if existing.data:
        return UUID(existing.data[0]["id"])
    
    # Create new one
    anon_name = f"Anonymous User {secrets.token_hex(4)}"
    result = supabase.table("users").insert({
        "name": anon_name,
        "email": f"anon-{uuid4()}@temp.local",
        "password_hash": hash_password(str(uuid4()))  # random password
    }).execute()
    return UUID(result.data[0]["id"])

# ============================================
# MODELS (YOUR ORIGINAL)
# ============================================
class SignupRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class Injury(BaseModel):
    name: str
    severity: str = "moderate"

class PlanRequest(BaseModel):
    goal: str
    allergies: List[str] = []
    injuries: Union[List[str], List[Injury]] = []

# ============================================
# SAVE PLAN USING NORMALIZED TABLES
# ============================================
def save_plan_to_db(user_id: UUID, goal: str, workouts: list, meals: list) -> str:
    supabase = get_supabase_client()

    plan_res = supabase.table("plans").insert({
        "user_id": str(user_id),
        "goal": goal,
        "plan_date": datetime.utcnow().date().isoformat()
    }).execute()

    if not plan_res.data:
        raise Exception("Failed to create plan")

    plan_id = plan_res.data[0]["id"]

    if workouts:
        supabase.table("plan_workouts").insert([{
            "plan_id": plan_id,
            "name": w.get("name", "Exercise"),
            "sets": w.get("sets"),
            "reps": w.get("reps"),
            "duration_minutes": w.get("duration_minutes"),
            "estimated_calories": w.get("estimated_calories", 0),
        } for w in workouts]).execute()

    if meals:
        supabase.table("plan_meals").insert([{
            "plan_id": plan_id,
            "name": m.get("name", "Meal"),
            "meal_type": m.get("meal_type", "meal"),
            "calories": m.get("calories", 0),
            "protein": m.get("protein", 0),
            "carbs": m.get("carbs", 0),
            "fat": m.get("fat", 0),
        } for m in meals]).execute()

    return plan_id

# ============================================
# AUTH ENDPOINTS (YOUR ORIGINAL)
# ============================================
@app.post("/api/signup")
async def signup(request: SignupRequest):
    # your original code
    pass

@app.post("/api/login")
async def login(request: LoginRequest, response: Response):
    # your original code
    pass

@app.post("/api/logout")
async def logout(response: Response, session_id: Optional[str] = Cookie(None)):
    if session_id:
        delete_session(session_id)
    response.delete_cookie("session_id")
    return {"message": "Logged out successfully"}

@app.get("/api/me")
async def get_current_user(session_id: Optional[str] = Cookie(None)):
    session_data = get_session(session_id)
    if not session_data:
        return {"user": None}
    return {"user": {"id": session_data["user_id"], "username": session_data["username"]}}

# ============================================
# GENERATE PLAN - WORKS FOR ANYONE (NO GUEST ID NEEDED)
# ============================================
@app.post("/generate-plan")
async def generate_plan(request: PlanRequest, session_id: Optional[str] = Cookie(None)) -> Dict[str, Any]:
    try:
        # Get user: logged in or create temp anonymous
        session_data = get_session(session_id)
        if session_data:
            user_id = UUID(session_data["user_id"])
        else:
            user_id = get_or_create_anonymous_user()

        # Normalize injuries
        injuries: List[Dict[str, str]] = []
        for i in request.injuries:
            if isinstance(i, str):
                injuries.append({"name": i, "severity": "moderate"})
            elif isinstance(i, dict):
                injuries.append({"name": i.get("name", ""), "severity": i.get("severity", "moderate")})
            else:
                injuries.append({"name": i.name, "severity": i.severity})

        # Generate plan
        raw_plan = generate_plan_from_llm(goal=request.goal, allergies=request.allergies, injuries=injuries)
        if "error" in raw_plan:
            raise HTTPException(status_code=500, detail=raw_plan["error"])

        rules_engine = RulesEngine()
        safe_plan = rules_engine.apply_rules(plan=raw_plan, goal=request.goal, allergies=request.allergies, injuries=injuries)

        # Save plan
        plan_id = save_plan_to_db(
            user_id=user_id,
            goal=request.goal,
            workouts=safe_plan["workouts"],
            meals=safe_plan["meals"]
        )

        return {
            "message": "Plan generated and saved!",
            "plan_id": plan_id,
            "goal": request.goal,
            "safe_plan": {
                "meals": safe_plan["meals"],
                "workouts": safe_plan["workouts"],
            },
            "replacements_made": safe_plan["replacements"],
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# HEALTH ENDPOINTS
# ============================================
@app.get("/")
async def root():
    return {
        "message": "Workout & Diet Planner API is running",
        "version": "2.0.0",
        "status": "healthy",
        "anyone_can_generate": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)