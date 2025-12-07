import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import App from "../pages/App.jsx"; // because App.jsx is in /pages
import PersonalizedPlans from "../pages/PersonalizedPlans.jsx";
import Profile from "../pages/Profile.jsx"; // Add this line

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/plans" element={<PersonalizedPlans />} />
        <Route path="/profile" element={<Profile />} /> {/* Add this line */}
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);