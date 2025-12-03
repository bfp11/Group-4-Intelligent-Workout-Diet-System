# Group-4-Intelligent-Workout-Diet-System

Group 4's project repository for the Intelligent Workout and Diet Planning System — a health and wellness web app that generates personalized workout and nutrition plans using AI and safety-based rules.

## 📋 Overview

The Intelligent Workout and Diet Planning System is a web application that generates personalized workout and nutrition plans based on user goals, medical history, injuries, and dietary restrictions. It uses a Large Language Model (LLM) to create draft plans that are refined by a rules engine to ensure safety and personalization.

The system features real-time AI plan generation, automatic safety checks for allergies and injuries, and smart substitution recommendations powered by OpenAI GPT-4 and Supabase.

## 🎯 Features

- **AI-Powered Plan Generation** – Creates personalized workouts and meals using OpenAI GPT-4o-mini
- **Safety-First Design** – Automatic detection and replacement of unsafe foods and exercises
- **Smart Substitutions** – Database-driven + AI-powered replacement system
- **Real-Time Validation** – Checks allergies and injury contraindications
- **Transparent Replacements** – Shows what was changed and why
- **Modern UI** – Clean, responsive React interface with Tailwind CSS
- **Persistent Storage** – Supabase PostgreSQL database for all data

## 🏗️ System Architecture

1. **Frontend (React + Vite)** – User interface for input and plan display
2. **Backend (FastAPI)** – Handles requests, validation, and business logic
3. **Database (Supabase PostgreSQL)** – Stores foods, exercises, and substitution rules
4. **LLM Integration (OpenAI API)** – Generates draft plans for review
5. **Rules Engine** – Checks and filters unsafe or invalid recommendations

## 📁 Folder Structure

```
Group-4-Intelligent-Workout-Diet-System/
│
├── frontend/               # React UI components and pages
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── api.js         # API service layer
│   │   └── main.jsx       # React app entry point
│   └── pages/             # Page components
│
├── backend/               # FastAPI backend
│   ├── main.py           # API routes and endpoints
│   ├── database.py       # Supabase connection
│   ├── rules_engine.py   # Safety rules and substitution logic
│   ├── llm_service.py    # OpenAI API integration
│   └── requirements.txt  # Python dependencies
│
├── docs/                 # Documentation and reports
├── .gitignore
├── README.md
└── LICENSE
```

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key
- Supabase account

### 1. Clone the repository
```bash
git clone https://github.com/bfp11/Group-4-Intelligent-Workout-Diet-System.git
cd Group-4-Intelligent-Workout-Diet-System
git checkout full-project
```

### 2. Set up Supabase Database

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run the database setup script
3. Get your Project URL and anon key from Settings → API

### 3. Configure Backend
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
```

Create `backend/.env` with:

```env
OPENAI_API_KEY=your_openai_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

### 4. Configure Frontend
```bash
cd frontend
npm install
```

### 5. Run the Application
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Access the Application

Open your browser to: **http://localhost:5173/plans**

## 🎮 Usage

1. Navigate to http://localhost:5173/plans
2. Fill out the form:
   - **Goal:** Your fitness objective (e.g., "lose weight", "build muscle")
   - **Allergies:** Comma-separated list (e.g., "peanuts, dairy")
   - **Injuries:** Comma-separated list (e.g., "knee injury")
3. Click **"Generate Plan"**
4. View your personalized workout and meal plan with safety replacements

## 👥 Team Members

| Name | Role | Responsibilities |
|------|------|------------------|
| Ethan Whittle | Database Developer | Schema design, Supabase integration, SQL optimization |
| Micah Thompson | Frontend Developer | UI design, React components, user experience |
| Jordan Trevino | Backend Developer | API development, LLM integration, rules engine |
| Erick Bardales | Project Manager | Documentation, coordination, testing |

## 🧩 Tech Stack

### Frontend
- **Framework:** React 19 with Vite
- **Styling:** Tailwind CSS 4.1
- **Routing:** React Router DOM
- **HTTP Client:** Fetch API

### Backend
- **Framework:** FastAPI (Python)
- **AI Model:** OpenAI GPT-4o-mini
- **Database Client:** Supabase Python SDK
- **Server:** Uvicorn (ASGI)

### Database
- **Provider:** Supabase (PostgreSQL)
- **Key Features:** Row Level Security, Real-time subscriptions, Auto-generated REST API

### External APIs
- **OpenAI API** – GPT-4o-mini for plan generation
- **Supabase API** – Database and authentication

## 🔌 API Endpoints

### Backend (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Detailed health status |
| `POST` | `/generate-plan` | Generate AI workout & meal plan |

### Example Request
```bash
curl -X POST "http://localhost:8000/generate-plan" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "build muscle",
    "allergies": ["peanuts"],
    "injuries": ["knee injury"]
  }'
```

## 🗄️ Database Schema

### Key Tables

- **food_items** – Available foods with nutritional info and allergens (15+ items)
- **exercise_items** – Available exercises with contraindications (15+ items)
- **food_substitutions** – Safety replacement rules for allergenic foods
- **exercise_substitutions** – Safety replacement rules for contraindicated exercises
- **plans** – User-generated workout and meal plans
- **plan_meals** – Individual meals within plans
- **plan_workouts** – Individual workouts within plans

## 🎯 How It Works

1. **User Input** – User fills form with fitness goal, allergies, and injuries
2. **AI Generation** – Backend sends request to OpenAI GPT-4o-mini with available foods/exercises
3. **Safety Validation** – Rules engine checks each meal and workout against user constraints
4. **Smart Substitutions** – Unsafe items replaced using database rules or AI recommendations
5. **Response** – Safe plan returned with detailed replacement tracking

## 🐛 Troubleshooting

### Backend Issues

**Error:** `OPENAI_API_KEY not set`
- Check `backend/.env` file exists with correct format (no quotes)
- Restart backend after changing `.env`

**Error:** `SUPABASE_URL and SUPABASE_KEY must be set`
- Verify `.env` has all three variables
- Use the **anon public** key, not service_role key

**Error:** `ModuleNotFoundError: No module named 'backend'`
- Run from backend folder: `cd backend && uvicorn main:app --reload`
- Imports should not have `backend.` prefix

### Frontend Issues

**Blank white screen**
- Check browser console (F12) for errors
- Verify backend is running on port 8000

**"Failed to generate plan"**
- Ensure both backend and frontend are running
- Check CORS is enabled in `backend/main.py`

## 🧪 Testing

### Manual Testing
1. Start both backend and frontend servers
2. Navigate to http://localhost:5173/plans
3. Test with various combinations of goals, allergies, and injuries
4. Verify safety replacements appear correctly

### API Testing
Visit http://127.0.0.1:8000/docs for interactive API documentation

---

## 🚀 Future Improvements

- **User Authentication** – Add login and profile management
- **Plan History** – Save and view past generated plans
- **Progress Tracking** – Monitor user fitness and nutrition progress over time
- **Analytics Dashboard** – Visualize trends and achievements
- **Wearable Integration** – Connect with fitness trackers
- **Mobile App** – Native iOS and Android applications
- **Social Features** – Share plans and compete with friends
- **Meal Prep Guides** – Detailed cooking instructions
- **Video Tutorials** – Exercise demonstration videos

## 📝 Known Limitations

- No user authentication (planned for future)
- Plans not persisted to user history yet
- Limited food and exercise database (15 of each)
- Substitution rules need expansion for more variety
- No mobile optimization yet

## 🤝 Contributing

This is a CS4398 Software Engineering course project by Group 4.

### Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and test locally
3. Commit: `git commit -m "Description of changes"`
4. Push: `git push origin feature/your-feature`
5. Create a Pull Request on GitHub

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Supabase Documentation](https://supabase.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
