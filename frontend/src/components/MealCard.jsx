export default function MealCard({ meal, onSelect }) {
  return (
    <button
      onClick={() => onSelect(meal)}
      className="flex flex-col overflow-hidden rounded-xl border bg-white text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md hover:cursor-pointer"
    >
      <img
        src={meal.image}
        alt={meal.title}
        className="h-40 w-full object-cover"
      />
      <div className="space-y-1 px-4 py-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
          {meal.category}
        </p>
        <h3 className="text-sm font-semibold text-black">{meal.title}</h3>
        <p className="text-xs text-gray-500">
          {meal.timeOfDay} • {meal.calories} kcal
        </p>
      </div>
    </button>
  );
}
