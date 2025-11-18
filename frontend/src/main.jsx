import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";

import App from "../pages/App.jsx"; // because App.jsx is in /pages
import PersonalizedPlans from "../pages/PersonalizedPlans.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/personalized" element={<PersonalizedPlans />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
