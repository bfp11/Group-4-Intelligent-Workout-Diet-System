# backend/llm_service.py

import os
import json
from typing import List, Dict, Any

from openai import OpenAI
from dotenv import load_dotenv

from database import get_supabase_client

# Load env vars from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase = get_supabase_client()


def _safe_json_from_model_content(content: str) -> Dict[str, Any]:
    """
    Strip code fences if present and parse JSON safely.
    """
    text = content.strip()

    # Remove ``` blocks if the model added them
    if text.startswith("```"):
        parts = text.split("```")
        # Find the part that looks like JSON
        for part in parts:
            if "{" in part and "}" in part:
                text = part.strip()
                break

    return json.loads(text)


def get_available_foods_and_exercises() -> tuple[List[str], List[str]]:
    """
    Fetch available foods and exercises from Supabase to bias the LLM
    toward items we actually support in the database.
    """
    foods: List[str] = []
    exercises: List[str] = []

    try:
        foods_response = (
            supabase.table("food_items")
            .select("name")
            .eq("is_active", True)
            .execute()
        )
        exercises_response = (
            supabase.table("exercise_items")
            .select("name")
            .eq("is_active", True)
            .execute()
        )

        if foods_response.data:
            foods = [f["name"] for f in foods_response.data]

        if exercises_response.data:
            exercises = [e["name"] for e in exercises_response.data]

    except Exception as e:
        print(f"Error fetching available items from Supabase: {e}")

    # Fallbacks if DB is empty or unavailable
    if not foods:
        foods = ["Chicken Breast", "Salmon", "Tofu", "Brown Rice", "Quinoa", "Broccoli"]

    if not exercises:
        exercises = ["Squats", "Push-Ups", "Stationary Bike", "Planks", "Seated Row"]

    return foods, exercises


def generate_plan_from_llm(
    goal: str, allergies: List[str], injuries: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Generates a personalized workout + diet plan using OpenAI.
    Uses:
      - user goal
      - allergies
      - injuries with severities
      - available foods/exercises from Supabase
    """

    available_foods, available_exercises = get_available_foods_and_exercises()

    allergy_text = ", ".join(allergies) if allergies else "none"
    injury_descriptions = [
        f"{i.get('name', '')} ({i.get('severity', 'moderate')})" for i in injuries
    ]
    injury_text = ", ".join(injury_descriptions) if injuries else "none"

    foods_list = ", ".join(available_foods)
    exercises_list = ", ".join(available_exercises)

    prompt = f"""
You are an AI fitness and nutrition assistant.

Respond ONLY with valid JSON — no Markdown, no code fences, no explanations.

Create a one-day workout and diet plan for a user whose goal is: "{goal}".

- User allergies: {allergy_text}.
- User injuries and severities: {injury_text}.

IMPORTANT:
- Try to primarily use foods from this list: {foods_list}
- Try to primarily use exercises from this list: {exercises_list}
- Avoid any foods that conflict with the allergies.
- Avoid any exercises that would be unsafe given the injuries and severities.

CRITICAL WORKOUT REQUIREMENTS - READ CAREFULLY:
- Generate EXACTLY 4-6 workouts
- ABSOLUTE RULE: NO TWO WORKOUTS CAN HAVE THE SAME NAME
- Each workout MUST target a DIFFERENT muscle group or movement pattern
- Mix workout types: at least 1 cardio, at least 1 strength, at least 1 core/flexibility
- Examples of DIFFERENT workouts: Push-Ups, Squats, Stationary Bike, Plank, Lunges, Rowing Machine
- INVALID example (DO NOT DO THIS): Dumbbell Shoulder Press, Dumbbell Shoulder Press, Dumbbell Shoulder Press
- If you're about to repeat a workout, STOP and choose a completely different exercise instead

CRITICAL MEAL REQUIREMENTS:
- Generate EXACTLY 4-6 meals
- ABSOLUTE RULE: NO TWO MEALS CAN HAVE THE SAME NAME
- Vary the meals: breakfast items, lunch items, dinner items, snacks
- INVALID example (DO NOT DO THIS): Chicken Breast, Chicken Breast, Chicken Breast

Return JSON with this exact structure:

{{
  "meals": [
    {{ 
      "name": "Scrambled Eggs with Spinach", 
      "calories": 250,
      "protein": 18,
      "carbs": 5,
      "fat": 15
    }},
    {{ 
      "name": "Grilled Chicken Salad", 
      "calories": 350,
      "protein": 35,
      "carbs": 20,
      "fat": 12
    }},
    {{ 
      "name": "Quinoa Bowl with Vegetables", 
      "calories": 300,
      "protein": 12,
      "carbs": 45,
      "fat": 8
    }},
    {{ 
      "name": "Greek Yogurt with Berries", 
      "calories": 150,
      "protein": 15,
      "carbs": 20,
      "fat": 2
    }}
  ],
  "workouts": [
    {{ 
      "name": "Push-Ups", 
      "duration": "3 sets of 12",
      "estimated_calories": 100
    }},
    {{ 
      "name": "Squats", 
      "duration": "3 sets of 15",
      "estimated_calories": 120
    }},
    {{ 
      "name": "Stationary Bike", 
      "duration": "20 minutes",
      "estimated_calories": 200
    }},
    {{ 
      "name": "Plank", 
      "duration": "3 sets of 45 seconds",
      "estimated_calories": 75
    }}
  ]
}}

VERIFICATION BEFORE RESPONDING:
- Count your workouts - do any have the exact same name? If YES, fix it!
- Count your meals - do any have the exact same name? If YES, fix it!
- Are you mixing cardio and strength? If NO, add variety!

FINAL REQUIREMENTS:
- Each meal MUST include: name, calories (integer), protein (grams as integer), carbs (grams as integer), fat (grams as integer)
- Each workout MUST include: name, duration (string), estimated_calories (integer)
- Provide realistic nutritional values based on typical serving sizes
- VERIFY: Every workout name is different from every other workout name
- VERIFY: Every meal name is different from every other meal name

Return ONLY the JSON.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,  # Increased for more variety
        )

        content = response.choices[0].message.content or ""
        print("Raw LLM plan text:\n", content)

        plan = _safe_json_from_model_content(content)

        # Normalize field names
        if "exercises" in plan and "workouts" not in plan:
            plan["workouts"] = plan.pop("exercises")

        plan.setdefault("meals", [])
        plan.setdefault("workouts", [])

        # Remove duplicate workouts (keep first occurrence)
        seen_workout_names = set()
        unique_workouts = []
        original_workout_count = len(plan["workouts"])
        for workout in plan["workouts"]:
            workout_name = workout.get("name", "").lower()
            if workout_name and workout_name not in seen_workout_names:
                seen_workout_names.add(workout_name)
                unique_workouts.append(workout)

        plan["workouts"] = unique_workouts
        print(f"Original workout count: {original_workout_count}, After deduplication: {len(unique_workouts)}")

        # Remove duplicate meals (keep first occurrence)
        seen_meal_names = set()
        unique_meals = []
        original_meal_count = len(plan["meals"])
        for meal in plan["meals"]:
            meal_name = meal.get("name", "").lower()
            if meal_name and meal_name not in seen_meal_names:
                seen_meal_names.add(meal_name)
                unique_meals.append(meal)

        plan["meals"] = unique_meals
        print(f"Original meal count: {original_meal_count}, After deduplication: {len(unique_meals)}")

        # Ensure all meals have nutritional info
        for meal in plan["meals"]:
            meal.setdefault("calories", 0)
            meal.setdefault("protein", 0)
            meal.setdefault("carbs", 0)
            meal.setdefault("fat", 0)

        # Ensure all workouts have required fields
        for workout in plan["workouts"]:
            workout.setdefault("duration", "30 minutes")
            workout.setdefault("estimated_calories", 200)

        print("Parsed Plan:", json.dumps(plan, indent=2))
        return plan

    except json.JSONDecodeError as e:
        print("JSON parsing failed in generate_plan_from_llm:", e)
        return {"error": "Model did not return valid JSON", "meals": [], "workouts": []}
    except Exception as e:
        print("LLM generation failed in generate_plan_from_llm:", e)
        return {"error": f"LLM generation failed: {e}", "meals": [], "workouts": []}


def validate_exercise_safety(
    exercise_name: str, injuries: List[Dict[str, str]], goal: str | None = None
) -> bool:
    """
    Uses the LLM to check if an exercise is safe given the user's injuries.
    Returns:
      True  -> safe
      False -> unsafe or uncertain
    """
    injury_text = ", ".join(
        f"{i.get('name', '')} ({i.get('severity', 'moderate')})" for i in injuries
    )

    goal_text = f" The user's goal is '{goal}'." if goal else ""

    prompt = f"""
You are a certified physical therapist AI.

The user has the following injuries: {injury_text}.{goal_text}
Determine if the exercise "{exercise_name}" is safe to perform.

Respond ONLY with one word: "safe" or "unsafe".
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        answer = (response.choices[0].message.content or "").strip().lower()
        print(f"LLM validation for '{exercise_name}': {answer}")
        return answer.startswith("safe")

    except Exception as e:
        print(f"Error validating {exercise_name}:", e)
        # On errors we act conservatively: treat as unsafe
        return False


def suggest_food_replacement(
    item_name: str, allergen: str, goal: str | None = None
) -> Dict[str, Any]:
    """
    Ask the LLM for a safe food replacement.
    Returns a dict like: {"name": "...", "calories": 200, "protein": 20, "carbs": 30, "fat": 10}
    """
    goal_text = f" The user's overall goal is '{goal}'." if goal else ""

    prompt = f"""
You are a nutrition assistant.

The user is allergic to "{allergen}". The meal "{item_name}" is not safe.
Suggest a single safe replacement meal that:
- avoids the allergen
- is realistic for a normal person
- supports the user's goal.{goal_text}

Return ONLY a JSON object like:
{{ 
  "name": "Safe Meal Name", 
  "calories": 400,
  "protein": 25,
  "carbs": 30,
  "fat": 10
}}

Include realistic nutritional values (protein, carbs, fat in grams).
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        content = response.choices[0].message.content or ""
        print("Raw LLM food replacement text:\n", content)
        data = _safe_json_from_model_content(content)
        # Basic safety defaults
        return {
            "name": data.get("name", "Generic Safe Meal"),
            "calories": data.get("calories", 300),
            "protein": data.get("protein", 20),
            "carbs": data.get("carbs", 30),
            "fat": data.get("fat", 10),
        }
    except Exception as e:
        print("Error in suggest_food_replacement:", e)
        return {
            "name": "Generic Safe Meal", 
            "calories": 300,
            "protein": 20,
            "carbs": 30,
            "fat": 10,
        }


def suggest_exercise_replacement(
    exercise_name: str, injuries: List[Dict[str, str]], goal: str | None = None
) -> Dict[str, Any]:
    """
    Ask the LLM for a safe exercise replacement.
    Returns a dict like: {"name": "...", "duration": "3 sets of 10", "estimated_calories": 150}
    """
    injury_text = ", ".join(
        f"{i.get('name', '')} ({i.get('severity', 'moderate')})" for i in injuries
    )
    goal_text = f" The user's overall goal is '{goal}'." if goal else ""

    prompt = f"""
You are a physical therapist and strength coach.

The user has these injuries: {injury_text}.
The exercise "{exercise_name}" is not safe.

Suggest ONE alternative exercise that:
- is safe for these injuries
- still helps the user work toward their goal.{goal_text}

Return ONLY a JSON object like:
{{ 
  "name": "Safe Exercise", 
  "duration": "3 sets of 12",
  "estimated_calories": 150
}}

Include estimated calories burned.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        content = response.choices[0].message.content or ""
        print("Raw LLM exercise replacement text:\n", content)
        data = _safe_json_from_model_content(content)
        return {
            "name": data.get("name", "Safe Alternative Exercise"),
            "duration": data.get("duration", "3 sets of 10"),
            "estimated_calories": data.get("estimated_calories", 150),
        }
    except Exception as e:
        print("Error in suggest_exercise_replacement:", e)
        return {
            "name": "Safe Alternative Exercise", 
            "duration": "3 sets of 10",
            "estimated_calories": 150,
        }