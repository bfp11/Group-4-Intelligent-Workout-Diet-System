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
from utils.images import get_smart_food_image, get_smart_exercise_image

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

# Save Plan Model
class SavePlanRequest(BaseModel):
    goal: str
    meals: List[Dict[str, Any]]
    workouts: List[Dict[str, Any]]
    replacements: Optional[Dict[str, Any]] = None
    allergies: Optional[List[str]] = None
    injuries: Optional[List[str]] = None

# Profile Models
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    allergies: Optional[List[str]] = None
    injuries: Optional[List[str]] = None

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
# SAVE PLAN ENDPOINTS
# ============================================

@app.post("/api/save-plan")
async def save_plan(request: SavePlanRequest, session_id: Optional[str] = Cookie(None)):
    """
    Save a workout and meal plan for the logged-in user.
    Maximum 5 plans per user.
    Also updates user's profile with goal, allergies, and injuries.
    """
    # Check authentication
    session_data = get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = session_data["user_id"]
    supabase = get_supabase_client()
    
    try:
        # Check how many plans the user currently has
        existing_plans = supabase.table('plans')\
            .select('id, created_at, goal')\
            .eq('user_id', user_id)\
            .order('created_at', desc=False)\
            .execute()
        
        if len(existing_plans.data) >= 5:
            # Return error indicating they need to delete oldest
            oldest_plan = existing_plans.data[0]
            return {
                "success": False,
                "error": "max_plans_reached",
                "message": "You have reached the maximum of 5 saved plans",
                "oldest_plan": {
                    "id": oldest_plan['id'],
                    "goal": oldest_plan['goal'],
                    "created_at": oldest_plan['created_at']
                }
            }
        
        # Create the plan
        plan_result = supabase.table('plans').insert({
            "user_id": user_id,
            "goal": request.goal,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        if not plan_result.data:
            raise HTTPException(status_code=500, detail="Failed to create plan")
        
        plan_id = plan_result.data[0]['id']
        
        # Save meals to plan_meals table
        for meal in request.meals:
            meal_data = {
                "plan_id": plan_id,
                "meal_type": meal.get('timeOfDay', meal.get('meal_type', 'Anytime')),
                "name": meal.get('title', meal.get('name', 'Unnamed Meal')),
                "calories": int(meal.get('calories', 0)) if meal.get('calories') else 0,
                "protein": int(meal.get('protein', 0)) if meal.get('protein') else 0,
                "carbs": int(meal.get('carbs', 0)) if meal.get('carbs') else 0,
                "fat": int(meal.get('fat', 0)) if meal.get('fat') else 0,
                "was_replaced": meal.get('was_replaced', False)
            }
            
            print(f"Saving meal: {meal_data}")  # Debug logging
            
            supabase.table('plan_meals').insert(meal_data).execute()
        
        # Save workouts to plan_workouts table
        for workout in request.workouts:
            # Extract duration in minutes from duration string (e.g., "30 min" -> 30)
            duration_str = workout.get('duration', '30 min')
            duration_minutes = 30  # default
            if 'min' in duration_str:
                try:
                    duration_minutes = int(duration_str.split()[0])
                except:
                    duration_minutes = 30
            
            workout_data = {
                "plan_id": plan_id,
                "name": workout.get('title', workout.get('name', 'Unnamed Workout')),
                "duration_minutes": duration_minutes,
                "estimated_calories": workout.get('calories', 0),
                "was_replaced": workout.get('was_replaced', False)
            }
            
            print(f"Saving workout: {workout_data}")  # Debug logging
            
            supabase.table('plan_workouts').insert(workout_data).execute()
        
        # Update user profile with the plan's goal, allergies, and injuries
        user_data = supabase.table('users').select('goal, allergies, injuries').eq('id', user_id).execute()
        
        if user_data.data:
            profile_update = {
                "goal": request.goal
            }
            
            # Only update allergies/injuries if they were part of the plan generation
            if hasattr(request, 'allergies') and request.allergies is not None:
                profile_update['allergies'] = request.allergies
            if hasattr(request, 'injuries') and request.injuries is not None:
                profile_update['injuries'] = request.injuries
            
            supabase.table('users').update(profile_update).eq('id', user_id).execute()
        
        return {
            "success": True,
            "message": "Plan saved successfully",
            "plan_id": plan_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/plans/{plan_id}")
async def delete_plan(plan_id: str, session_id: Optional[str] = Cookie(None)):
    """
    Delete a specific plan (and its associated meals/workouts).
    Due to ON DELETE CASCADE, meals and workouts will be automatically deleted.
    """
    # Check authentication
    session_data = get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = session_data["user_id"]
    supabase = get_supabase_client()
    
    try:
        # Verify the plan belongs to this user
        plan = supabase.table('plans')\
            .select('id')\
            .eq('id', plan_id)\
            .eq('user_id', user_id)\
            .execute()
        
        if not plan.data:
            raise HTTPException(status_code=404, detail="Plan not found or access denied")
        
        # Delete the plan (meals and workouts will cascade delete automatically)
        supabase.table('plans').delete().eq('id', plan_id).execute()
        
        return {"success": True, "message": "Plan deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plans")
async def get_saved_plans(session_id: Optional[str] = Cookie(None)):
    """
    Get all saved plans for the logged-in user with their meals and workouts
    Enriches meal data with allergen information and images using smart keyword matching
    """
    # Check authentication
    session_data = get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = session_data["user_id"]
    supabase = get_supabase_client()
    
    try:
        # Get all plans for the user
        plans_result = supabase.table('plans')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()
        
        plans = []
        
        for plan in plans_result.data:
            plan_id = plan['id']
            
            # Get meals for this plan
            meals_result = supabase.table('plan_meals')\
                .select('*')\
                .eq('plan_id', plan_id)\
                .execute()
            
            # Enrich meals with allergen info AND smart IMAGE matching
            enriched_meals = []
            for meal in meals_result.data:
                # Try to find matching food item in database for allergens
                food_item = supabase.table('food_items')\
                    .select('allergens')\
                    .eq('name', meal['name'])\
                    .execute()
                
                # Use smart keyword matching for image
                image_url = get_smart_food_image(meal['name'])
                
                meal_data = {
                    'name': meal['name'],
                    'meal_type': meal['meal_type'],
                    'calories': meal['calories'],
                    'protein': meal['protein'],
                    'carbs': meal['carbs'],
                    'fat': meal['fat'],
                    'was_replaced': meal['was_replaced'],
                    'allergens': food_item.data[0]['allergens'] if food_item.data else [],
                    'image_url': image_url
                }
                enriched_meals.append(meal_data)
            
            # Get workouts for this plan
            workouts_result = supabase.table('plan_workouts')\
                .select('*')\
                .eq('plan_id', plan_id)\
                .execute()
            
            # Enrich workouts with exercise info AND smart IMAGE matching
            enriched_workouts = []
            for workout in workouts_result.data:
                # Try to find matching exercise item in database for metadata
                exercise_item = supabase.table('exercise_items')\
                    .select('category, difficulty_level, contraindications')\
                    .eq('name', workout['name'])\
                    .execute()
                
                # Use smart keyword matching for image
                image_url = get_smart_exercise_image(workout['name'])
                
                workout_data = {
                    'name': workout['name'],
                    'duration_minutes': workout['duration_minutes'],
                    'estimated_calories': workout['estimated_calories'],
                    'was_replaced': workout['was_replaced'],
                    'category': exercise_item.data[0]['category'] if exercise_item.data else None,
                    'difficulty_level': exercise_item.data[0]['difficulty_level'] if exercise_item.data else None,
                    'contraindications': exercise_item.data[0]['contraindications'] if exercise_item.data else [],
                    'image_url': image_url
                }
                enriched_workouts.append(workout_data)
            
            plans.append({
                'id': plan['id'],
                'goal': plan['goal'],
                'created_at': plan['created_at'],
                'meals': enriched_meals,
                'workouts': enriched_workouts,
                'meal_count': len(enriched_meals),
                'workout_count': len(enriched_workouts)
            })
        
        return {
            'success': True,
            'plans': plans
        }
    
    except Exception as e:
        print(f"Error fetching plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# IMAGE ENDPOINTS
# ============================================

@app.get("/api/exercise-image")
async def get_exercise_image(name: str, session_id: Optional[str] = Cookie(None)):
    """
    Get image URL for a specific exercise item with smart keyword matching
    """
    session_data = get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    supabase = get_supabase_client()
    
    try:
        # First try exact match in database
        result = supabase.table('exercise_items')\
            .select('image_url')\
            .eq('name', name)\
            .execute()
        
        if result.data and result.data[0]['image_url']:
            return {"image_url": result.data[0]['image_url']}
        
        # Use smart keyword matching
        return {"image_url": get_smart_exercise_image(name)}
    
    except Exception as e:
        print(f"Error fetching exercise image: {e}")
        return {"image_url": get_smart_exercise_image(name)}


@app.get("/api/food-image")
async def get_food_image(name: str, session_id: Optional[str] = Cookie(None)):
    """
    Get image URL for a specific food item with smart keyword matching
    """
    session_data = get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    supabase = get_supabase_client()
    
    try:
        # First try exact match in database
        result = supabase.table('food_items')\
            .select('image_url')\
            .eq('name', name)\
            .execute()
        
        if result.data and result.data[0]['image_url']:
            return {"image_url": result.data[0]['image_url']}
        
        # Use smart keyword matching
        return {"image_url": get_smart_food_image(name)}
    
    except Exception as e:
        print(f"Error fetching food image: {e}")
        return {"image_url": get_smart_food_image(name)}

# ============================================
# PROFILE ENDPOINTS
# ============================================

@app.get("/api/profile")
async def get_profile(session_id: Optional[str] = Cookie(None)):
    """
    Get the current user's profile data
    """
    # Check authentication
    session_data = get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = session_data["user_id"]
    supabase = get_supabase_client()
    
    try:
        # Get user data
        result = supabase.table('users').select('*').eq('id', user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = result.data[0]
        
        return {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "age": user.get('age'),
            "height": user.get('height'),
            "weight": user.get('weight'),
            "goal": user.get('goal'),
            "allergies": user.get('allergies', []),
            "injuries": user.get('injuries', [])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/profile")
async def update_profile(request: UpdateProfileRequest, session_id: Optional[str] = Cookie(None)):
    """
    Update the current user's profile data
    """
    # Check authentication
    session_data = get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = session_data["user_id"]
    supabase = get_supabase_client()
    
    try:
        # Build update dict with only provided fields
        update_data = {}
        if request.name is not None:
            update_data['name'] = request.name
        if request.age is not None:
            update_data['age'] = request.age
        if request.height is not None:
            update_data['height'] = request.height
        if request.weight is not None:
            update_data['weight'] = request.weight
        if request.goal is not None:
            update_data['goal'] = request.goal
        if request.allergies is not None:
            update_data['allergies'] = request.allergies
        if request.injuries is not None:
            update_data['injuries'] = request.injuries
        
        # Update user data
        result = supabase.table('users').update(update_data).eq('id', user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
        return {
            "success": True,
            "message": "Profile updated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)