export default function WorkoutCard({ workout, onSelect }) {
  return (
    <button
      onClick={() => onSelect(workout)}
      className="flex flex-col overflow-hidden rounded-xl border bg-white text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md hover:cursor-pointer"
    >
      <img
        src={workout.image}
        alt={workout.title}
        className="h-40 w-full object-cover"
      />
      <div className="space-y-1 px-4 py-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
          {workout.category}
        </p>
        <h3 className="text-sm font-semibold text-black">{workout.title}</h3>
        <p className="text-xs text-gray-500">
          {workout.level} • {workout.duration} • {workout.calories} kcal
        </p>
      </div>
    </button>
  );
}
