from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from backend.llm_service import generate_plan_from_llm
from backend.rules_engine import RulesEngine
from backend.database import get_supabase_client

app = FastAPI(title="Workout & Diet Planner API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    goal: str
    allergies: List[str] = []
    injuries: List[str] = []

class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    allergies: List[str] = []
    injuries: List[str] = []

class PlanResponse(BaseModel):
    plan_id: str
    goal: str
    safe_plan: dict
    replacements_made: dict

@app.get("/")
def read_root():
    return {"message": "Workout & Diet Planner API is running"}

@app.post("/generate-plan")
def generate_plan(user: UserInput):
    """Generate a personalized workout and meal plan"""
    
    # Generate plan from LLM
    plan = generate_plan_from_llm(user.goal, user.allergies, user.injuries)
    
    # Check for LLM errors
    if "error" in plan:
        raise HTTPException(status_code=500, detail=plan["error"])
    
    # Apply safety rules
    engine = RulesEngine()
    safe_plan = engine.apply_rules(plan, user.allergies, user.injuries)
    
    return {
        "goal": user.goal,
        "safe_plan": {
            "meals": safe_plan["meals"],
            "workouts": safe_plan["workouts"]
        },
        "replacements_made": safe_plan["replacements"]
    }

@app.post("/save-plan")
def save_plan(user_id: str, plan_data: dict):
    """Save a generated plan to the database"""
    supabase = get_supabase_client()
    
    try:
        # Insert plan
        plan_response = supabase.table('plans').insert({
            "user_id": user_id,
            "goal": plan_data.get("goal", ""),
            "status": "active"
        }).execute()
        
        if not plan_response.data:
            raise HTTPException(status_code=500, detail="Failed to create plan")
        
        plan_id = plan_response.data[0]['id']
        
        # Insert meals
        meals = plan_data.get("meals", [])
        for meal in meals:
            supabase.table('plan_meals').insert({
                "plan_id": plan_id,
                "name": meal.get("name"),
                "calories": meal.get("calories"),
                "protein": meal.get("protein"),
                "carbs": meal.get("carbs"),
                "fat": meal.get("fat")
            }).execute()
        
        # Insert workouts
        workouts = plan_data.get("workouts", [])
        for workout in workouts:
            supabase.table('plan_workouts').insert({
                "plan_id": plan_id,
                "name": workout.get("name"),
                "duration_minutes": 30,  # Default, parse from duration if needed
            }).execute()
        
        return {"plan_id": plan_id, "message": "Plan saved successfully"}
        
    except Exception as e:
        print(f"Error saving plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/foods")
def get_foods():
    """Get all available food items"""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('food_items').select('*').eq('is_active', True).execute()
        return {"foods": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/exercises")
def get_exercises():
    """Get all available exercises"""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('exercise_items').select('*').eq('is_active', True).execute()
        return {"exercises": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/plans")
def get_user_plans(user_id: str):
    """Get all plans for a user"""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('plans') \
            .select('*, plan_meals(*), plan_workouts(*)') \
            .eq('user_id', user_id) \
            .order('created_at', desc=True) \
            .execute()
        
        return {"plans": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)