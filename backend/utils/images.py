# backend/utils/images.py
# Smart image matching logic for food and exercise items

def get_smart_food_image(food_name: str) -> str:
    """Get appropriate food image using smart keyword matching"""
    name_lower = food_name.lower()
    
    # Chicken/Turkey
    if any(word in name_lower for word in ['chicken', 'turkey']):
        return 'https://images.pexels.com/photos/2338407/pexels-photo-2338407.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Salmon/Fish
    if any(word in name_lower for word in ['salmon', 'fish', 'tuna']):
        return 'https://images.pexels.com/photos/2374946/pexels-photo-2374946.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Tofu/Plant-based
    if any(word in name_lower for word in ['tofu', 'tempeh', 'seitan']):
        return 'https://images.pexels.com/photos/4518604/pexels-photo-4518604.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Grains (Quinoa, Rice, Oats)
    if any(word in name_lower for word in ['quinoa', 'rice', 'oat', 'oatmeal', 'grain', 'bowl', 'lentil']):
        return 'https://images.pexels.com/photos/4224259/pexels-photo-4224259.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Yogurt/Dairy
    if any(word in name_lower for word in ['yogurt', 'milk', 'cheese', 'cottage cheese', 'greek yogurt']):
        return 'https://images.pexels.com/photos/2992308/pexels-photo-2992308.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Eggs
    if 'egg' in name_lower:
        return 'https://images.pexels.com/photos/4397063/pexels-photo-4397063.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Vegetables
    if any(word in name_lower for word in ['vegetable', 'broccoli', 'spinach', 'kale', 'salad', 'greens', 'carrot', 'pepper']):
        return 'https://images.pexels.com/photos/6465182/pexels-photo-6465182.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Nuts/Seeds/Butter
    if any(word in name_lower for word in ['almond', 'nut', 'peanut', 'seed', 'butter', 'cashew', 'walnut']):
        return 'https://images.pexels.com/photos/1295572/pexels-photo-1295572.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Fruits/Berries
    if any(word in name_lower for word in ['fruit', 'berry', 'berries', 'apple', 'banana', 'strawberry', 'blueberry']):
        return 'https://images.pexels.com/photos/1132047/pexels-photo-1132047.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Sweet Potato
    if 'sweet potato' in name_lower or 'potato' in name_lower:
        return 'https://images.pexels.com/photos/7456548/pexels-photo-7456548.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Avocado
    if 'avocado' in name_lower:
        return 'https://images.pexels.com/photos/557659/pexels-photo-557659.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Pasta
    if 'pasta' in name_lower:
        return 'https://images.pexels.com/photos/1437267/pexels-photo-1437267.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Default food image
    return 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=800'


def get_smart_exercise_image(exercise_name: str) -> str:
    """Get appropriate exercise image using smart keyword matching"""
    name_lower = exercise_name.lower()
    
    # Bench Press
    if any(word in name_lower for word in ['bench press', 'chest press', 'incline press', 'decline press']):
        return 'https://images.pexels.com/photos/3837757/pexels-photo-3837757.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Shoulder exercises
    if any(word in name_lower for word in ['shoulder press', 'overhead press', 'military press', 'lateral raise', 'shoulder raise']):
        return 'https://images.pexels.com/photos/5327476/pexels-photo-5327476.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Push-ups
    if 'push' in name_lower and ('up' in name_lower or 'pushup' in name_lower):
        return 'https://images.pexels.com/photos/4162487/pexels-photo-4162487.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Deadlifts
    if 'deadlift' in name_lower:
        return 'https://images.pexels.com/photos/1552103/pexels-photo-1552103.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Squats
    if any(word in name_lower for word in ['squat', 'leg press']):
        return 'https://images.pexels.com/photos/1552106/pexels-photo-1552106.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Lunges
    if 'lunge' in name_lower:
        return 'https://images.pexels.com/photos/29205145/pexels-photo-29205145.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Rows
    if 'row' in name_lower:
        return 'https://images.pexels.com/photos/6389869/pexels-photo-6389869.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Planks and core
    if any(word in name_lower for word in ['plank', 'side plank', 'bridge', 'glute bridge']):
        return 'https://images.pexels.com/photos/6740309/pexels-photo-6740309.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Running
    if any(word in name_lower for word in ['run', 'running', 'jog', 'jogging', 'sprint']):
        return 'https://images.pexels.com/photos/1954524/pexels-photo-1954524.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Biking/Cycling
    if any(word in name_lower for word in ['bike', 'biking', 'bicycle', 'cycling', 'cycle', 'spin']):
        return 'https://images.pexels.com/photos/248547/pexels-photo-248547.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Swimming
    if 'swim' in name_lower:
        return 'https://images.pexels.com/photos/863988/pexels-photo-863988.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Burpees
    if 'burpee' in name_lower:
        return 'https://images.pexels.com/photos/6339477/pexels-photo-6339477.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Yoga
    if 'yoga' in name_lower:
        return 'https://images.pexels.com/photos/3823039/pexels-photo-3823039.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Cardio fallback
    if any(word in name_lower for word in ['cardio', 'elliptical', 'stair', 'climbing', 'jump rope', 'jumping']):
        return 'https://images.pexels.com/photos/1552242/pexels-photo-1552242.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Dumbbell/weight training fallback
    if any(word in name_lower for word in ['dumbbell', 'barbell', 'weight', 'curl', 'extension', 'fly', 'raise', 'press', 'pull', 'chin up', 'pull up']):
        return 'https://images.pexels.com/photos/5327476/pexels-photo-5327476.jpeg?auto=compress&cs=tinysrgb&w=800'
    
    # Default workout image
    return 'https://images.pexels.com/photos/4720574/pexels-photo-4720574.jpeg?auto=compress&cs=tinysrgb&w=800'