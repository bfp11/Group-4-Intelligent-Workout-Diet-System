# Intelligent Workout & Diet System — Backend

This is the backend service for **Group 4’s Intelligent Workout and Diet Planning System**, a health and wellness web app that generates personalized meal and workout plans using AI.  
It integrates with OpenAI’s GPT model and applies safety rules (like avoiding allergens and injury-related workouts) before returning a final plan.

---

## Backend Overview

The backend is built using **FastAPI** and includes:
- An **LLM service** (`llm_service.py`) that generates meal and workout plans via the OpenAI API.
- A **Rules Engine** (`rules_engine.py`) that filters unsafe foods or exercises.
- A **FastAPI server** (`main.py`) that exposes an API endpoint `/generate-plan`.

You can run it locally and interact through FastAPI’s built-in Swagger UI at [http://127.0.0.1:8000/docs]

---

## Folder Structure

backend/
│
├── main.py             # FastAPI entry point and API routes
├── llm_service.py      # Handles OpenAI-based plan generation
├── rules_engine.py     # Applies safety filters for allergies/injuries
├── requirements.txt    # Python dependencies
├── **init**.py         # Marks the folder as a package
└── .env                # Contains your OpenAI API key (not tracked by Git)


## Prerequisites

Before starting, make sure you have:
- **Python 3.12 or newer**
- **Pip** (installed automatically with Python)
- An **OpenAI API key** (you can create one at [https://platform.openai.com]

## Setup Instructions

### 1. Clone the repository
git clone https://github.com/<your-team-repo>/Group-4-Intelligent-Workout-Diet-System.git
cd Group-4-Intelligent-Workout-Diet-System

### 2. Navigate to the backend folder

cd backend

### 3. Create a virtual environment

This isolates your dependencies so they don’t affect global Python packages.

python -m venv venv

### 4. Activate the virtual environment

**Mac/Linux:**

source venv/bin/activate

**Windows:**

venv\Scripts\activate

You’ll know it worked when you see `(venv)` before your terminal prompt.

### 5. Install dependencies

All required libraries (FastAPI, OpenAI SDK, Uvicorn, etc.) are listed in `requirements.txt`.

pip install -r requirements.txt

### 6. Set your environment variables

Create a `.env` file inside the `backend/` folder:

OPENAI_API_KEY=your_api_key_here

### 7. Run the FastAPI server

Start the backend server using Uvicorn:

python -m uvicorn backend.main:app --reload

If successful, you’ll see something like:

INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.

---

## 🧪 Testing the Plan Generation API

1. Open your browser and go to:
   [http://127.0.0.1:8000/docs]

2. Click on the `POST /generate-plan` endpoint.

3. Click **“Try it out”**, then enter this example JSON:

{
  "goal": "build muscle",
  "allergies": ["peanuts"],
  "injuries": ["knee"]
}

4. Click **Execute**.
   You should receive a response like:

{
  "goal": "build muscle",
  "safe_plan": {
    "meals": [
      {"name": "Grilled Chicken Breast with Quinoa", "calories": 450},
      {"name": "Greek Yogurt with Berries", "calories": 200}
    ],
    "workouts": [
      {"name": "Bench Press", "duration": "3 sets of 8-10"},
      {"name": "Plank", "duration": "3 sets of 30 seconds"}
    ]
  },
  "replacements_made": {
    "meals": [],
    "workouts": []
  }
}

If you include allergies like `"peanuts"` or injuries like `"wrist"`,
the `rules_engine.py` filters out those items automatically.

* The backend currently runs locally only, but it’s structured to deploy to a cloud platform later (like Render, Vercel, or AWS Lambda).

* To test endpoints via code (instead of Swagger UI), you can use:

  curl -X POST "http://127.0.0.1:8000/generate-plan" \
  -H "Content-Type: application/json" \
  -d '{"goal": "lose weight", "allergies": ["fish"], "injuries": ["shoulder"]}
