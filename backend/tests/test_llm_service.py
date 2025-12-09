# backend/tests/test_llm_service.py
"""
Unit tests for LLM service (OpenAI integration)
Testing the most critical component for plan generation
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from llm_service import (
    generate_plan_from_llm,
    validate_exercise_safety,
    suggest_food_replacement,
    suggest_exercise_replacement,
    _safe_json_from_model_content
)

class TestLLMService:
    """Test suite for LLM service functionality"""
    
    def test_safe_json_from_model_content_clean_json(self):
        """Test parsing clean JSON without markdown fences"""
        content = '{"meals": [], "workouts": []}'
        result = _safe_json_from_model_content(content)
        assert result == {"meals": [], "workouts": []}
    
    def test_safe_json_from_model_content_with_fences(self):
        """Test parsing JSON wrapped in markdown code fences"""
        content = '```json\n{"meals": [], "workouts": []}\n```'
        result = _safe_json_from_model_content(content)
        assert result == {"meals": [], "workouts": []}
    
    def test_safe_json_from_model_content_with_mixed_fences(self):
        """Test parsing JSON with multiple fence blocks"""
        content = '```\nSome text\n```\n```json\n{"meals": [], "workouts": []}\n```'
        result = _safe_json_from_model_content(content)
        assert result == {"meals": [], "workouts": []}
    
    @patch('llm_service.client.chat.completions.create')
    @patch('llm_service.get_supabase_client')
    def test_generate_plan_from_llm_success(self, mock_supabase, mock_openai):
        """Test successful plan generation with valid LLM response"""
        # Mock database response
        mock_db = MagicMock()
        mock_db.table().select().eq().execute.return_value = MagicMock(
            data=[
                {"name": "Chicken Breast"},
                {"name": "Salmon"},
                {"name": "Push-Ups"},
                {"name": "Squats"}
            ]
        )
        mock_supabase.return_value = mock_db
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "meals": [
                {"name": "Chicken Salad", "calories": 350, "protein": 35, "carbs": 20, "fat": 12},
                {"name": "Scrambled Eggs", "calories": 250, "protein": 18, "carbs": 5, "fat": 15}
            ],
            "workouts": [
                {"name": "Push-Ups", "duration": "3 sets of 12", "estimated_calories": 100},
                {"name": "Squats", "duration": "3 sets of 15", "estimated_calories": 120}
            ]
        })
        mock_openai.return_value = mock_response
        
        # Execute
        result = generate_plan_from_llm(
            goal="build muscle",
            allergies=["peanuts"],
            injuries=[{"name": "knee injury", "severity": "moderate"}]
        )
        
        # Verify
        assert "meals" in result
        assert "workouts" in result
        assert len(result["meals"]) == 2
        assert len(result["workouts"]) == 2
        assert result["meals"][0]["name"] == "Chicken Salad"
        assert result["meals"][0]["calories"] == 350
    
    @patch('llm_service.client.chat.completions.create')
    @patch('llm_service.get_supabase_client')
    def test_generate_plan_removes_duplicates(self, mock_supabase, mock_openai):
        """Test that duplicate meals/workouts are removed"""
        # Mock database
        mock_db = MagicMock()
        mock_db.table().select().eq().execute.return_value = MagicMock(data=[])
        mock_supabase.return_value = mock_db
        
        # Mock OpenAI response with duplicates
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "meals": [
                {"name": "Chicken Salad", "calories": 350, "protein": 35, "carbs": 20, "fat": 12},
                {"name": "Chicken Salad", "calories": 350, "protein": 35, "carbs": 20, "fat": 12},  # Duplicate
                {"name": "Greek Yogurt", "calories": 150, "protein": 15, "carbs": 20, "fat": 2}
            ],
            "workouts": [
                {"name": "Push-Ups", "duration": "3 sets of 12", "estimated_calories": 100},
                {"name": "Push-Ups", "duration": "3 sets of 10", "estimated_calories": 90},  # Duplicate
                {"name": "Squats", "duration": "3 sets of 15", "estimated_calories": 120}
            ]
        })
        mock_openai.return_value = mock_response
        
        # Execute
        result = generate_plan_from_llm(
            goal="lose weight",
            allergies=[],
            injuries=[]
        )
        
        # Verify duplicates removed
        assert len(result["meals"]) == 2  # Not 3
        assert len(result["workouts"]) == 2  # Not 3
        
        # Verify names are unique
        meal_names = [m["name"].lower() for m in result["meals"]]
        workout_names = [w["name"].lower() for w in result["workouts"]]
        assert len(meal_names) == len(set(meal_names))
        assert len(workout_names) == len(set(workout_names))
    
    @patch('llm_service.client.chat.completions.create')
    @patch('llm_service.get_supabase_client')
    def test_generate_plan_adds_default_values(self, mock_supabase, mock_openai):
        """Test that missing nutritional values get defaults"""
        # Mock database
        mock_db = MagicMock()
        mock_db.table().select().eq().execute.return_value = MagicMock(data=[])
        mock_supabase.return_value = mock_db
        
        # Mock OpenAI response with missing values
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "meals": [
                {"name": "Chicken Salad", "calories": 350}  # Missing protein, carbs, fat
            ],
            "workouts": [
                {"name": "Push-Ups"}  # Missing duration, estimated_calories
            ]
        })
        mock_openai.return_value = mock_response
        
        # Execute
        result = generate_plan_from_llm(
            goal="build muscle",
            allergies=[],
            injuries=[]
        )
        
        # Verify defaults added
        assert result["meals"][0]["protein"] == 0
        assert result["meals"][0]["carbs"] == 0
        assert result["meals"][0]["fat"] == 0
        assert result["workouts"][0]["duration"] == "30 minutes"
        assert result["workouts"][0]["estimated_calories"] == 200
    
    @patch('llm_service.client.chat.completions.create')
    def test_validate_exercise_safety_returns_true(self, mock_openai):
        """Test exercise validation returns true for safe exercises"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "safe"
        mock_openai.return_value = mock_response
        
        result = validate_exercise_safety(
            "Running",
            [{"name": "wrist pain", "severity": "mild"}],
            "lose weight"
        )
        
        assert result is True
    
    @patch('llm_service.client.chat.completions.create')
    def test_validate_exercise_safety_returns_false(self, mock_openai):
        """Test exercise validation returns false for unsafe exercises"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "unsafe"
        mock_openai.return_value = mock_response
        
        result = validate_exercise_safety(
            "Squats",
            [{"name": "knee injury", "severity": "severe"}],
            "build muscle"
        )
        
        assert result is False
    
    @patch('llm_service.client.chat.completions.create')
    def test_suggest_food_replacement(self, mock_openai):
        """Test food replacement suggestion returns valid structure"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "name": "Almond Milk Smoothie",
            "calories": 180,
            "protein": 8,
            "carbs": 25,
            "fat": 6
        })
        mock_openai.return_value = mock_response
        
        result = suggest_food_replacement(
            "Greek Yogurt",
            "dairy",
            "lose weight"
        )
        
        assert result["name"] == "Almond Milk Smoothie"
        assert result["calories"] == 180
        assert "protein" in result
        assert "carbs" in result
        assert "fat" in result
    
    @patch('llm_service.client.chat.completions.create')
    def test_suggest_exercise_replacement(self, mock_openai):
        """Test exercise replacement suggestion returns valid structure"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "name": "Glute Bridge",
            "duration": "3 sets of 15",
            "estimated_calories": 90
        })
        mock_openai.return_value = mock_response
        
        result = suggest_exercise_replacement(
            "Squats",
            [{"name": "knee injury", "severity": "moderate"}],
            "build muscle"
        )
        
        assert result["name"] == "Glute Bridge"
        assert result["duration"] == "3 sets of 15"
        assert result["estimated_calories"] == 90
    
    @patch('llm_service.client.chat.completions.create')
    @patch('llm_service.get_supabase_client')
    def test_generate_plan_handles_api_error(self, mock_supabase, mock_openai):
        """Test graceful handling of OpenAI API errors"""
        # Mock database
        mock_db = MagicMock()
        mock_db.table().select().eq().execute.return_value = MagicMock(data=[])
        mock_supabase.return_value = mock_db
        
        # Mock API error
        mock_openai.side_effect = Exception("API Error")
        
        # Execute
        result = generate_plan_from_llm(
            goal="build muscle",
            allergies=[],
            injuries=[]
        )
        
        # Verify error response
        assert "error" in result
        assert "API Error" in result["error"]