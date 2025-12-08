export default function MealCard({ meal, onSelect }) {
  return (
    <button
      onClick={() => onSelect(meal)}
      className="w-full max-w-xs mx-auto h-[280px] flex flex-col overflow-hidden rounded-xl border bg-white text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md hover:cursor-pointer"
    >
      <img
        src={meal.image}
        alt={meal.title || meal.name}
        className="h-40 w-full object-cover flex-shrink-0"
      />
      <div className="space-y-1 px-4 py-3 flex-1 overflow-hidden">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
          {meal.category || 'MEAL'}
        </p>
        <h3 className="text-sm font-semibold text-black line-clamp-2">{meal.title || meal.name}</h3>
        <p className="text-xs text-gray-500 line-clamp-1">
          {meal.timeOfDay || meal.meal_type} • {meal.calories} kcal
        </p>
        {(meal.protein > 0 || meal.carbs > 0 || meal.fat > 0) && (
          <p className="text-xs text-gray-400 line-clamp-1">
            P: {meal.protein}g • C: {meal.carbs}g • F: {meal.fat}g
          </p>
        )}
        {/* Show allergens if they exist */}
        {meal.allergens && meal.allergens.length > 0 && (
          <div className="pt-1">
            <div className="flex flex-wrap gap-1">
              {meal.allergens.slice(0, 2).map((allergen, i) => (
                <span key={i} className="text-xs bg-red-100 text-red-800 px-2 py-0.5 rounded">
                  {allergen}
                </span>
              ))}
              {meal.allergens.length > 2 && (
                <span className="text-xs text-gray-500">+{meal.allergens.length - 2}</span>
              )}
            </div>
          </div>
        )}
      </div>
    </button>
  );
}