# backend/main.py - Secure Authentication with Database Storage
# This version uses bcrypt for password hashing and stores sessions in Supabase

from fastapi import FastAPI, HTTPException, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Union, Dict, Any, Optional
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

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# AUTHENTICATION HELPER FUNCTIONS
# ============================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_session(user_id: str, username: str) -> str:
    """Create a new session in Supabase and return session ID"""
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
    """Get session data from Supabase if valid, None otherwise"""
    if not session_id:
        return None
    
    supabase = get_supabase_client()
    
    try:
        # Get session from database
        result = supabase.table('sessions').select('*, users(id, name, email)').eq('session_id', session_id).execute()
        
        if not result.data:
            return None
        
        session = result.data[0]
        
        # Check if expired
        expires_at = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00'))
        if datetime.now(expires_at.tzinfo) > expires_at:
            # Delete expired session
            supabase.table('sessions').delete().eq('session_id', session_id).execute()
            return None
        
        # Return user data
        user = session.get('users')
        if user:
            return {
                "user_id": user['id'],
                "username": user['name']
            }
        
        return None
    except Exception as e:
        print(f"Error getting session: {e}")
        return None

def delete_session(session_id: str):
    """Delete a session from Supabase"""
    if not session_id:
        return
    
    supabase = get_supabase_client()
    
    try:
        supabase.table('sessions').delete().eq('session_id', session_id).execute()
    except Exception as e:
        print(f"Error deleting session: {e}")

# ============================================
# PYDANTIC MODELS
# ============================================

# Authentication Models
class SignupRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

# Plan Generation Models
class Injury(BaseModel):
    name: str
    severity: str = "moderate"

class PlanRequest(BaseModel):
    goal: str
    allergies: List[str] = []
    injuries: Union[List[str], List[Injury]] = []

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/api/signup")
async def signup(request: SignupRequest):
    """
    Create a new user account with secure password hashing
    """
    supabase = get_supabase_client()
    
    try:
        # Check if username already exists
        existing = supabase.table('users').select('id').eq('email', request.username).execute()
        
        if existing.data:
            raise HTTPException(status_code=409, detail="Username already taken")
        
        # Hash password with bcrypt
        password_hash = hash_password(request.password)
        
        # Create user in database
        result = supabase.table('users').insert({
            "name": request.username,
            "email": request.username,  # Using username as email for simplicity
            "password_hash": password_hash
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        return {"message": "User created successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/login")
async def login(request: LoginRequest, response: Response):
    """
    Log in with username and password, create session in database
    """
    supabase = get_supabase_client()
    
    try:
        # Find user by username
        result = supabase.table('users').select('*').eq('email', request.username).execute()
        
        if not result.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = result.data[0]
        
        # Verify password
        if not user.get('password_hash'):
            # User has no password (old account), reject login
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(request.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create session in database
        session_id = create_session(user['id'], user['name'])
        
        # Set session cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=7 * 24 * 60 * 60,  # 7 days
            samesite="lax"
        )
        
        return {"message": "Login successful"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/logout")
async def logout(response: Response, session_id: Optional[str] = Cookie(None)):
    """
    Log out and delete session from database
    """
    if session_id:
        delete_session(session_id)
    
    response.delete_cookie("session_id")
    return {"message": "Logged out successfully"}


@app.get("/api/me")
async def get_current_user(session_id: Optional[str] = Cookie(None)):
    """
    Get current logged-in user from database session
    """
    session_data = get_session(session_id)
    
    if not session_data:
        return {"user": None}
    
    return {
        "user": {
            "id": session_data["user_id"],
            "username": session_data["username"]
        }
    }

# ============================================
# PLAN GENERATION ENDPOINTS
# ============================================

@app.get("/")
async def root():
    return {
        "message": "Workout & Diet Planner API is running",
        "version": "2.0.0",
        "status": "healthy",
        "auth": "secure (bcrypt + database sessions)"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api": "running",
        "auth": "database-backed"
    }


@app.post("/generate-plan")
async def generate_plan(request: PlanRequest) -> Dict[str, Any]:
    """
    Generate a personalized workout and meal plan based on user input.
    """
    try:
        # 1. Normalize injuries into a consistent {name, severity} shape
        injuries: List[Dict[str, str]] = []
        for i in request.injuries:
            if isinstance(i, str):
                injuries.append({"name": i, "severity": "moderate"})
            elif hasattr(i, "name") and hasattr(i, "severity"):
                injuries.append({"name": i.name, "severity": i.severity})
            elif isinstance(i, dict):
                injuries.append({
                    "name": i.get("name", ""),
                    "severity": i.get("severity", "moderate"),
                })

        # 2. Generate initial plan from the LLM
        print(f"Generating plan for goal: {request.goal}")
        print(f"Allergies: {request.allergies}")
        print(f"Injuries: {injuries}")
        
        raw_plan = generate_plan_from_llm(
            goal=request.goal,
            allergies=request.allergies,
            injuries=injuries,
        )

        if "error" in raw_plan:
            raise HTTPException(status_code=500, detail=raw_plan["error"])

        # 3. Apply safety + replacement rules
        rules_engine = RulesEngine()
        safe_plan = rules_engine.apply_rules(
            plan=raw_plan,
            goal=request.goal,
            allergies=request.allergies,
            injuries=injuries,
        )

        print(f"Plan generated successfully with {len(safe_plan['meals'])} meals and {len(safe_plan['workouts'])} workouts")

        # 4. Return combined response
        return {
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
        print(f"Error generating plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)