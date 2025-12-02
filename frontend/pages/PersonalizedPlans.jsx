// pages/PersonalizedPlans.jsx
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../src/components/Navbar.jsx";
import WorkoutCard from "../src/components/WorkoutCard.jsx";
import MealCard from "../src/components/MealCard.jsx";

const workouts = [
  {
    id: 1,
    title: "Full Body Strength",
    category: "Workout",
    level: "Intermediate",
    duration: "45 min",
    calories: 310,
    image:
      "https://images.pexels.com/photos/1552103/pexels-photo-1552103.jpeg?auto=compress&cs=tinysrgb&w=800",
    focus: "Back, shoulders, abs, hamstrings",
    equipment: ["Barbell", "Dumbbells", "Bench"],
    description:
      "A balanced full body strength session focused on compound lifts and controlled tempo.",
    tutorialUrl: "https://youtube.com/",
  },
  {
    id: 2,
    title: "HIIT Fat Burn",
    category: "Workout",
    level: "Advanced",
    duration: "30 min",
    calories: 280,
    image:
      "https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=800",
    focus: "Cardio, legs, core",
    equipment: ["Bodyweight"],
    description:
      "High-intensity interval training to boost metabolism and cardiovascular fitness.",
    tutorialUrl: "https://youtube.com/",
  },
  {
    id: 3,
    title: "Beginner Mobility",
    category: "Workout",
    level: "Beginner",
    duration: "20 min",
    calories: 110,
    image:
      "https://images.pexels.com/photos/3823063/pexels-photo-3823063.jpeg?auto=compress&cs=tinysrgb&w=800",
    focus: "Hips, hamstrings, lower back",
    equipment: ["Mat"],
    description:
      "Gentle mobility routine to improve flexibility and reduce stiffness.",
    tutorialUrl: "https://youtube.com/",
  },
];

const meals = [
  {
    id: 1,
    title: "High-Protein Breakfast Bowl",
    category: "Meal",
    timeOfDay: "Breakfast",
    calories: 420,
    image:
      "https://images.pexels.com/photos/1437267/pexels-photo-1437267.jpeg?auto=compress&cs=tinysrgb&w=800",
  },
  {
    id: 2,
    title: "Grilled Chicken Salad",
    category: "Meal",
    timeOfDay: "Lunch",
    calories: 520,
    image:
      "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=800",
  },
  {
    id: 3,
    title: "Salmon & Veggie Plate",
    category: "Meal",
    timeOfDay: "Dinner",
    calories: 610,
    image:
      "https://images.pexels.com/photos/46239/salmon-dish-food-meal-46239.jpeg?auto=compress&cs=tinysrgb&w=800",
  },
];

export default function PersonalizedPlans() {
  const [selectedWorkout, setSelectedWorkout] = useState(workouts[0]);
  const [selectedMeal, setSelectedMeal] = useState(meals[0]);
  const [user, setUser] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);

  const navigate = useNavigate();

  // Set document title
  useEffect(() => {
    document.title = "Personalized Plans | My App";
  }, []);

  // Check backend session on mount
  useEffect(() => {
    async function checkSession() {
      try {
        const res = await fetch("http://localhost:8000/api/me", {
          credentials: "include", // send session cookie
        });
        const data = await res.json();
        if (!data.user) {
          // no active session → send back to login
          navigate("/", { replace: true });
        } else {
          setUser(data.user);
        }
      } catch (err) {
        // any error → treat as not logged in
        navigate("/", { replace: true });
      } finally {
        setCheckingSession(false);
      }
    }

    checkSession();
  }, [navigate]);

  // Logout handler
  async function handleLogout() {
    try {
      await fetch("http://localhost:8000/api/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (e) {
      // ignore errors, we’ll still send user to login
    } finally {
      navigate("/", { replace: true });
    }
  }

  if (checkingSession) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 text-black">
        Loading your plan…
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 text-black">
      <Navbar />

      {/* user info + logout */}
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 pt-4">
        <p className="text-sm text-gray-600">
          Logged in as{" "}
          <span className="font-semibold">{user?.username}</span>
        </p>
        <button
          onClick={handleLogout}
          className="rounded-md bg-black px-3 py-1 text-xs font-medium text-white hover:bg-gray-900"
        >
          Logout
        </button>
      </div>

      <main className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-6 lg:flex-row">
        {/* LEFT: workout column */}
        <section className="flex-1 rounded-2xl bg-white p-4 shadow-sm">
          <header className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-semibold text-black">
              <span className="text-xs text-gray-400">←</span>
              WORKOUT
            </div>
            <button className="text-xs text-gray-500 hover:text-black">
              ✏️ Edit
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

          <button className="mt-4 w-full rounded-xl border border-gray-300 py-2 text-xs font-medium text-gray-600 hover:bg-gray-50">
            LOAD MORE
          </button>
        </section>

        {/* MIDDLE: meal column */}
        <section className="flex-1 rounded-2xl bg-white p-4 shadow-sm">
          <header className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-semibold text-black">
              <span className="text-xs text-gray-400">←</span>
              MEAL
            </div>
            <button className="text-xs text-gray-500 hover:text-black">
              ✏️ Edit
            </button>
          </header>

          <div className="space-y-3">
            {meals.map((m) => (
              <MealCard
                key={m.id}
                meal={m}
                onSelect={setSelectedMeal}
              />
            ))}
          </div>

          <button className="mt-4 w-full rounded-xl border border-gray-300 py-2 text-xs font-medium text-gray-600 hover:bg-gray-50">
            LOAD MORE
          </button>
        </section>

        {/* RIGHT: detail panel */}
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
              <h2 className="text-lg font-semibold">
                {selectedWorkout.title}
              </h2>
              <p className="mt-1 text-xs text-gray-500">
                Personalized for you • {selectedMeal.title}
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

            <p className="text-sm text-gray-600">
              {selectedWorkout.description}
            </p>

            <div className="grid grid-cols-1 gap-4 text-sm md:grid-cols-2">
              <div>
                <h3 className="mb-1 text-xs font-semibold text-gray-500">
                  GOOD FOR
                </h3>
                <p className="text-gray-700">{selectedWorkout.focus}</p>
              </div>

              <div>
                <h3 className="mb-1 text-xs font-semibold text-gray-500">
                  EQUIPMENT
                </h3>
                <ul className="list-disc pl-4 text-gray-700">
                  {selectedWorkout.equipment.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div>
              <h3 className="mb-1 text-xs font-semibold text-gray-500">
                TUTORIAL
              </h3>
              <a
                href={selectedWorkout.tutorialUrl}
                className="text-xs text-blue-600 underline"
              >
                View guided video
              </a>
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}
