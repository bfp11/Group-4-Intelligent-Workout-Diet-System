// src/pages/MyPlans.jsx
import { useState, useEffect } from "react";
import axios from "axios";

export default function MyPlans() {
  const [plans, setPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch all saved plans
  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const res = await axios.get("http://localhost:8000/my-plans", {
          withCredentials: true,
        });
        setPlans(res.data.plans || []);
      } catch (err) {
        console.error(err);
      }
    };
    fetchPlans();
  }, []);

  // Load a specific plan's workouts + meals
  const loadPlan = async (planId: string) => {
    setLoading(true);
    try {
      const res = await axios.get(`http://localhost:8000/plan/${planId}`, {
        withCredentials: true,
      });
      setSelectedPlan(res.data);
    } catch (err) {
      alert("Could not load plan");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">My Saved Plans</h1>

      {plans.length === 0 ? (
        <p>No plans yet – generate one first!</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {plans.map((plan) => (
            <div key={plan.id} className="border rounded-lg p-4 bg-white shadow">
              <h3 className="font-semibold text-lg">{plan.goal}</h3>
              <p className="text-sm text-gray-600">
                {new Date(plan.created_at).toLocaleDateString()}
              </p>
              <button
                onClick={() => loadPlan(plan.id)}
                className="mt-3 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Load Plan
              </button>
            </div>
          ))}
        </div>
      )}

      {loading && <p className="mt-8">Loading plan...</p>}

      {selectedPlan && (
        <div className="mt-12 border-t pt-8">
          <h2 className="text-2xl font-bold mb-6">Your Plan: {selectedPlan.goal}</h2>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Workouts */}
            <div>
              <h3 className="text-xl font-semibold mb-4">Workouts</h3>
              {selectedPlan.workouts.map((w: any, i: number) => (
                <div key={i} className="bg-gray-50 p-4 rounded mb-3">
                  <p className="font-medium">{w.name}</p>
                  {w.sets && <p>Sets: {w.sets} × {w.reps}</p>}
                  {w.duration_minutes && <p>Duration: {w.duration_minutes} min</p>}
                </div>
              ))}
            </div>

            {/* Meals */}
            <div>
              <h3 className="text-xl font-semibold mb-4">Meals</h3>
              {selectedPlan.meals.map((m: any, i: number) => (
                <div key={i} className="bg-gray-50 p-4 rounded mb-3">
                  <p className="font-medium">{m.name}</p>
                  <p className="text-sm">
                    {m.calories} cal • P:{m.protein}g • C:{m.carbs}g • F:{m.fat}g
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}