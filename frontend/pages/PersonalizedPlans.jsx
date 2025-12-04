// pages/PersonalizedPlans.jsx - With logout functionality
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../src/components/Navbar.jsx";
import WorkoutCard from "../src/components/WorkoutCard.jsx";
import MealCard from "../src/components/MealCard.jsx";
import { generatePlan } from "../src/api.js";

export default function PersonalizedPlans() {
  const navigate = useNavigate();
  
  // State for generated plans
  const [workouts, setWorkouts] = useState([]);
  const [meals, setMeals] = useState([]);
  const [selectedWorkout, setSelectedWorkout] = useState(null);
  const [selectedMeal, setSelectedMeal] = useState(null);
  
  // State for user input form
  const [showForm, setShowForm] = useState(true);
  const [goal, setGoal] = useState("");
  const [allergies, setAllergies] = useState("");
  const [injuries, setInjuries] = useState("");
  
  // State for UI
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [replacements, setReplacements] = useState(null);

  // Set document title
  useEffect(() => {
    document.title = "Personalized Plans | Workout & Diet Planner";
  }, []);

  // Logout handler
  async function handleLogout() {
    try {
      await fetch("http://localhost:8000/api/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (e) {
      // ignore errors
    } finally {
      navigate("/", { replace: true });
    }
  }

  // Handle plan generation
  async function handleGeneratePlan(e) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // Parse allergies and injuries (comma-separated)
      const allergyList = allergies
        .split(",")
        .map(a => a.trim())
        .filter(a => a.length > 0);
      
      const injuryList = injuries
        .split(",")
        .map(i => i.trim())
        .filter(i => i.length > 0);

      // Call the backend API
      console.log("Sending request:", { goal, allergies: allergyList, injuries: injuryList });
      
      const result = await generatePlan({
        goal: goal,
        allergies: allergyList,
        injuries: injuryList,
      });

      console.log("Plan generated:", result);

      // Update state with the generated plan
      if (result.safe_plan) {
        const generatedWorkouts = result.safe_plan.workouts.map((w, index) => ({
          id: index + 1,
          title: w.name,
          category: "Workout",
          level: "Intermediate",
          duration: w.duration || "30 min",
          calories: w.estimated_calories || 200,
          image: "https://images.pexels.com/photos/1552103/pexels-photo-1552103.jpeg?auto=compress&cs=tinysrgb&w=800",
          focus: w.category || "Full body",
          equipment: ["Equipment varies"],
          description: `AI-generated workout for: ${goal}`,
          tutorialUrl: "https://youtube.com/",
        }));

        const generatedMeals = result.safe_plan.meals.map((m, index) => ({
          id: index + 1,
          title: m.name,
          category: "Meal",
          timeOfDay: index === 0 ? "Breakfast" : index === 1 ? "Lunch" : "Dinner",
          calories: m.calories || 400,
          protein: m.protein || 0,
          carbs: m.carbs || 0,
          fat: m.fat || 0,
          image: "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=800",
        }));

        setWorkouts(generatedWorkouts);
        setMeals(generatedMeals);
        setSelectedWorkout(generatedWorkouts[0]);
        setSelectedMeal(generatedMeals[0]);
        setReplacements(result.replacements_made);
        setShowForm(false);
      }
    } catch (err) {
      console.error("Error generating plan:", err);
      setError(err.message || "Failed to generate plan. Make sure the backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 text-black">
      <Navbar />

      {/* User info + logout button */}
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 pt-4 pb-2">
        <p className="text-sm text-gray-600">
          Welcome! You're logged in
        </p>
        <button
          onClick={handleLogout}
          className="rounded-md bg-black px-3 py-1 text-xs font-medium text-white hover:bg-gray-900 transition-colors"
        >
          Logout
        </button>
      </div>

      {/* Header */}
      <div className="mx-auto max-w-6xl px-4 pt-2">
        <h1 className="text-2xl font-bold">AI-Powered Workout & Meal Planner</h1>
        <p className="text-sm text-gray-600">Get personalized plans based on your goals</p>
      </div>

      {/* Show form if no plan generated yet */}
      {showForm && (
        <div className="mx-auto max-w-2xl px-4 py-8">
          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-bold mb-4">Generate Your Personalized Plan</h2>
            <p className="text-sm text-gray-600 mb-6">
              Tell us about your goals, allergies, and any injuries so we can create a safe and effective plan for you.
            </p>

            {error && (
              <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                ⚠️ {error}
              </div>
            )}

            <form onSubmit={handleGeneratePlan} className="space-y-4">
              <div>
                <label htmlFor="goal" className="block text-sm font-medium mb-2">
                  Your Fitness Goal <span className="text-red-500">*</span>
                </label>
                <input
                  id="goal"
                  type="text"
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="e.g., lose weight, build muscle, improve endurance"
                  required
                  className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                />
                <p className="mt-1 text-xs text-gray-500">Be specific about what you want to achieve</p>
              </div>

              <div>
                <label htmlFor="allergies" className="block text-sm font-medium mb-2">
                  Food Allergies <span className="text-gray-400">(optional)</span>
                </label>
                <input
                  id="allergies"
                  type="text"
                  value={allergies}
                  onChange={(e) => setAllergies(e.target.value)}
                  placeholder="e.g., peanuts, dairy, fish, soy"
                  className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                />
                <p className="mt-1 text-xs text-gray-500">Separate multiple allergies with commas</p>
              </div>

              <div>
                <label htmlFor="injuries" className="block text-sm font-medium mb-2">
                  Current Injuries <span className="text-gray-400">(optional)</span>
                </label>
                <input
                  id="injuries"
                  type="text"
                  value={injuries}
                  onChange={(e) => setInjuries(e.target.value)}
                  placeholder="e.g., knee injury, wrist injury, back pain"
                  className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                />
                <p className="mt-1 text-xs text-gray-500">Separate multiple injuries with commas</p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-black px-4 py-3 font-medium text-white hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating Your Plan with AI...
                  </span>
                ) : (
                  "✨ Generate Plan"
                )}
              </button>
            </form>

            <div className="mt-6 rounded-lg bg-blue-50 border border-blue-200 p-4">
              <p className="text-xs font-semibold text-blue-900 mb-2">💡 How it works:</p>
              <ul className="text-xs text-blue-800 space-y-1 list-disc pl-4">
                <li>AI analyzes your goals and constraints</li>
                <li>Generates personalized workouts and meals</li>
                <li>Automatically replaces unsafe items</li>
                <li>Provides detailed nutritional information</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Show generated plan */}
      {!showForm && workouts.length > 0 && meals.length > 0 && (
        <div className="mx-auto max-w-6xl px-4 py-6">
          {/* Display replacements if any */}
          {replacements && (replacements.meals?.length > 0 || replacements.workouts?.length > 0) && (
            <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-4 mb-6">
              <h3 className="font-semibold text-yellow-900 mb-2 flex items-center gap-2">
                ⚠️ Safety Replacements Made
              </h3>
              <p className="text-xs text-yellow-800 mb-3">
                Our AI detected unsafe items and automatically replaced them for your safety.
              </p>
              {replacements.meals?.length > 0 && (
                <div className="mb-2">
                  <p className="text-sm font-medium text-yellow-800">Meal Replacements:</p>
                  <ul className="text-sm text-yellow-700 list-disc pl-5 space-y-1">
                    {replacements.meals.map((r, i) => (
                      <li key={i}>
                        Replaced "<strong>{r.replaced}</strong>" with "<strong>{r.with}</strong>" 
                        <span className="text-xs"> ({r.reason})</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {replacements.workouts?.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-yellow-800">Workout Replacements:</p>
                  <ul className="text-sm text-yellow-700 list-disc pl-5 space-y-1">
                    {replacements.workouts.map((r, i) => (
                      <li key={i}>
                        Replaced "<strong>{r.replaced}</strong>" with "<strong>{r.with}</strong>" 
                        <span className="text-xs"> ({r.reason})</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div className="flex gap-6 flex-col lg:flex-row">
            {/* LEFT: workout column */}
            <section className="flex-1 rounded-2xl bg-white p-4 shadow-sm">
              <header className="mb-3 flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-semibold text-black">
                  <span className="text-xs text-gray-400">💪</span>
                  WORKOUTS
                </div>
                <button 
                  onClick={() => setShowForm(true)}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  ✨ Generate New Plan
                </button>
              </header>

              <div className="space-y-3">
                {workouts.map((w) => (
                  <WorkoutCard
                    key={w.id}
                    workout={w}
                    onSelect={setSelectedWorkout}
                  />
                ))}
              </div>
            </section>

            {/* MIDDLE: meal column */}
            <section className="flex-1 rounded-2xl bg-white p-4 shadow-sm">
              <header className="mb-3 flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-semibold text-black">
                  <span className="text-xs text-gray-400">🍽️</span>
                  MEALS
                </div>
                <button 
                  onClick={() => setShowForm(true)}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  ✨ Generate New Plan
                </button>
              </header>

              <div className="space-y-3">
                {meals.map((m) => (
                  <MealCard key={m.id} meal={m} onSelect={setSelectedMeal} />
                ))}
              </div>
            </section>

            {/* RIGHT: detail panel */}
            {selectedWorkout && (
              <aside className="flex-1 rounded-2xl bg-white shadow-sm">
                <div className="overflow-hidden rounded-t-2xl">
                  <img
                    src={selectedWorkout.image}
                    alt={selectedWorkout.title}
                    className="h-52 w-full object-cover"
                  />
                </div>

                <div className="space-y-4 p-5">
                  <div>
                    <h2 className="text-lg font-semibold">{selectedWorkout.title}</h2>
                    <p className="mt-1 text-xs text-gray-500">
                      Personalized for: {goal}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-3 text-xs">
                    <span className="rounded-full bg-gray-100 px-3 py-1">
                      Level: {selectedWorkout.level}
                    </span>
                    <span className="rounded-full bg-gray-100 px-3 py-1">
                      Duration: {selectedWorkout.duration}
                    </span>
                    <span className="rounded-full bg-gray-100 px-3 py-1">
                      Calories: {selectedWorkout.calories} kcal
                    </span>
                  </div>

                  <p className="text-sm text-gray-600">{selectedWorkout.description}</p>

                  <div className="grid grid-cols-1 gap-4 text-sm md:grid-cols-2">
                    <div>
                      <h3 className="mb-1 text-xs font-semibold text-gray-500">GOOD FOR</h3>
                      <p className="text-gray-700">{selectedWorkout.focus}</p>
                    </div>

                    <div>
                      <h3 className="mb-1 text-xs font-semibold text-gray-500">EQUIPMENT</h3>
                      <ul className="list-disc pl-4 text-gray-700">
                        {selectedWorkout.equipment.map((item) => (
                          <li key={item}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {selectedMeal && (
                    <div className="border-t pt-4">
                      <h3 className="mb-2 text-xs font-semibold text-gray-500">
                        PAIRED MEAL
                      </h3>
                      <div className="rounded-lg bg-gray-50 p-3">
                        <p className="text-sm font-medium text-gray-900">
                          {selectedMeal.title}
                        </p>
                        <p className="text-xs text-gray-600 mt-1">
                          {selectedMeal.calories} kcal
                        </p>
                        {selectedMeal.protein > 0 && (
                          <p className="text-xs text-gray-600 mt-1">
                            Protein: {selectedMeal.protein}g | Carbs: {selectedMeal.carbs}g | Fat: {selectedMeal.fat}g
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </aside>
            )}
          </div>
        </div>
      )}
    </div>
  );
}