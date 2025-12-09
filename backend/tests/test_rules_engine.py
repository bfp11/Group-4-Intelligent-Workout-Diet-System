# backend/tests/test_rules_engine.py
"""
Unit tests for Rules Engine (safety validation and substitution)
Testing critical safety logic that prevents unsafe recommendations
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from rules_engine import RulesEngine

class TestRulesEngine:
    """Test suite for rules engine safety validation"""
    
    @pytest.fixture
    def rules_engine(self):
        """Create RulesEngine instance for testing"""
        return RulesEngine()
    
    @pytest.fixture
    def mock_db_client(self, mock_supabase):
        """Mock database client for rules engine"""
        return mock_supabase
    
    def test_check_food_has_allergen_database_match(self, rules_engine, mock_supabase):
        """Test allergen detection through database lookup"""
        # Mock database response with allergen
        mock_supabase.table().select().ilike().limit().execute.return_value = MagicMock(
            data=[{"allergens": ["dairy", "lactose"]}]
        )
        rules_engine.supabase = mock_supabase
        
        has_allergen, allergen = rules_engine.check_food_has_allergen(
            "Greek Yogurt",
            ["dairy", "peanuts"]
        )
        
        assert has_allergen is True
        assert allergen == "dairy"
    
    def test_check_food_has_allergen_no_match(self, rules_engine, mock_supabase):
        """Test no allergen detection when food is safe"""
        # Mock database response without allergen
        mock_supabase.table().select().ilike().limit().execute.return_value = MagicMock(
            data=[{"allergens": ["gluten"]}]
        )
        rules_engine.supabase = mock_supabase
        
        has_allergen, allergen = rules_engine.check_food_has_allergen(
            "Chicken Breast",
            ["dairy", "peanuts"]
        )
        
        assert has_allergen is False
        assert allergen is None
    
    def test_check_food_has_allergen_fallback_name_matching(self, rules_engine, mock_supabase):
        """Test fallback to name-based matching when database has no entry"""
        # Mock empty database response
        mock_supabase.table().select().ilike().limit().execute.return_value = MagicMock(
            data=[]
        )
        rules_engine.supabase = mock_supabase
        
        # Food name contains allergen
        has_allergen, allergen = rules_engine.check_food_has_allergen(
            "Peanut Butter Smoothie",
            ["peanuts", "dairy"]
        )
        
        assert has_allergen is True
        assert allergen == "peanuts"
    
    def test_check_exercise_has_contraindication_database_match(self, rules_engine, mock_supabase):
        """Test contraindication detection through database lookup"""
        # Mock database response with contraindication
        mock_supabase.table().select().ilike().limit().execute.return_value = MagicMock(
            data=[{"contraindications": ["knee injury", "knee pain"]}]
        )
        rules_engine.supabase = mock_supabase
        
        has_contra, injury = rules_engine.check_exercise_has_contraindication(
            "Squats",
            ["knee injury", "wrist pain"]
        )
        
        assert has_contra is True
        assert injury == "knee injury"
    
    def test_check_exercise_has_contraindication_no_match(self, rules_engine, mock_supabase):
        """Test no contraindication when exercise is safe"""
        # Mock database response without contraindication
        mock_supabase.table().select().ilike().limit().execute.return_value = MagicMock(
            data=[{"contraindications": ["shoulder injury"]}]
        )
        rules_engine.supabase = mock_supabase
        
        has_contra, injury = rules_engine.check_exercise_has_contraindication(
            "Running",
            ["knee injury", "wrist pain"]
        )
        
        assert has_contra is False
        assert injury is None
    
    @patch('rules_engine.suggest_food_replacement')
    def test_apply_allergy_rule_replaces_unsafe_meal(self, mock_suggest, rules_engine, mock_supabase):
        """Test that unsafe meals are replaced with safe alternatives"""
        # Setup
        meals = [
            {"name": "Greek Yogurt", "calories": 150, "protein": 15, "carbs": 20, "fat": 2},
            {"name": "Chicken Salad", "calories": 350, "protein": 35, "carbs": 20, "fat": 12}
        ]
        allergies = ["dairy"]
        
        # Mock database - yogurt has dairy, chicken doesn't
        def mock_db_response(*args, **kwargs):
            if "Greek Yogurt" in str(args):
                return MagicMock(data=[{"allergens": ["dairy", "lactose"]}])
            else:
                return MagicMock(data=[{"allergens": []}])
        
        mock_supabase.table().select().ilike().limit().execute.side_effect = mock_db_response
        rules_engine.supabase = mock_supabase
        
        # Mock LLM replacement
        mock_suggest.return_value = {
            "name": "Almond Milk Smoothie",
            "calories": 180,
            "protein": 8,
            "carbs": 25,
            "fat": 6
        }
        
        # Execute
        safe_meals, replacements = rules_engine.apply_allergy_rule(
            meals, allergies, "lose weight"
        )
        
        # Verify
        assert len(safe_meals) == 2
        assert safe_meals[0]["name"] == "Almond Milk Smoothie"  # Replaced
        assert safe_meals[1]["name"] == "Chicken Salad"  # Kept
        assert len(replacements) == 1
        assert replacements[0]["replaced"] == "Greek Yogurt"
        assert replacements[0]["with"] == "Almond Milk Smoothie"
        assert "dairy allergy" in replacements[0]["reason"]
    
    @patch('rules_engine.validate_exercise_safety')
    @patch('rules_engine.suggest_exercise_replacement')
    def test_apply_injury_rule_replaces_unsafe_workout(self, mock_suggest, mock_validate, rules_engine, mock_supabase):
        """Test that unsafe workouts are replaced with safe alternatives"""
        # Setup
        workouts = [
            {"name": "Squats", "duration": "3 sets of 15", "estimated_calories": 120},
            {"name": "Push-Ups", "duration": "3 sets of 12", "estimated_calories": 100}
        ]
        injuries = [{"name": "knee injury", "severity": "moderate"}]
        
        # Mock database - squats have knee contraindication
        def mock_db_response(*args, **kwargs):
            if "Squats" in str(args):
                return MagicMock(data=[{"contraindications": ["knee injury", "knee pain"]}])
            else:
                return MagicMock(data=[{"contraindications": []}])
        
        mock_supabase.table().select().ilike().limit().execute.side_effect = mock_db_response
        rules_engine.supabase = mock_supabase
        
        # Mock LLM validation and replacement
        mock_validate.return_value = True  # Push-ups are safe
        mock_suggest.return_value = {
            "name": "Glute Bridge",
            "duration": "3 sets of 15",
            "estimated_calories": 90
        }
        
        # Execute
        safe_workouts, replacements = rules_engine.apply_injury_rule(
            workouts, injuries, "build muscle"
        )
        
        # Verify
        assert len(safe_workouts) == 2
        assert safe_workouts[0]["name"] == "Glute Bridge"  # Replaced
        assert safe_workouts[1]["name"] == "Push-Ups"  # Kept
        assert len(replacements) == 1
        assert replacements[0]["replaced"] == "Squats"
        assert replacements[0]["with"] == "Glute Bridge"
    
    @patch('rules_engine.suggest_exercise_replacement')
    def test_apply_injury_rule_prevents_duplicate_replacements(self, mock_suggest, rules_engine, mock_supabase):
        """Test that duplicate replacement names are retried"""
        # Setup - two unsafe workouts
        workouts = [
            {"name": "Squats", "duration": "3 sets of 15", "estimated_calories": 120},
            {"name": "Lunges", "duration": "3 sets of 12", "estimated_calories": 110}
        ]
        injuries = [{"name": "knee injury", "severity": "severe"}]
        
        # Mock database - both have knee contraindication
        mock_supabase.table().select().ilike().limit().execute.return_value = MagicMock(
            data=[{"contraindications": ["knee injury"]}]
        )
        rules_engine.supabase = mock_supabase
        
        # Mock LLM - first tries to return same replacement twice
        mock_suggest.side_effect = [
            {"name": "Glute Bridge", "duration": "3 sets of 15", "estimated_calories": 90},
            {"name": "Glute Bridge", "duration": "3 sets of 12", "estimated_calories": 85},  # Duplicate!
            {"name": "Hip Thrust", "duration": "3 sets of 12", "estimated_calories": 95}   # Different (retry success)
        ]
        
        # Execute
        safe_workouts, replacements = rules_engine.apply_injury_rule(
            workouts, injuries, "build muscle"
        )
        
        # Verify no duplicates
        workout_names = [w["name"] for w in safe_workouts]
        assert len(workout_names) == len(set(workout_names))
        assert "Glute Bridge" in workout_names
        assert "Hip Thrust" in workout_names
    
    def test_apply_injury_rule_severity_based_filtering(self, rules_engine, mock_supabase):
        """Test that severity-based heuristic rules work correctly"""
        # Setup
        workouts = [
            {"name": "Squats", "duration": "3 sets of 15", "estimated_calories": 120},
            {"name": "Leg Press", "duration": "3 sets of 12", "estimated_calories": 130}
        ]
        injuries = [{"name": "knee", "severity": "severe"}]  # SEVERE knee injury
        
        # Mock empty database (testing heuristic rules)
        mock_supabase.table().select().ilike().limit().execute.return_value = MagicMock(
            data=[]
        )
        rules_engine.supabase = mock_supabase
        
        # Mock LLM replacement (won't be called if database substitution works)
        with patch('rules_engine.suggest_exercise_replacement') as mock_suggest:
            mock_suggest.return_value = {
                "name": "Arm Curls",
                "duration": "3 sets of 12",
                "estimated_calories": 80
            }
            
            # Execute
            safe_workouts, replacements = rules_engine.apply_injury_rule(
                workouts, injuries, "build muscle"
            )
            
            # Verify both leg exercises were replaced (severe knee injury)
            assert len(safe_workouts) == 2
            assert "Squats" not in [w["name"] for w in safe_workouts]
            assert "Leg Press" not in [w["name"] for w in safe_workouts]
            assert len(replacements) == 2
    
    @patch('rules_engine.suggest_food_replacement')
    @patch('rules_engine.suggest_exercise_replacement')
    def test_apply_rules_full_integration(self, mock_exercise_suggest, mock_food_suggest, rules_engine, mock_supabase):
        """Test full rules engine integration (meals + workouts)"""
        # Setup plan with unsafe items
        plan = {
            "meals": [
                {"name": "Greek Yogurt", "calories": 150, "protein": 15, "carbs": 20, "fat": 2},
                {"name": "Peanut Butter Toast", "calories": 300, "protein": 12, "carbs": 35, "fat": 14}
            ],
            "workouts": [
                {"name": "Squats", "duration": "3 sets of 15", "estimated_calories": 120},
                {"name": "Bench Press", "duration": "3 sets of 10", "estimated_calories": 140}
            ]
        }
        
        goal = "lose weight"
        allergies = ["dairy", "peanuts"]
        injuries = [{"name": "knee injury", "severity": "moderate"}]
        
        # Mock database responses
        def mock_db_side_effect(*args, **kwargs):
            query_str = str(args) if args else str(kwargs)
            if "Greek Yogurt" in query_str or "yogurt" in query_str.lower():
                return MagicMock(data=[{"allergens": ["dairy"]}])
            elif "Peanut" in query_str or "peanut" in query_str.lower():
                return MagicMock(data=[{"allergens": ["peanuts", "nuts"]}])
            elif "Squats" in query_str or "squat" in query_str.lower():
                return MagicMock(data=[{"contraindications": ["knee injury"]}])
            else:
                return MagicMock(data=[])
        
        mock_supabase.table().select().ilike().limit().execute.side_effect = mock_db_side_effect
        mock_supabase.table().select().eq().execute.side_effect = mock_db_side_effect
        rules_engine.supabase = mock_supabase
        
        # Mock LLM replacements
        mock_food_suggest.side_effect = [
            {"name": "Almond Milk", "calories": 60, "protein": 1, "carbs": 8, "fat": 3},
            {"name": "Sunflower Seed Butter Toast", "calories": 280, "protein": 10, "carbs": 32, "fat": 12}
        ]
        mock_exercise_suggest.return_value = {
            "name": "Glute Bridge",
            "duration": "3 sets of 15",
            "estimated_calories": 90
        }
        
        # Mock validate_exercise_safety for bench press
        with patch('rules_engine.validate_exercise_safety', return_value=True):
            # Execute
            result = rules_engine.apply_rules(plan, goal, allergies, injuries)
        
        # Verify
        assert len(result["meals"]) == 2
        assert result["meals"][0]["name"] == "Almond Milk"  # Yogurt replaced
        assert result["meals"][1]["name"] == "Sunflower Seed Butter Toast"  # PB replaced
        
        assert len(result["workouts"]) == 2
        assert result["workouts"][0]["name"] == "Glute Bridge"  # Squats replaced
        assert result["workouts"][1]["name"] == "Bench Press"  # Kept (safe)
        
        assert len(result["replacements"]["meals"]) == 2
        assert len(result["replacements"]["workouts"]) == 1