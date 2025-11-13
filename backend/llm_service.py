import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from database import get_supabase_client

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_available_foods_and_exercises() -> tuple[list, list]:
    """Fetch available foods and exercises from database"""
    supabase = get_supabase_client()
    
    try:
        foods_response = supabase.table('food_items').select('name, calories').eq('is_active', True).execute()
        exercises_response = supabase.table('exercise_items').select('name, category').eq('is_active', True).execute()
        
        foods = [f['name'] for f in foods_response.data] if foods_response.data else []
        exercises = [e['name'] for e in exercises_response.data] if exercises_response.data else []
        
        return foods, exercises
    except Exception as e:
        print(f"Error fetching available items: {e}")
        return [], []

def generate_plan_from_llm(goal: str, allergies: list[str], injuries: list[str]) -> dict:
    """Generates a personalized workout + diet plan using OpenAI"""
    
    # Get available foods and exercises from database
    available_foods, available_exercises = get_available_foods_and_exercises()
    
    foods_list = ', '.join(available_foods) if available_foods else 'Chicken Breast, Salmon, Tofu, Brown Rice, Quinoa, Broccoli'
    exercises_list = ', '.join(available_exercises) if available_exercises else 'Squats, Push-Ups, Stationary Bike, Planks'
    
    prompt = f"""
    You are an AI fitness and nutrition assistant.
    Respond ONLY with valid JSON — no Markdown, no code fences, no explanations.
    
    Create a one-day workout and diet plan for a user whose goal is: {goal}.
    
    User has these allergies: {', '.join(allergies) if allergies else 'none'}.
    User has these injuries: {', '.join(injuries) if injuries else 'none'}.
    
    IMPORTANT: Try to use foods from this list: {foods_list}
    IMPORTANT: Try to use exercises from this list: {exercises_list}
    
    Provide 3-4 meals and 3-5 exercises.
    
    The JSON must have this exact structure:
    {{
        "meals": [
            {{"name": "Chicken Breast", "calories": 350}},
            {{"name": "Brown Rice", "calories": 200}}
        ],
        "workouts": [
            {{"name": "Squats", "duration": "3 sets of 10"}},
            {{"name": "Push-Ups", "duration": "3 sets of 15"}}
        ]
    }}
    
    Return ONLY the JSON object, nothing else.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        print("Raw LLM response:\n", content)
        
        # Remove Markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            # Remove first and last lines if they're code fence markers
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
        
        # Parse JSON
        plan = json.loads(content)
        
        # Normalize field names
        if "exercises" in plan and "workouts" not in plan:
            plan["workouts"] = plan.pop("exercises")
        
        plan.setdefault("meals", [])
        plan.setdefault("workouts", [])
        
        print("Parsed Plan:", json.dumps(plan, indent=2))
        return plan
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        print(f"Content was: {content}")
        return {"error": "Model did not return valid JSON", "meals": [], "workouts": []}
    except Exception as e:
        print(f"LLM generation failed: {e}")
        return {"error": f"LLM generation failed: {str(e)}", "meals": [], "workouts": []}
