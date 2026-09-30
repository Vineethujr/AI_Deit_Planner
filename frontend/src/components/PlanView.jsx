const MEAL_ORDER = [
  ["breakfast", "Breakfast"],
  ["lunch", "Lunch"],
  ["snack", "Snack"],
  ["dinner", "Dinner"],
];

export default function PlanView({ plan }) {
  if (!plan) return null;
  const summary = plan.nutrition_summary || {};

  return (
    <div>
      <div className="stat-row" style={{ marginBottom: 24 }}>
        <div className="stat">
          <div className="value">{summary.estimated_calories ?? "—"}</div>
          <div className="label">kcal (est.)</div>
        </div>
        <div className="stat">
          <div className="value">{summary.protein_g ?? "—"}g</div>
          <div className="label">Protein</div>
        </div>
        <div className="stat">
          <div className="value">{summary.carbs_g ?? "—"}g</div>
          <div className="label">Carbs</div>
        </div>
        <div className="stat">
          <div className="value">{summary.fat_g ?? "—"}g</div>
          <div className="label">Fat</div>
        </div>
      </div>

      {MEAL_ORDER.map(([key, label]) => {
        const items = plan[key] || [];
        return (
          <div className="meal-block" key={key}>
            <div className="meal-label">{label}</div>
            {items.length === 0 && <div className="meal-item-detail">No suggestion available.</div>}
            {items.map((item, idx) => (
              <div key={idx}>
                <span className="meal-item-name">{item.name}</span>
                {item.grams != null && <span className="meal-item-detail"> — {item.grams}g</span>}
                {item.kcal != null && <span className="meal-item-detail"> · {item.kcal} kcal</span>}
              </div>
            ))}
          </div>
        );
      })}

      {plan.hydration_reminder && (
        <p style={{ marginTop: 18, color: "var(--color-ink-soft)", fontSize: "0.92rem" }}>
          💧 {plan.hydration_reminder}
        </p>
      )}

      <p className="disclaimer">{plan.disclaimer}</p>
      {plan.ai_fallback_reason && (
        <p style={{ fontSize: "0.78rem", color: "var(--color-ink-soft)" }}>
          Source: {plan.source} — {plan.ai_fallback_reason}
        </p>
      )}
    </div>
  );
}
