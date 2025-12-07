# backend/rules_engine.py

from typing import List, Dict, Any, Optional

from database import get_supabase_client
from llm_service import (
    validate_exercise_safety,
    suggest_food_replacement,
    suggest_exercise_replacement,
)


class RulesEngine:
    """
    Safety + substitution layer:
      - Uses Supabase metadata (allergens, contraindications, substitution tables)
      - Uses LLM to validate exercise safety and propose replacements
      - Considers injury severity and user goal
    """

    def __init__(self) -> None:
        self.supabase = get_supabase_client()

    # ---------- DB HELPER QUERIES ---------- #

    def get_food_items(self) -> List[Dict[str, Any]]:
        try:
            resp = (
                self.supabase.table("food_items")
                .select("*")
                .eq("is_active", True)
                .execute()
            )
            return resp.data or []
        except Exception as e:
            print(f"Error fetching food items: {e}")
            return []

    def get_exercise_items(self) -> List[Dict[str, Any]]:
        try:
            resp = (
                self.supabase.table("exercise_items")
                .select("*")
                .eq("is_active", True)
                .execute()
            )
            return resp.data or []
        except Exception as e:
            print(f"Error fetching exercise items: {e}")
            return []

    # ---------- ALLERGY LOGIC ---------- #

    def check_food_has_allergen(
        self, food_name: str, allergens: List[str]
    ) -> tuple[bool, Optional[str]]:
        """
        Check if a given food name contains any of the user's allergens,
        using DB allergens field if available, then falling back to simple matching.
        """
        try:
            resp = (
                self.supabase.table("food_items")
                .select("allergens")
                .ilike("name", f"%{food_name}%")
                .limit(1)
                .execute()
            )

            if resp.data:
                food_allergens = resp.data[0].get("allergens") or []
                for allergen in allergens:
                    for food_allergen in food_allergens:
                        if allergen.lower() in food_allergen.lower() or food_allergen.lower() in allergen.lower():
                            return True, allergen

            # Fallback: simple name-based match
            for allergen in allergens:
                if allergen.lower() in food_name.lower():
                    return True, allergen

            return False, None

        except Exception as e:
            print(f"Error checking food allergen: {e}")
            for allergen in allergens:
                if allergen.lower() in food_name.lower():
                    return True, allergen
            return False, None

    def find_food_substitute(self, allergen: str) -> Optional[Dict[str, Any]]:
        """
        Try to find a defined substitution in 'food_substitutions' table.
        Fallback to any food that doesn't contain that allergen.
        """
        try:
            # Look up a specific substitution rule
            resp = (
                self.supabase.table("food_substitutions")
                .select(
                    "substitute_food_id, food_items!food_substitutions_substitute_food_id_fkey(*)"
                )
                .ilike("allergen", f"%{allergen}%")
                .order("priority")
                .limit(1)
                .execute()
            )

            if resp.data:
                substitute = resp.data[0].get("food_items")
                if substitute:
                    return substitute

            # Fallback: any active food without that allergen
            for food in self.get_food_items():
                food_allergens = food.get("allergens") or []
                if allergen.lower() not in [a.lower() for a in food_allergens]:
                    return food

            return None

        except Exception as e:
            print(f"Error finding food substitute for {allergen}: {e}")
            return None

    def apply_allergy_rule(
        self, meals: List[Dict[str, Any]], allergies: List[str], goal: str
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        For each meal:
          - Check if it violates any allergy
          - If yes, try DB-based substitute
          - If DB fails, ask LLM for a safe replacement
        """
        if not allergies:
            return meals, []

        safe_meals: List[Dict[str, Any]] = []
        replacements: List[Dict[str, Any]] = []

        for meal in meals:
            name = meal.get("name", "")
            has_allergen, allergen = self.check_food_has_allergen(name, allergies)

            if has_allergen and allergen:
                # Try DB-based substitution first
                substitute = self.find_food_substitute(allergen)
                if substitute:
                    new_meal = {
                        "name": substitute.get("name", "Safe Meal"),
                        "calories": substitute.get(
                            "calories", meal.get("calories", 0)
                        ),
                        "protein": substitute.get("protein", 0),
                        "carbs": substitute.get("carbs", 0),
                        "fat": substitute.get("fat", 0),
                    }
                    safe_meals.append(new_meal)
                    replacements.append(
                        {
                            "replaced": name,
                            "with": new_meal["name"],
                            "reason": f"{allergen} allergy (DB substitution)",
                        }
                    )
                else:
                    # Ask LLM for a safe replacement
                    llm_sub = suggest_food_replacement(name, allergen, goal)
                    safe_meals.append(llm_sub)
                    replacements.append(
                        {
                            "replaced": name,
                            "with": llm_sub["name"],
                            "reason": f"{allergen} allergy (LLM substitution)",
                        }
                    )
            else:
                safe_meals.append(meal)

        return safe_meals, replacements

    # ---------- INJURY / EXERCISE LOGIC ---------- #

    def check_exercise_has_contraindication(
        self, exercise_name: str, injury_names: List[str]
    ) -> tuple[bool, Optional[str]]:
        """
        Check if an exercise has contraindications for any of the user's injuries,
        using the DB exercise_items.contraindications field if available.
        Returns (True, matched_injury_name) or (False, None).
        """
        try:
            resp = (
                self.supabase.table("exercise_items")
                .select("contraindications")
                .ilike("name", f"%{exercise_name}%")
                .limit(1)
                .execute()
            )

            if resp.data:
                contraindications = resp.data[0].get("contraindications") or []
                for injury in injury_names:
                    for c in contraindications:
                        if injury.lower() in c.lower() or c.lower() in injury.lower():
                            return True, injury

            # Fallback: simple string matching
            for injury in injury_names:
                if injury.lower() in exercise_name.lower():
                    return True, injury

            return False, None

        except Exception as e:
            print(f"Error checking exercise contraindication: {e}")
            for injury in injury_names:
                if injury.lower() in exercise_name.lower():
                    return True, injury
            return False, None

    def find_exercise_substitute(self, injury_name: str) -> Optional[Dict[str, Any]]:
        """
        Try to find an exercise substitution rule in 'exercise_substitutions' table.
        Fallback to any exercise without that contraindication.
        """
        try:
            resp = (
                self.supabase.table("exercise_substitutions")
                .select(
                    "substitute_exercise_id, exercise_items!exercise_substitutions_substitute_exercise_id_fkey(*)"
                )
                .ilike("contraindication", f"%{injury_name}%")
                .order("priority")
                .limit(1)
                .execute()
            )

            if resp.data:
                substitute = resp.data[0].get("exercise_items")
                if substitute:
                    return substitute

            # Fallback: any active exercise without that contraindication
            for ex in self.get_exercise_items():
                contras = ex.get("contraindications") or []
                if injury_name.lower() not in [c.lower() for c in contras]:
                    return ex

            return None

        except Exception as e:
            print(f"Error finding exercise substitute for {injury_name}: {e}")
            return None

    def apply_injury_rule(
        self,
        workouts: List[Dict[str, Any]],
        injuries: List[Dict[str, str]],
        goal: str,
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        For each workout:
        - Use DB to check for contraindications
        - Use severity-based keyword rules (e.g., severe knee)
        - Ask LLM if exercise is safe
        - Substitute with DB rule or LLM recommendation if unsafe
        - ENSURES NO DUPLICATE WORKOUTS in the final list
        """
        if not injuries:
            return workouts, []

        safe_workouts: List[Dict[str, Any]] = []
        replacements: List[Dict[str, Any]] = []

        injury_names = [i["name"] for i in injuries]
        
        # Track workout names to avoid duplicates
        used_workout_names = set()

        for w in workouts:
            w_name = w.get("name", "")
            unsafe = False
            matched_injury_name: Optional[str] = None
            matched_injury: Optional[Dict[str, str]] = None

            # --- 1. DB-based contraindication check ---
            has_contra, inj_name = self.check_exercise_has_contraindication(
                w_name, injury_names
            )
            if has_contra and inj_name:
                unsafe = True
                matched_injury_name = inj_name
                matched_injury = next(
                    (i for i in injuries if i["name"].lower() == inj_name.lower()),
                    {"name": inj_name, "severity": "moderate"},
                )

            # --- 2. Severity-based keyword rules (extra strict for "severe") ---
            if not unsafe:
                for i in injuries:
                    name = i["name"].lower()
                    severity = i.get("severity", "moderate").lower()
                    w_lower = w_name.lower()

                    if name == "knee" and severity == "severe":
                        if any(
                            kw in w_lower
                            for kw in ["squat", "lunge", "leg press", "leg", "calf"]
                        ):
                            unsafe = True
                            matched_injury_name = name
                            matched_injury = i
                            break

                    if name == "wrist" and severity == "severe":
                        if any(
                            kw in w_lower for kw in ["push-up", "push up", "bench", "press"]
                        ):
                            unsafe = True
                            matched_injury_name = name
                            matched_injury = i
                            break

            # --- 3. LLM-based safety check if still unclear ---
            if not unsafe:
                is_safe = validate_exercise_safety(w_name, injuries, goal)
                if not is_safe:
                    unsafe = True
                    # If we don't know which specific injury, just pick the first
                    matched_injury = injuries[0]
                    matched_injury_name = matched_injury["name"]

            # --- 4. Substitution if unsafe ---
            if unsafe and matched_injury_name:
                # Try to find a replacement that's not already in the list
                max_attempts = 5
                replacement_found = False
                
                for attempt in range(max_attempts):
                    # First try DB substitution
                    if attempt == 0:
                        substitute = self.find_exercise_substitute(matched_injury_name)
                        if substitute:
                            new_name = substitute.get("name", "Safe Alternative Exercise")
                            if new_name.lower() not in used_workout_names:
                                new_workout = {
                                    "name": new_name,
                                    "duration": w.get("duration", "3 sets of 10"),
                                    "category": substitute.get("category", ""),
                                    "estimated_calories": substitute.get("estimated_calories_per_minute", 5) * 30,  # Estimate
                                }
                                safe_workouts.append(new_workout)
                                used_workout_names.add(new_name.lower())
                                replacements.append(
                                    {
                                        "replaced": w_name,
                                        "with": new_workout["name"],
                                        "reason": f"{matched_injury_name} contraindication (DB substitution)",
                                    }
                                )
                                replacement_found = True
                                break
                    
                    # Ask the LLM for a replacement
                    llm_sub = suggest_exercise_replacement(w_name, injuries, goal)
                    llm_name = llm_sub.get("name", "Safe Alternative Exercise")
                    
                    # Check if this replacement is already used
                    if llm_name.lower() not in used_workout_names:
                        safe_workouts.append(llm_sub)
                        used_workout_names.add(llm_name.lower())
                        replacements.append(
                            {
                                "replaced": w_name,
                                "with": llm_sub["name"],
                                "reason": f"{matched_injury_name} contraindication (LLM substitution)",
                            }
                        )
                        replacement_found = True
                        break
                    else:
                        print(f"Attempt {attempt + 1}: Replacement '{llm_name}' already used, retrying...")
                
                # If we couldn't find a unique replacement after all attempts, use a generic fallback
                if not replacement_found:
                    fallback_name = f"Alternative Exercise {len(safe_workouts) + 1}"
                    fallback_workout = {
                        "name": fallback_name,
                        "duration": w.get("duration", "3 sets of 10"),
                        "estimated_calories": 150,
                    }
                    safe_workouts.append(fallback_workout)
                    used_workout_names.add(fallback_name.lower())
                    replacements.append(
                        {
                            "replaced": w_name,
                            "with": fallback_name,
                            "reason": f"{matched_injury_name} contraindication (fallback)",
                        }
                    )
            else:
                # Exercise is safe, but check if we already have it
                if w_name.lower() not in used_workout_names:
                    safe_workouts.append(w)
                    used_workout_names.add(w_name.lower())
                else:
                    print(f"Skipping duplicate safe workout: {w_name}")

        return safe_workouts, replacements

    # ---------- MASTER ENTRY POINT ---------- #

    def apply_rules(
        self,
        plan: Dict[str, Any],
        goal: str,
        allergies: List[str],
        injuries: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Main function:
          - apply allergy rules to meals
          - apply injury rules to workouts
        """
        meals, meal_replacements = self.apply_allergy_rule(
            plan.get("meals", []), allergies, goal
        )
        workouts, workout_replacements = self.apply_injury_rule(
            plan.get("workouts", []), injuries, goal
        )

        return {
            "meals": meals,
            "workouts": workouts,
            "replacements": {
                "meals": meal_replacements,
                "workouts": workout_replacements,
            },
        }
