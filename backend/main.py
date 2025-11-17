# backend/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union, Dict, Any

from backend.rules_engine import RulesEngine
from backend.llm_service import generate_plan_from_llm

app = FastAPI(title="Workout & Diet Planner API")
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
    return {"message": "Workout & Diet Planner API is running"}


@app.post("/generate-plan")
async def generate_plan(request: PlanRequest) -> Dict[str, Any]:
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

        # 2. Generate initial plan from the LLM (already uses goal, allergies, injuries)
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
        raise HTTPException(status_code=500, detail=str(e))
