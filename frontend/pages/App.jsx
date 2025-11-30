import { useState, useEffect } from 'react'

export default function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    document.title = "Login Page | My App";
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // Call your backend; the backend talks to LDAP (not the browser)
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const { message } = await res.json().catch(() => ({ message: "Login failed" }));
        throw new Error(message || "Login failed");
      }

      // success → redirect
      window.location.href = "/dashboard";
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[url('../public/workout_background.jpg')] bg-cover bg-center">
      <div className="w-full max-w-sm shrink-0 rounded-2xl bg-[#501214] p-6 shadow opacity-90 hover:opacity-100 hover:cursor-pointer">
        <h1 className="text-xl font-semibold text-black">Sign in</h1>
        <p className="mt-1 text-sm text-black">
          Use your directory username and password.
        </p>

        {error && (
          <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-black">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              inputMode="text"
              autoComplete="username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 w-full rounded-lg border border-gray-300 bg-gray-400 px-3 py-2 text-black outline-none ring-0 focus:border-gray-400"
              placeholder="e.g. jdoe"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-black">
              Password
            </label>
            <div className="mt-1 flex rounded-lg border border-black focus-within:border-gray-400">
              <input
                id="password"
                name="password"
                type={showPw ? "text" : "password"}
                autoComplete="current-password"
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
                aria-label={showPw ? "Hide password" : "Show password"}
              >
                {showPw ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <label className="inline-flex items-center gap-2 text-sm text-black">
              <input type="checkbox" className="h-4 w-4 rounded border-gray-400" />
              Remember me
            </label>
            <a href="/forgot" className="text-sm text-blue-400 hover:underline">
              Forgot password?
            </a>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-black px-4 py-2 text-white disabled:opacity-60"
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-black">
          By signing in you agree to the Acceptable Use Policy.
        </p>
      </div>
    </div>
  );
}
