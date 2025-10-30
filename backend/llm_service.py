import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_plan_from_llm(goal: str, allergies: list[str], injuries: list[str]) -> dict:
    """Generates a personalized workout + diet plan using OpenAI"""

    prompt = f"""
    You are an AI fitness and nutrition assistant.
    Respond ONLY with valid JSON — no Markdown or explanations.
    Create a one-day workout and diet plan for a user whose goal is: {goal}.
    Avoid foods with these allergies: {', '.join(allergies) or 'none'}.
    Avoid exercises that are unsafe for: {', '.join(injuries) or 'none'}.

    The JSON should look like:
    {{
        "meals": [
            {{"name": "Chicken Salad", "calories": 350}},
            ...
        ],
        "workouts": [
            {{"name": "Squats", "duration": "3 sets of 10"}},
            ...
        ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        print("Raw LLM text:\n", content)

        #Remove Markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")
            # find the JSON part (usually between ```json ... ```)
            content = next((c for c in content if "{" in c and "}" in c), content[0])
            content = content.strip()

        plan = json.loads(content)

        if "exercises" in plan and "workouts" not in plan:
            plan["workouts"] = plan.pop("exercises")
        plan.setdefault("meals", [])
        plan.setdefault("workouts", [])

        print("Parsed Plan:", json.dumps(plan, indent=2))
        return plan

    except json.JSONDecodeError as e:
        print("JSON parsing failed:", e)
        return {"error": "Model did not return valid JSON", "meals": [], "workouts": []}

    except Exception as e:
        print("LLM generation failed:", e)
        return {"error": f"LLM generation failed: {e}", "meals": [], "workouts": []}
