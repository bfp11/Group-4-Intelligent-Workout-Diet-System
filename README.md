# Group-4-Intelligent-Workout-Diet-System
Group 4’s project repository for the Intelligent Workout and Diet Planning System — a health and wellness web app that generates personalized workout and nutrition plans using AI and safety-based rules.

📋 Overview
The Intelligent Workout and Diet Planning System is a web application that generates personalized workout and nutrition plans based on user goals, medical history, injuries, and dietary restrictions. It uses a Large Language Model (LLM) to create draft plans that are refined by a rules engine to ensure safety and personalization.

🎯 Features
- Collects user data (goals, allergies, medical conditions, etc.)
- Generates customized workout and meal plans via LLM
- Enforces safety rules (e.g., no peanut foods if allergic)
- Maintains a database of foods and exercises with constraints
- Allows users to view, modify, and refine their plans
- Tracks progress for improved recommendations

🏗️ System Architecture (high-level)
1. Frontend (React / HTML-CSS-JS) – User interface for input and plan display
2. Backend (Node.js / Express) – Handles requests, validation, and business logic
3. Database (Supabase or PostgreSQL) – Stores user data, foods, exercises, and rules
4. LLM Integration (OpenAI API) – Generates draft plans for review
5. Rules Engine – Checks and filters unsafe or invalid recommendations

📁 Folder Structure
project-root/
│
├── frontend/           # UI components and pages
├── backend/            # API routes, controllers, validation logic
├── database/           # SQL scripts or schema definitions
├── docs/               # Reports, SRS, UML diagrams, etc.
├── .gitignore
├── README.md
└── LICENSE

⚙️ Installation & Setup

Clone the repository

git clone https://github.com/YourUsername/intelligent-workout-diet-system.git
cd intelligent-workout-diet-system

Install dependencies

npm install

Set up environment variables

Create a .env file in the backend/ folder with:

OPENAI_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here

Run the app

npm start

👥 Team Members
Name	Role	Responsibilities
Eathen Whittle	Database Developer	Schema design, Supabase integration
Micah Thompson	Frontend Developer	UI and user interaction
Jordan Trevino	Backend Developer	API, LLM, and rules engine
Erick Bardales	Project Manager	Documentation and coordination

🧩 Tech Stack
- Frontend: React / HTML / CSS / JavaScript
- Backend: Node.js + Express
- Database: Supabase (PostgreSQL)
- AI Integration: OpenAI API (GPT-based models)
- Version Control: Git + GitHub

🧪 Future Improvements
- Add user authentication and profile management
- Enable real-time progress tracking
- Introduce analytics for nutrition and fitness trends
- Support wearable device integration
