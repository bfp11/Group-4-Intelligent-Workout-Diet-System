// pages/Profile.jsx - User Profile and Settings Page
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../src/components/Navbar.jsx";

export default function Profile() {
  const navigate = useNavigate();
  
  // User data state
  const [userData, setUserData] = useState({
    name: "",
    email: "",
    age: "",
    height: "",
    weight: "",
    goal: "",
    allergies: [],
    injuries: []
  });

  // Form state
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  // Temporary form data (for editing)
  const [formData, setFormData] = useState({ ...userData });

  // Set document title
  useEffect(() => {
    document.title = "Profile | Workout & Diet Planner";
  }, []);

  // Fetch user data on mount
  useEffect(() => {
    fetchUserData();
  }, []);

  async function fetchUserData() {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/profile", {
        credentials: "include"
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate("/");
          return;
        }
        throw new Error("Failed to fetch user data");
      }

      const data = await response.json();
      
      // Format the data
      const formattedData = {
        name: data.name || "",
        email: data.email || "",
        age: data.age || "",
        height: data.height || "",
        weight: data.weight || "",
        goal: data.goal || "",
        allergies: data.allergies || [],
        injuries: data.injuries || []
      };

      setUserData(formattedData);
      setFormData(formattedData);
    } catch (err) {
      console.error("Error fetching user data:", err);
      setMessage("❌ Failed to load profile data");
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    setSaving(true);
    setMessage("");

    try {
      const response = await fetch("http://localhost:8000/api/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name: formData.name,
          age: formData.age ? parseInt(formData.age) : null,
          height: formData.height ? parseFloat(formData.height) : null,
          weight: formData.weight ? parseFloat(formData.weight) : null,
          goal: formData.goal,
          allergies: formData.allergies,
          injuries: formData.injuries
        })
      });

      if (!response.ok) {
        throw new Error("Failed to update profile");
      }

      const data = await response.json();
      setUserData(formData);
      setIsEditing(false);
      setMessage("✅ Profile updated successfully!");
      setTimeout(() => setMessage(""), 3000);
    } catch (err) {
      console.error("Error updating profile:", err);
      setMessage("❌ Failed to update profile");
      setTimeout(() => setMessage(""), 5000);
    } finally {
      setSaving(false);
    }
  }

  function handleCancel() {
    setFormData({ ...userData });
    setIsEditing(false);
  }

  function handleAllergyAdd(allergen) {
    if (allergen.trim() && !formData.allergies.includes(allergen.trim())) {
      setFormData({
        ...formData,
        allergies: [...formData.allergies, allergen.trim()]
      });
    }
  }

  function handleAllergyRemove(allergen) {
    setFormData({
      ...formData,
      allergies: formData.allergies.filter(a => a !== allergen)
    });
  }

  function handleInjuryAdd(injury) {
    if (injury.trim() && !formData.injuries.includes(injury.trim())) {
      setFormData({
        ...formData,
        injuries: [...formData.injuries, injury.trim()]
      });
    }
  }

  function handleInjuryRemove(injury) {
    setFormData({
      ...formData,
      injuries: formData.injuries.filter(i => i !== injury)
    });
  }

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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <svg className="animate-spin h-12 w-12 mx-auto text-blue-600" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="mt-4 text-gray-600">Loading profile...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 text-black">
      <Navbar />

      {/* User info + logout button */}
      <div className="mx-auto flex max-w-4xl items-center justify-between px-4 pt-4 pb-2">
        <p className="text-sm text-gray-600">
          Welcome, {userData.name}!
        </p>
        <button
          onClick={handleLogout}
          className="rounded-md bg-black px-3 py-1 text-xs font-medium text-white hover:bg-gray-900 transition-colors"
        >
          Logout
        </button>
      </div>

      {/* Header */}
      <div className="mx-auto max-w-4xl px-4 pt-2 pb-6">
        <h1 className="text-2xl font-bold">Profile & Settings</h1>
        <p className="text-sm text-gray-600">
          Manage your personal information and preferences
        </p>
      </div>

      {/* Message */}
      {message && (
        <div className={`mx-auto max-w-4xl px-4 mb-4`}>
          <div className={`rounded-md border px-4 py-3 text-sm ${
            message.includes('✅') 
              ? 'border-green-200 bg-green-50 text-green-700'
              : 'border-red-200 bg-red-50 text-red-700'
          }`}>
            {message}
          </div>
        </div>
      )}

      {/* Profile Card */}
      <div className="mx-auto max-w-4xl px-4">
        <div className="rounded-2xl bg-white p-6 shadow-sm">
          
          {/* Account Information */}
            <div className="mb-6 pb-6 border-b">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Account Information</h2>
                {!isEditing && (
                <button
                    onClick={() => setIsEditing(true)}
                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                    Edit
                </button>
                )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                </label>
                {isEditing ? (
                    <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                    />
                ) : (
                    <p className="text-gray-900 bg-gray-50 rounded-lg px-4 py-2">
                    {userData.name}
                    </p>
                )}
                </div>
                <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                </label>
                <p className="text-gray-900 bg-gray-50 rounded-lg px-4 py-2">
                    {userData.email}
                </p>
                </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
                Email cannot be changed at this time
            </p>
            </div>

          {/* Personal Information */}
          <div className="mb-6 pb-6 border-b">
            <h2 className="text-lg font-semibold mb-4">Personal Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Age
                </label>
                {isEditing ? (
                    <input
                    type="number"
                    value={formData.age}
                    onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                    placeholder="25"
                    />
                ) : (
                    <p className="text-gray-900 bg-gray-50 rounded-lg px-4 py-2">
                    {userData.age || "Not set"}
                    </p>
                )}
                </div>
                <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Height (inches)
                </label>
                {isEditing ? (
                    <input
                    type="number"
                    step="0.1"
                    value={formData.height}
                    onChange={(e) => setFormData({ ...formData, height: e.target.value })}
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                    placeholder="68"
                    />
                ) : (
                    <p className="text-gray-900 bg-gray-50 rounded-lg px-4 py-2">
                    {userData.height ? `${userData.height} in` : "Not set"}
                    </p>
                )}
                </div>
                <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Weight (lbs)
                </label>
                {isEditing ? (
                    <input
                    type="number"
                    step="0.1"
                    value={formData.weight}
                    onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                    placeholder="170"
                    />
                ) : (
                    <p className="text-gray-900 bg-gray-50 rounded-lg px-4 py-2">
                    {userData.weight ? `${userData.weight} lbs` : "Not set"}
                    </p>
                )}
                </div>
            </div>
          </div>

          {/* Fitness Goal */}
          <div className="mb-6 pb-6 border-b">
            <h2 className="text-lg font-semibold mb-4">Fitness Goal</h2>
            {isEditing ? (
              <input
                type="text"
                value={formData.goal}
                onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
                placeholder="e.g., lose weight, build muscle, improve endurance"
                className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
              />
            ) : (
              <p className="text-gray-900 bg-gray-50 rounded-lg px-4 py-2">
                {userData.goal || "Not set"}
              </p>
            )}
          </div>

          {/* Allergies */}
          <div className="mb-6 pb-6 border-b">
            <h2 className="text-lg font-semibold mb-4">Food Allergies</h2>
            {isEditing ? (
              <div>
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    id="allergyInput"
                    placeholder="Add an allergen (e.g., peanuts)"
                    className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleAllergyAdd(e.target.value);
                        e.target.value = '';
                      }
                    }}
                  />
                  <button
                    onClick={() => {
                      const input = document.getElementById('allergyInput');
                      handleAllergyAdd(input.value);
                      input.value = '';
                    }}
                    className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.allergies.map((allergen, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 rounded-full bg-red-100 px-3 py-1 text-sm text-red-700"
                    >
                      {allergen}
                      <button
                        onClick={() => handleAllergyRemove(allergen)}
                        className="ml-1 hover:text-red-900"
                      >
                        ✕
                      </button>
                    </span>
                  ))}
                  {formData.allergies.length === 0 && (
                    <p className="text-sm text-gray-500">No allergies added</p>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {userData.allergies.map((allergen, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center rounded-full bg-red-100 px-3 py-1 text-sm text-red-700"
                  >
                    {allergen}
                  </span>
                ))}
                {userData.allergies.length === 0 && (
                  <p className="text-gray-500">No allergies recorded</p>
                )}
              </div>
            )}
          </div>

          {/* Injuries */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-4">Current Injuries</h2>
            {isEditing ? (
              <div>
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    id="injuryInput"
                    placeholder="Add an injury (e.g., knee injury)"
                    className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleInjuryAdd(e.target.value);
                        e.target.value = '';
                      }
                    }}
                  />
                  <button
                    onClick={() => {
                      const input = document.getElementById('injuryInput');
                      handleInjuryAdd(input.value);
                      input.value = '';
                    }}
                    className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.injuries.map((injury, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 rounded-full bg-yellow-100 px-3 py-1 text-sm text-yellow-700"
                    >
                      {injury}
                      <button
                        onClick={() => handleInjuryRemove(injury)}
                        className="ml-1 hover:text-yellow-900"
                      >
                        ✕
                      </button>
                    </span>
                  ))}
                  {formData.injuries.length === 0 && (
                    <p className="text-sm text-gray-500">No injuries added</p>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {userData.injuries.map((injury, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center rounded-full bg-yellow-100 px-3 py-1 text-sm text-yellow-700"
                  >
                    {injury}
                  </span>
                ))}
                {userData.injuries.length === 0 && (
                  <p className="text-gray-500">No injuries recorded</p>
                )}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          {isEditing && (
            <div className="flex gap-3 mt-6 pt-6 border-t">
              <button
                onClick={handleCancel}
                className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2 font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex-1 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {saving ? "Saving..." : "Save Changes"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}