from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
from backend.rules_engine import RulesEngine
from backend.llm_service import generate_plan_from_llm

app = FastAPI()
rules_engine = RulesEngine()


class Injury(BaseModel):
    name: str
    severity: str = "moderate"  # Default to moderate if not specified


class PlanRequest(BaseModel):
    goal: str
    allergies: List[str] = []
    injuries: Union[List[str], List[Injury]] = []


@app.post("/generate-plan")
async def generate_plan(request: PlanRequest):
    try:
        # Normalize injuries to a consistent structure first
        injuries = []
        for i in request.injuries:
            if isinstance(i, str):
                injuries.append({"name": i, "severity": "moderate"})
            elif isinstance(i, dict):
                injuries.append({"name": i.get("name", ""), "severity": i.get("severity", "moderate")})
            else:
                injuries.append({"name": i.name, "severity": i.severity})

        # Generate plan using LLM
        raw_plan = generate_plan_from_llm(request.goal, request.allergies, injuries)

        # Apply rules
        safe_plan = rules_engine.apply_rules(
            plan=raw_plan,
            allergies=request.allergies,
            injuries=injuries
        )

        return {
            "goal": request.goal,
            "safe_plan": {
                "meals": safe_plan["meals"],
                "workouts": safe_plan["workouts"]
            },
            "replacements_made": safe_plan["replacements"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
