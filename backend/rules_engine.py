from typing import List, Dict, Optional
from database import get_supabase_client

class RulesEngine:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def get_food_items(self) -> List[Dict]:
        """Fetch all active food items from database"""
        try:
            response = self.supabase.table('food_items').select('*').eq('is_active', True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching food items: {e}")
            return []
    
    def get_exercise_items(self) -> List[Dict]:
        """Fetch all active exercise items from database"""
        try:
            response = self.supabase.table('exercise_items').select('*').eq('is_active', True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching exercise items: {e}")
            return []
    
    def find_food_substitute(self, allergen: str) -> Optional[Dict]:
        """Find a safe food substitute for a given allergen"""
        try:
            # First, try to find a defined substitution rule
            response = self.supabase.table('food_substitutions') \
                .select('substitute_food_id, food_items!food_substitutions_substitute_food_id_fkey(*)') \
                .ilike('allergen', f'%{allergen}%') \
                .order('priority') \
                .limit(1) \
                .execute()
            
            if response.data and len(response.data) > 0:
                # Extract the nested food_items data
                substitute = response.data[0].get('food_items')
                if substitute:
                    return substitute
            
            # Fallback: find any food that doesn't contain the allergen
            # Using postgrest's not_.cs (not contains) operator
            all_foods = self.get_food_items()
            for food in all_foods:
                allergens = food.get('allergens', [])
                if allergen.lower() not in [a.lower() for a in allergens]:
                    return food
            
            return None
        except Exception as e:
            print(f"Error finding food substitute for {allergen}: {e}")
            return None
    
    def find_exercise_substitute(self, injury: str) -> Optional[Dict]:
        """Find a safe exercise substitute for a given injury"""
        try:
            # First, try to find a defined substitution rule
            response = self.supabase.table('exercise_substitutions') \
                .select('substitute_exercise_id, exercise_items!exercise_substitutions_substitute_exercise_id_fkey(*)') \
                .ilike('contraindication', f'%{injury}%') \
                .order('priority') \
                .limit(1) \
                .execute()
            
            if response.data and len(response.data) > 0:
                substitute = response.data[0].get('exercise_items')
                if substitute:
                    return substitute
            
            # Fallback: find any exercise without that contraindication
            all_exercises = self.get_exercise_items()
            for exercise in all_exercises:
                contraindications = exercise.get('contraindications', [])
                if injury.lower() not in [c.lower() for c in contraindications]:
                    return exercise
            
            return None
        except Exception as e:
            print(f"Error finding exercise substitute for {injury}: {e}")
            return None
    
    def check_food_has_allergen(self, food_name: str, allergens: List[str]) -> tuple[bool, Optional[str]]:
        """Check if a food contains any of the user's allergens"""
        try:
            # Try to find the food in our database
            response = self.supabase.table('food_items') \
                .select('allergens') \
                .ilike('name', f'%{food_name}%') \
                .limit(1) \
                .execute()
            
            if response.data and len(response.data) > 0:
                food_allergens = response.data[0].get('allergens', [])
                for allergen in allergens:
                    for food_allergen in food_allergens:
                        if allergen.lower() in food_allergen.lower() or food_allergen.lower() in allergen.lower():
                            return True, allergen
            
            # If not in database, do simple name matching
            for allergen in allergens:
                if allergen.lower() in food_name.lower():
                    return True, allergen
            
            return False, None
        except Exception as e:
            print(f"Error checking food allergen: {e}")
            # Fallback to simple name matching
            for allergen in allergens:
                if allergen.lower() in food_name.lower():
                    return True, allergen
            return False, None
    
    def check_exercise_has_contraindication(self, exercise_name: str, injuries: List[str]) -> tuple[bool, Optional[str]]:
        """Check if an exercise has contraindications for user's injuries"""
        try:
            # Try to find the exercise in our database
            response = self.supabase.table('exercise_items') \
                .select('contraindications') \
                .ilike('name', f'%{exercise_name}%') \
                .limit(1) \
                .execute()
            
            if response.data and len(response.data) > 0:
                contraindications = response.data[0].get('contraindications', [])
                for injury in injuries:
                    for contraindication in contraindications:
                        if injury.lower() in contraindication.lower() or contraindication.lower() in injury.lower():
                            return True, injury
            
            # If not in database, do simple name matching
            for injury in injuries:
                if injury.lower() in exercise_name.lower():
                    return True, injury
            
            return False, None
        except Exception as e:
            print(f"Error checking exercise contraindication: {e}")
            # Fallback to simple name matching
            for injury in injuries:
                if injury.lower() in exercise_name.lower():
                    return True, injury
            return False, None
    
    def apply_allergy_rule(self, meals: List[Dict], allergies: List[str]) -> tuple[List[Dict], List[Dict]]:
        """Replace unsafe meals with safe alternatives"""
        if not allergies:
            return meals, []
        
        safe_meals = []
        replacements = []
        
        for meal in meals:
            meal_name = meal.get("name", "")
            has_allergen, allergen = self.check_food_has_allergen(meal_name, allergies)
            
            if has_allergen:
                substitute = self.find_food_substitute(allergen)
                if substitute:
                    safe_meals.append({
                        "name": substitute["name"],
                        "calories": substitute.get("calories", meal.get("calories", 0)),
                        "protein": substitute.get("protein", 0),
                        "carbs": substitute.get("carbs", 0),
                        "fat": substitute.get("fat", 0)
                    })
                    replacements.append({
                        "replaced": meal_name,
                        "with": substitute["name"],
                        "reason": f"{allergen} allergy"
                    })
                else:
                    # No substitute found, keep original but flag it
                    safe_meals.append(meal)
                    print(f"Warning: No substitute found for {meal_name} (allergen: {allergen})")
            else:
                safe_meals.append(meal)
        
        return safe_meals, replacements
    
    def apply_injury_rule(self, workouts: List[Dict], injuries: List[str]) -> tuple[List[Dict], List[Dict]]:
        """Replace unsafe workouts with safe alternatives"""
        if not injuries:
            return workouts, []
        
        safe_workouts = []
        replacements = []
        
        for workout in workouts:
            workout_name = workout.get("name", "")
            has_contraindication, injury = self.check_exercise_has_contraindication(workout_name, injuries)
            
            if has_contraindication:
                substitute = self.find_exercise_substitute(injury)
                if substitute:
                    safe_workouts.append({
                        "name": substitute["name"],
                        "duration": workout.get("duration", "3 sets of 10"),
                        "category": substitute.get("category", ""),
                        "estimated_calories": substitute.get("estimated_calories_per_minute", 0) * 30
                    })
                    replacements.append({
                        "replaced": workout_name,
                        "with": substitute["name"],
                        "reason": f"{injury} contraindication"
                    })
                else:
                    # No substitute found, keep original but flag it
                    safe_workouts.append(workout)
                    print(f"Warning: No substitute found for {workout_name} (injury: {injury})")
            else:
                safe_workouts.append(workout)
        
        return safe_workouts, replacements
    
    def apply_rules(self, plan: Dict, allergies: List[str], injuries: List[str]) -> Dict:
        """Apply all safety rules to the plan"""
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
