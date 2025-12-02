export default function Navbar() {
  return (
    <header className="w-full border-b bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="h-8 w-8 rounded-full bg-black text-white flex items-center justify-center text-sm font-semibold">
            WP
          </span>
          <span className="text-lg font-semibold tracking-tight text-black">
            WorkoutPlan
          </span>
        </div>

        <nav className="flex items-center gap-6 text-sm text-gray-600">
          <button className="hover:text-black">Dashboard</button>
          <button className="hover:text-black">Plans</button>
          <button className="hover:text-black">Profile</button>
        </nav>
      </div>
    </header>
  );
}
