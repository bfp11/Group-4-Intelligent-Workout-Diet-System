from typing import List, Dict, Any
from backend.llm_service import generate_plan_from_llm, validate_exercise_safety



class RulesEngine:
    def __init__(self):
        # More dynamic, category-based data
        self.foods = [
            {"name": "Chicken Breast", "tags": ["protein", "poultry"], "allergens": [], "calories": 165},
            {"name": "Peanut Butter", "tags": ["protein", "nut"], "allergens": ["nuts"], "calories": 188},
            {"name": "Salmon", "tags": ["protein", "fish"], "allergens": ["fish"], "calories": 208},
            {"name": "Almond Butter", "tags": ["protein", "nut"], "allergens": ["nuts"], "calories": 190},
            {"name": "Tofu", "tags": ["protein", "soy"], "allergens": ["soy"], "calories": 144},
            {"name": "Turkey Breast", "tags": ["protein", "poultry"], "allergens": [], "calories": 150},
        ]

        self.exercises = [
            {"name": "Squat", "tags": ["legs", "knees"], "contraindications": ["knee"]},
            {"name": "Push-Up", "tags": ["arms", "chest", "wrist"], "contraindications": ["wrist"]},
            {"name": "Deadlift", "tags": ["back", "legs"], "contraindications": ["lower back", "knee"]},
            {"name": "Stationary Bike", "tags": ["legs", "cardio"], "contraindications": []},
            {"name": "Seated Row", "tags": ["back", "arms"], "contraindications": []},
            {"name": "Lateral Raise", "tags": ["shoulders"], "contraindications": []},
        ]

        # Dynamic substitution mappings
        self.food_substitutions = {
            "nuts": "Chicken Breast",
            "fish": "Turkey Breast",
            "soy": "Chicken Breast"
        }

        self.exercise_substitutions = {
            "knee": "Seated Row",
            "wrist": "Stationary Bike",
            "lower back": "Lateral Raise"
        }

    # ---------------------- HELPER FUNCTIONS ---------------------- #

    def find_food_substitute(self, allergen: str) -> Dict[str, Any]:
        """Find safe food or fallback to generic safe option."""
        substitute_name = self.food_substitutions.get(allergen.lower())
        if not substitute_name:
            return next((f for f in self.foods if not f["allergens"]), None)
        return next((f for f in self.foods if f["name"] == substitute_name), None)

    def find_exercise_substitute(self, injury: str, severity: str = "moderate") -> Dict[str, Any]:
        """Return safe exercise, factoring in severity."""
        if severity == "severe":
            # avoid all tags related to injury
            return next((e for e in self.exercises if not any(injury in t for t in e["tags"])), None)
        elif severity == "mild":
            # allow low-strain movements like Stationary Bike
            return next((e for e in self.exercises if "cardio" in e["tags"]), None)
        else:
            substitute_name = self.exercise_substitutions.get(injury.lower())
            if substitute_name:
                return next((e for e in self.exercises if e["name"] == substitute_name), None)
        return next((e for e in self.exercises if not e["contraindications"]), None)

    # ---------------------- RULE APPLICATION ---------------------- #

    def apply_allergy_rule(self, meals: List[Dict], allergies: List[str]) -> (List[Dict], List[Dict]):
        safe_meals = []
        replacements = []

        for meal in meals:
            if any(a.lower() in meal["name"].lower() for a in allergies):
                allergen = next((a for a in allergies if a.lower() in meal["name"].lower()), allergies[0])
                substitute = self.find_food_substitute(allergen)
                if substitute:
                    safe_meals.append({"name": substitute["name"], "calories": substitute["calories"]})
                    replacements.append({
                        "replaced": meal["name"],
                        "with": substitute["name"],
                        "reason": f"Contains {allergen} allergen"
                    })
                else:
                    # LLM fallback
                    llm_substitute = self.ask_llm_for_replacement(meal["name"], "allergy", allergen)
                    safe_meals.append(llm_substitute)
                    replacements.append({
                        "replaced": meal["name"],
                        "with": llm_substitute["name"],
                        "reason": f"LLM replacement for {allergen} allergen"
                    })
            else:
                safe_meals.append(meal)
        return safe_meals, replacements

    def apply_injury_rule(self, workouts, injuries):
        safe_workouts = []
        replacements = []

        for w in workouts:
            is_unsafe = False
            matched_injury = None

            # --- 1. Static filtering by known contraindications ---
            for injury in injuries:
                injury_name = injury["name"].lower()
                severity = injury.get("severity", "moderate").lower()

                # direct contraindication or body-part match
                if (
                    injury_name in w.get("name", "").lower()
                    or injury_name in w.get("contraindications", "").lower()
                ):
                    is_unsafe = True
                    matched_injury = injury_name
                    break

                # severity-based check — stricter rules
                if injury_name == "knee" and severity == "severe" and any(
                    kw in w["name"].lower() for kw in ["leg", "calf", "squat", "lunge"]
                ):
                    is_unsafe = True
                    matched_injury = injury_name
                    break
                if injury_name == "wrist" and severity == "severe" and any(
                    kw in w["name"].lower() for kw in ["push", "bench", "press"]
                ):
                    is_unsafe = True
                    matched_injury = injury_name
                    break

            # --- 2. LLM-based validation if unclear ---
            if not is_unsafe:
                is_safe_llm = validate_exercise_safety(w["name"], injuries)
                if not is_safe_llm:
                    is_unsafe = True
                    matched_injury = injuries[0]["name"] if injuries else "unknown"

            # --- 3. Replace unsafe workouts ---
            if is_unsafe:
                substitute = self.find_exercise_substitute(matched_injury)
                if substitute:
                    safe_workouts.append({
                        "name": substitute["name"],
                        "duration": w.get("duration", "3 sets of 10")
                    })
                    replacements.append({
                        "replaced": w["name"],
                        "with": substitute["name"],
                        "reason": f"unsafe for {matched_injury} injury"
                    })
                else:
                    print(f"No safe substitute found for {w['name']}, skipping.")
            else:
                safe_workouts.append(w)

        return safe_workouts, replacements
    def ask_llm_for_replacement(self, item: str, context: str, issue: str) -> Dict[str, Any]:
        """Ask the LLM for safe replacements dynamically."""
        prompt = f"Suggest a safe replacement for '{item}' considering the user's {context}: {issue}. " \
                f"Return a short JSON object with name and (if food) calories or (if workout) duration."
        response = generate_plan_from_llm(prompt)
        if isinstance(response, dict):
            return response
        return {"name": "Generic Safe Option", "calories": 200 if context == "allergy" else "3 sets of 10"}

    # ---------------------- MASTER RULE APPLICATION ---------------------- #

    def apply_rules(self, plan: Dict, allergies: List[str], injuries: List[Dict]):
        meals, meal_replacements = self.apply_allergy_rule(plan.get("meals", []), allergies)
        workouts, workout_replacements = self.apply_injury_rule(plan.get("workouts", []), injuries)

        return {
            "meals": meals,
            "workouts": workouts,
            "replacements": {
                "meals": meal_replacements,
                "workouts": workout_replacements
            }
        }
