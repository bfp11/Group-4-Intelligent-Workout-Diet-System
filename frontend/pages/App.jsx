// src/pages/Login.jsx - Updated for FastAPI backend
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [mode, setMode] = useState("login"); // "login" or "signup"
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [infoMessage, setInfoMessage] = useState("");
  const [checkingSession, setCheckingSession] = useState(true);

  const navigate = useNavigate();

  // On mount, check if user already has a valid session
  useEffect(() => {
    async function checkSession() {
      try {
        const res = await fetch("http://localhost:8000/api/me", {
          credentials: "include",
        });
        const data = await res.json();
        if (data.user) {
          navigate("/plans", { replace: true });
        }
      } catch (e) {
        // ignore
      } finally {
        setCheckingSession(false);
      }
    }
    checkSession();
  }, [navigate]);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setInfoMessage("");

    try {
      const endpoint = mode === "login" ? "/api/login" : "/api/signup";

      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // 🔑 send/receive cookies
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data.detail || data.message || "Request failed");
      }

      if (mode === "login") {
        // session cookie is set by backend; just navigate
        navigate("/plans", { replace: true });
      } else {
        setInfoMessage("Account created! You can now log in.");
        setMode("login");
        setPassword("");
      }
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  if (checkingSession) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 text-black">
        Checking session…
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[url('/workout_background.jpg')] bg-cover bg-center">
      <div className="w-full max-w-sm shrink-0 rounded-2xl bg-[#501214] p-6 shadow opacity-90">
        <h1 className="text-xl font-semibold text-black">
          {mode === "login" ? "Sign in" : "Sign up"}
        </h1>
        <p className="mt-1 text-sm text-black">
          {mode === "login"
            ? "Use your username and password."
            : "Create a new account with a username and password."}
        </p>

        {error && (
          <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        {infoMessage && (
          <div className="mt-4 rounded-md border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-700">
            {infoMessage}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-black"
            >
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 w-full rounded-lg border border-gray-300 bg-gray-400 px-3 py-2 text-black outline-none ring-0 focus:border-gray-400"
              placeholder="e.g. jdoe"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-black"
            >
              Password
            </label>
            <div className="mt-1 flex rounded-lg border border-black focus-within:border-gray-400">
              <input
                id="password"
                name="password"
                type={showPw ? "text" : "password"}
                autoComplete={
                  mode === "login" ? "current-password" : "new-password"
                }
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-l-lg bg-gray-400 px-3 py-2 text-black outline-none ring-0"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPw((v) => !v)}
                className="rounded-r-lg px-3 text-sm text-black hover:bg-gray-100"
              >
                {showPw ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {mode === "login" && (
            <div className="flex items-center justify-between">
              <label className="inline-flex items-center gap-2 text-sm text-black">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-400"
                />
                Remember me
              </label>
              <a
                href="/forgot"
                className="text-sm text-blue-400 hover:underline"
              >
                Forgot password?
              </a>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-black px-4 py-2 text-white disabled:opacity-60"
          >
            {loading
              ? mode === "login"
                ? "Signing in…"
                : "Creating account…"
              : mode === "login"
              ? "Sign in"
              : "Sign up"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-black">
          {mode === "login" ? (
            <>
              Don&apos;t have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("signup");
                  setError("");
                  setInfoMessage("");
                }}
                className="text-blue-300 underline"
              >
                Sign up
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("login");
                  setError("");
                  setInfoMessage("");
                }}
                className="text-blue-300 underline"
              >
                Log in
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}