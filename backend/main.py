# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Union, Dict, Any

from rules_engine import RulesEngine
from llm_service import generate_plan_from_llm

app = FastAPI(title="Workout & Diet Planner API")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rules_engine = RulesEngine()


class Injury(BaseModel):
    name: str
    severity: str = "moderate"  # mild / moderate / severe


class PlanRequest(BaseModel):
    goal: str
    allergies: List[str] = []
    injuries: Union[List[str], List[Injury]] = []


@app.get("/")
async def root():
    return {
        "message": "Workout & Diet Planner API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api": "running"
    }


@app.post("/generate-plan")
async def generate_plan(request: PlanRequest) -> Dict[str, Any]:
    """
    Generate a personalized workout and meal plan based on user input.
    
    Args:
        request: PlanRequest containing goal, allergies, and injuries
        
    Returns:
        Dictionary with safe_plan (meals, workouts) and replacements_made
    """
    try:
        # 1. Normalize injuries into a consistent {name, severity} shape
        injuries: List[Dict[str, str]] = []
        for i in request.injuries:
            # If client sent just a list of strings
            if isinstance(i, str):
                injuries.append({"name": i, "severity": "moderate"})
            # If FastAPI gave us a Pydantic Injury model
            elif hasattr(i, "name") and hasattr(i, "severity"):
                injuries.append({"name": i.name, "severity": i.severity})
            # If we somehow get a dict already
            elif isinstance(i, dict):
                injuries.append(
                    {
                        "name": i.get("name", ""),
                        "severity": i.get("severity", "moderate"),
                    }
                )

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