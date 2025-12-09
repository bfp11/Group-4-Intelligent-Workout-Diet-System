# backend/tests/conftest.py
"""
Shared test fixtures and configuration for pytest
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database import get_supabase_client

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def mock_supabase():
    """Mock Supabase client for database operations"""
    mock_client = MagicMock()
    
    # Mock table() chain
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.update.return_value = mock_table
    mock_table.delete.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.ilike.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=[])
    
    return mock_client

@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "id": "test-user-123",
        "name": "Test User",
        "email": "test@example.com",
        "password_hash": "$2b$12$test_hash_value"
    }

@pytest.fixture
def sample_injuries():
    """Sample injury data for testing"""
    return [
        {"name": "knee injury", "severity": "moderate"},
        {"name": "wrist pain", "severity": "mild"}
    ]

@pytest.fixture
def sample_allergies():
    """Sample allergy data for testing"""
    return ["peanuts", "dairy"]

@pytest.fixture
def sample_llm_response():
    """Sample LLM response for testing"""
    return {
        "meals": [
            {"name": "Grilled Chicken Salad", "calories": 350, "protein": 35, "carbs": 20, "fat": 12},
            {"name": "Scrambled Eggs", "calories": 250, "protein": 18, "carbs": 5, "fat": 15},
            {"name": "Quinoa Bowl", "calories": 300, "protein": 12, "carbs": 45, "fat": 8},
            {"name": "Greek Yogurt", "calories": 150, "protein": 15, "carbs": 20, "fat": 2}
        ],
        "workouts": [
            {"name": "Push-Ups", "duration": "3 sets of 12", "estimated_calories": 100},
            {"name": "Squats", "duration": "3 sets of 15", "estimated_calories": 120},
            {"name": "Plank", "duration": "3 sets of 45 seconds", "estimated_calories": 75},
            {"name": "Running", "duration": "20 minutes", "estimated_calories": 200}
        ]
    }