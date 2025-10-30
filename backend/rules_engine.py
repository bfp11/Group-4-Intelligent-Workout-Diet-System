class RulesEngine:
    def __init__(self):
        self.foods = [
            {"name": "Chicken Breast", "allergens": "none", "calories": 165},
            {"name": "Peanut Butter", "allergens": "peanuts", "calories": 188},
            {"name": "Salmon", "allergens": "fish", "calories": 208},
            {"name": "Almond Butter", "allergens": "none", "calories": 190},
            {"name": "Tofu", "allergens": "soy", "calories": 144},
            {"name": "Turkey Breast", "allergens": "none", "calories": 150},
        ]

        self.exercises = [
            {"name": "Squat", "contraindications": "knee injury"},
            {"name": "Push-Up", "contraindications": "wrist injury"},
            {"name": "Stationary Bike", "contraindications": "none"},
            {"name": "Leg Press", "contraindications": "none"},
            {"name": "Lat Pulldown", "contraindications": "none"},
        ]

        # define basic replacement mappings
        self.food_substitutions = {
            "peanut": "Almond Butter",
            "fish": "Turkey Breast",
            "soy": "Chicken Breast"
        }

        self.exercise_substitutions = {
            "knee": "Stationary Bike",
            "wrist": "Lat Pulldown"
        }

    def find_food_substitute(self, allergen):
        """Finds a safe food to replace an allergen-containing meal."""
        substitute_name = self.food_substitutions.get(allergen.lower())
        if not substitute_name:
            # fallback: pick any safe food
            return next((f for f in self.foods if f["allergens"] == "none"), None)
        return next((f for f in self.foods if f["name"] == substitute_name), None)

    def find_exercise_substitute(self, injury):
        """Finds a safe exercise to replace an unsafe one."""
        substitute_name = self.exercise_substitutions.get(injury.lower())
        if not substitute_name:
            return next((e for e in self.exercises if e["contraindications"] == "none"), None)
        return next((e for e in self.exercises if e["name"] == substitute_name), None)

    def apply_allergy_rule(self, meals, allergies):
        safe_meals = []
        replacements = []  # track replacements

        for meal in meals:
            if any(a.lower() in meal["name"].lower() for a in allergies):
                substitute = self.find_food_substitute(allergies[0])
                if substitute:
                    safe_meals.append({
                        "name": substitute["name"],
                        "calories": substitute["calories"]
                    })
                    replacements.append({
                        "replaced": meal["name"],
                        "with": substitute["name"]
                    })
            else:
                safe_meals.append(meal)
        return safe_meals, replacements

    def apply_injury_rule(self, workouts, injuries):
        safe_workouts = []
        replacements = []

        for w in workouts:
            if any(i.lower() in w["name"].lower() or i.lower() in w.get("contraindications", "").lower() for i in injuries):
                substitute = self.find_exercise_substitute(injuries[0])
                if substitute:
                    safe_workouts.append({
                        "name": substitute["name"],
                        "duration": w.get("duration", "3 sets of 10")
                    })
                    replacements.append({
                        "replaced": w["name"],
                        "with": substitute["name"]
                    })
            else:
                safe_workouts.append(w)
        return safe_workouts, replacements

    def apply_rules(self, plan, allergies, injuries):
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
