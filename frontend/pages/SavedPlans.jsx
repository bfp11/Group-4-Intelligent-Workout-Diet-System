import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../src/components/Navbar";

export default function SavedPlans() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [planToDelete, setPlanToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPlans();
  }, []);

  async function fetchPlans() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/plans", {
        credentials: "include"
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate("/");
          return;
        }
        throw new Error("Failed to fetch plans");
      }

      const data = await response.json();
      console.log("Fetched plans:", data.plans);
      setPlans(data.plans || []);
    } catch (err) {
      console.error("Error fetching plans:", err);
      setError("Failed to load saved plans");
    } finally {
      setLoading(false);
    }
  }

  async function handleDeletePlan(planId) {
    setDeleting(true);

    try {
      const response = await fetch(`http://localhost:8000/api/plans/${planId}`, {
        method: "DELETE",
        credentials: "include"
      });

      if (!response.ok) {
        throw new Error("Failed to delete plan");
      }

      setPlans(plans.filter(p => p.id !== planId));
      setShowDeleteConfirm(false);
      setPlanToDelete(null);
      if (selectedPlan?.id === planId) {
        setSelectedPlan(null);
      }
    } catch (err) {
      console.error("Error deleting plan:", err);
      setError("Failed to delete plan");
    } finally {
      setDeleting(false);
    }
  }

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  }

  function confirmDelete(plan) {
    setPlanToDelete(plan);
    setShowDeleteConfirm(true);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Saved Plans</h1>
          <p className="text-gray-600 mt-2">
            You have {plans.length} of 5 saved plans
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        ) : plans.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">📋</div>
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">
              No Saved Plans Yet
            </h2>
            <p className="text-gray-600 mb-6">
              Start by creating a personalized workout and meal plan
            </p>
            <button
              onClick={() => navigate("/plans")}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
            >
              Create a Plan
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Plans List */}
            <div className="lg:col-span-1 space-y-4">
              {plans.map((plan) => (
                <div
                  key={plan.id}
                  onClick={() => setSelectedPlan(plan)}
                  className={`bg-white rounded-lg p-4 shadow cursor-pointer transition border-2 ${
                    selectedPlan?.id === plan.id
                      ? "border-blue-500"
                      : "border-transparent hover:border-gray-300"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-1">
                        {plan.goal}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {formatDate(plan.created_at)}
                      </p>
                      <div className="mt-2 flex gap-4 text-xs text-gray-500">
                        <span>🍽️ {plan.meal_count} meals</span>
                        <span>💪 {plan.workout_count} workouts</span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        confirmDelete(plan);
                      }}
                      className="text-red-500 hover:text-red-700 ml-2"
                      title="Delete plan"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Plan Details */}
            <div className="lg:col-span-2">
              {selectedPlan ? (
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <div className="mb-6">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      {selectedPlan.goal}
                    </h2>
                    <p className="text-gray-600">
                      Created: {formatDate(selectedPlan.created_at)}
                    </p>
                  </div>

                {/* Meals Section */}
                <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                    🍽️ Meal Plan
                    <span className="ml-2 text-sm font-normal text-gray-600">
                    ({selectedPlan.meals.length} meals)
                    </span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {selectedPlan.meals.map((meal, idx) => (
                    <div
                        key={idx}
                        className="border border-gray-200 rounded-lg overflow-hidden hover:border-blue-300 transition bg-white shadow-sm"
                    >
                        {/* Meal Image */}
                        <img
                        src="https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=800"
                        alt={meal.name}
                        className="h-40 w-full object-cover"
                        />
                        
                        <div className="p-4">
                        <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 text-lg">
                                {meal.name}
                            </h4>
                            </div>
                            {meal.was_replaced && (
                            <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                                Replaced
                            </span>
                            )}
                        </div>
                        
                        <div className="bg-gray-50 rounded-lg p-3 mb-3">
                            <div className="grid grid-cols-2 gap-3 text-sm">
                            <div className="flex flex-col">
                                <span className="text-xs text-gray-500 mb-1">Calories</span>
                                <span className="font-semibold text-gray-900">{meal.calories || 0} kcal</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-xs text-gray-500 mb-1">Protein</span>
                                <span className="font-semibold text-gray-900">{meal.protein || 0}g</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-xs text-gray-500 mb-1">Carbs</span>
                                <span className="font-semibold text-gray-900">{meal.carbs || 0}g</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-xs text-gray-500 mb-1">Fat</span>
                                <span className="font-semibold text-gray-900">{meal.fat || 0}g</span>
                            </div>
                            </div>
                        </div>
                        
                        {/* Show allergens if they exist */}
                        {meal.allergens && meal.allergens.length > 0 && (
                            <div>
                            <p className="text-xs text-gray-500 mb-1">Allergens:</p>
                            <div className="flex flex-wrap gap-1">
                                {meal.allergens.map((allergen, i) => (
                                <span key={i} className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                                    {allergen}
                                </span>
                                ))}
                            </div>
                            </div>
                        )}
                        </div>
                    </div>
                    ))}
                </div>
                </div>

                {/* Workouts Section */}
                <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                    💪 Workout Plan
                    <span className="ml-2 text-sm font-normal text-gray-600">
                    ({selectedPlan.workouts.length} workouts)
                    </span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {selectedPlan.workouts.map((workout, idx) => (
                    <div
                        key={idx}
                        className="border border-gray-200 rounded-lg overflow-hidden hover:border-blue-300 transition bg-white shadow-sm"
                    >
                        {/* Workout Image */}
                        <img
                        src="https://images.pexels.com/photos/1552103/pexels-photo-1552103.jpeg?auto=compress&cs=tinysrgb&w=800"
                        alt={workout.name}
                        className="h-40 w-full object-cover"
                        />
                        
                        <div className="p-4">
                        <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 text-lg">
                                {workout.name}
                            </h4>
                            {workout.category && (
                                <p className="text-sm text-blue-600 font-medium capitalize">
                                {workout.category}
                                </p>
                            )}
                            </div>
                            {workout.was_replaced && (
                            <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                                Replaced
                            </span>
                            )}
                        </div>
                        
                        <div className="bg-gray-50 rounded-lg p-3 mb-3">
                            <div className="grid grid-cols-2 gap-3 text-sm">
                            <div className="flex flex-col">
                                <span className="text-xs text-gray-500 mb-1">Duration</span>
                                <span className="font-semibold text-gray-900">{workout.duration_minutes} min</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-xs text-gray-500 mb-1">Calories Burned</span>
                                <span className="font-semibold text-gray-900">{workout.estimated_calories} kcal</span>
                            </div>
                            {workout.difficulty_level && (
                                <div className="flex flex-col col-span-2">
                                <span className="text-xs text-gray-500 mb-1">Difficulty</span>
                                <span className="font-semibold text-gray-900 capitalize">{workout.difficulty_level}</span>
                                </div>
                            )}
                            </div>
                        </div>
                        
                        {/* Show contraindications if they exist */}
                        {workout.contraindications && workout.contraindications.length > 0 && (
                            <div>
                            <p className="text-xs text-gray-500 mb-1">Not recommended with:</p>
                            <div className="flex flex-wrap gap-1">
                                {workout.contraindications.map((contraindication, i) => (
                                <span key={i} className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                                    {contraindication}
                                </span>
                                ))}
                            </div>
                            </div>
                        )}
                        </div>
                    </div>
                    ))}
                </div>
                </div>
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow-lg p-12 text-center">
                  <p className="text-gray-600 text-lg">
                    Select a plan to view details
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Delete Plan?
            </h3>
            <p className="text-gray-600 mb-6">
                Are you sure you want to delete the plan "{planToDelete?.goal}"?
                This action cannot be undone.
            </p>
            <div className="flex gap-3">
                <button
                onClick={() => {
                    setShowDeleteConfirm(false);
                    setPlanToDelete(null);
                }}
                disabled={deleting}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 bg-white hover:bg-gray-50 transition font-medium"
                >
                Cancel
                </button>
                <button
                onClick={() => handleDeletePlan(planToDelete.id)}
                disabled={deleting}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50 font-medium"
                >
                {deleting ? "Deleting..." : "Delete"}
                </button>
            </div>
            </div>
        </div>
        )}
    </div>
  );
}