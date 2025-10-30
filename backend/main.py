from fastapi import FastAPI
from pydantic import BaseModel
from backend.llm_service import generate_plan_from_llm
from backend.rules_engine import RulesEngine

app = FastAPI(title="Workout & Diet Planner API")

class UserInput(BaseModel):
    goal: str
    allergies: list[str]
    injuries: list[str]

@app.post("/generate-plan")
def generate_plan(user: UserInput):
    plan = generate_plan_from_llm(user.goal, user.allergies, user.injuries)
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
