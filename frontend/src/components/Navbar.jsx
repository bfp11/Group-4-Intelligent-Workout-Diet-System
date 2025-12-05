import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();

  // Helper function to check if a link is active
  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between items-center">
          {/* Logo/Brand */}
          <div className="flex items-center">
            <Link to="/plans" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-black text-white font-bold text-sm">
                WP
              </div>
              <span className="text-lg font-semibold text-gray-900">
                WorkoutPlan
              </span>
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center gap-1">
            {/* Dashboard button */}
            <button
              onClick={() => {
                window.dispatchEvent(new CustomEvent('showDashboard'));
              }}
              className="px-4 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
            >
              Dashboard
            </button>

            {/* Plans button */}
            <button
              onClick={() => {
                window.dispatchEvent(new CustomEvent('showPlans'));
              }}
              className="px-4 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
            >
              Plans
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}