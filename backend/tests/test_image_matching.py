# backend/tests/test_image_matching.py
"""
Unit tests for smart image matching algorithm
Testing keyword-based image selection
"""
import pytest
from utils.images import get_smart_food_image, get_smart_exercise_image

class TestImageMatching:
    """Test suite for smart image matching algorithms"""
    
    # FOOD IMAGE MATCHING TESTS
    
    def test_food_image_chicken_keyword(self):
        """Test chicken keyword matches correctly"""
        url = get_smart_food_image("Grilled Chicken Salad")
        assert "2338407" in url  # Chicken image ID
    
    def test_food_image_salmon_keyword(self):
        """Test salmon keyword matches correctly"""
        url = get_smart_food_image("Baked Salmon with Vegetables")
        assert "2374946" in url  # Salmon image ID
    
    def test_food_image_yogurt_keyword(self):
        """Test yogurt keyword matches correctly"""
        url = get_smart_food_image("Greek Yogurt with Berries")
        assert "2992308" in url  # Yogurt image ID
    
    def test_food_image_egg_keyword(self):
        """Test egg keyword matches correctly"""
        url = get_smart_food_image("Scrambled Eggs with Spinach")
        assert "4397063" in url  # Egg image ID
    
    def test_food_image_quinoa_keyword(self):
        """Test quinoa/grain keyword matches correctly"""
        url = get_smart_food_image("Quinoa Bowl with Vegetables")
        assert "4224259" in url  # Grain image ID
    
    def test_food_image_case_insensitive(self):
        """Test matching is case-insensitive"""
        url1 = get_smart_food_image("CHICKEN SALAD")
        url2 = get_smart_food_image("chicken salad")
        url3 = get_smart_food_image("Chicken Salad")
        
        assert url1 == url2 == url3
    
    def test_food_image_multiple_keywords_first_wins(self):
        """Test that first matching keyword takes priority"""
        # "Peanut butter banana smoothie" has both peanut and banana
        url = get_smart_food_image("Peanut Butter Banana Smoothie")
        
        # Should match "peanut" first (nut category)
        assert "1295572" in url  # Nut image ID (not fruit)
    
    def test_food_image_default_fallback(self):
        """Test unknown food gets default image"""
        url = get_smart_food_image("Mysterious Unknown Food Item")
        assert "1640777" in url  # Default food image ID
    
    def test_food_image_partial_match(self):
        """Test partial keyword matching works"""
        url = get_smart_food_image("Turkey Breast Sandwich")
        assert "2338407" in url  # Should match turkey → chicken category
    
    # EXERCISE IMAGE MATCHING TESTS
    
    def test_exercise_image_pushup_keyword(self):
        """Test push-up keyword matches correctly"""
        url = get_smart_exercise_image("Push-Ups")
        assert "4162487" in url  # Push-up image ID
    
    def test_exercise_image_squat_keyword(self):
        """Test squat keyword matches correctly"""
        url = get_smart_exercise_image("Barbell Squats")
        assert "1552106" in url  # Squat image ID
    
    def test_exercise_image_plank_keyword(self):
        """Test plank keyword matches correctly"""
        url = get_smart_exercise_image("Plank Hold")
        assert "6740309" in url  # Plank image ID
    
    def test_exercise_image_running_keyword(self):
        """Test running keyword matches correctly"""
        url = get_smart_exercise_image("30 Minute Running")
        assert "1954524" in url  # Running image ID
    
    def test_exercise_image_row_keyword(self):
        """Test row keyword matches correctly"""
        url = get_smart_exercise_image("Seated Row Machine")
        assert "6389869" in url  # Rowing image ID
    
    def test_exercise_image_compound_name(self):
        """Test exercise with multiple words matches correctly"""
        url = get_smart_exercise_image("Incline Dumbbell Bench Press")
        assert "3837757" in url  # Should match "bench press"
    
    def test_exercise_image_case_insensitive(self):
        """Test matching is case-insensitive"""
        url1 = get_smart_exercise_image("PUSH-UPS")
        url2 = get_smart_exercise_image("push-ups")
        url3 = get_smart_exercise_image("Push-Ups")
        
        assert url1 == url2 == url3
    
    def test_exercise_image_default_fallback(self):
        """Test unknown exercise gets default image"""
        url = get_smart_exercise_image("Mysterious Unknown Exercise")
        assert "4720574" in url  # Default workout image ID
    
    def test_exercise_image_specific_over_generic(self):
        """Test specific keywords take priority over generic"""
        # "Shoulder press" should match shoulder category, not generic dumbbell
        url = get_smart_exercise_image("Dumbbell Shoulder Press")
        assert "5327476" in url  # Shoulder exercise (not generic dumbbell)
    
    def test_exercise_image_with_variation(self):
        """Test exercise variations match base exercise"""
        url1 = get_smart_exercise_image("Standard Push-Ups")
        url2 = get_smart_exercise_image("Diamond Push-Ups")
        url3 = get_smart_exercise_image("Wide Push-Ups")
        
        # All should match push-up category
        assert url1 == url2 == url3
    
    # EDGE CASES
    
    def test_food_image_empty_string(self):
        """Test empty string returns default"""
        url = get_smart_food_image("")
        assert "1640777" in url  # Default
    
    def test_exercise_image_empty_string(self):
        """Test empty string returns default"""
        url = get_smart_exercise_image("")
        assert "4720574" in url  # Default
    
    def test_food_image_special_characters(self):
        """Test handling of special characters"""
        url = get_smart_food_image("Chicken & Rice (w/ Vegetables)")
        assert "2338407" in url  # Should still match chicken
    
    def test_exercise_image_numbers_in_name(self):
        """Test handling of numbers in exercise name"""
        url = get_smart_exercise_image("100 Push-Ups Challenge")
        assert "4162487" in url  # Should still match push-up