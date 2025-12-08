import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "../pages/App.jsx";
import PersonalizedPlans from "../pages/PersonalizedPlans.jsx";
import Profile from "../pages/Profile.jsx";
import SavedPlans from "../pages/SavedPlans.jsx"; 
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/plans" element={<PersonalizedPlans />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/saved-plans" element={<SavedPlans />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);