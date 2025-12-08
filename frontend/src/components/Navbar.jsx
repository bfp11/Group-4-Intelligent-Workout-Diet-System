import { Link, useLocation, useNavigate } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      await fetch("http://localhost:8000/api/logout", {
        method: "POST",
        credentials: "include"
      });
      navigate("/");
    } catch (err) {
      console.error("Logout error:", err);
    }
  }

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link to="/plans" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-black text-white font-bold text-sm">
                FP
              </div>
              <span className="text-lg font-semibold text-gray-900">
                FitPlan
              </span>
            </Link>
            <div className="flex space-x-4">
              <button
                onClick={() => {
                  if (location.pathname === '/plans') {
                    window.dispatchEvent(new CustomEvent('showPlans'));
                  } else {
                    navigate('/plans');
                  }
                }}
                className={`px-4 py-2 rounded-lg transition ${
                  location.pathname === '/plans'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Generate Plans
              </button>
              <Link
                to="/saved-plans"
                className={`px-4 py-2 rounded-lg transition ${
                  location.pathname === '/saved-plans'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Saved Plans
              </Link>
              <Link
                to="/profile"
                className={`px-4 py-2 rounded-lg transition ${
                  location.pathname === '/profile'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Profile
              </Link>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="text-red-600 hover:text-red-800 font-medium"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}