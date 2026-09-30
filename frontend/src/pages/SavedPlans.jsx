import { useEffect, useState } from "react";
import { api } from "../services/api";
import PlanView from "../components/PlanView";

function formatDate(ts) {
  if (!ts) return "";
  return new Date(ts * 1000).toLocaleString();
}

export default function SavedPlans() {
  const [plans, setPlans] = useState([]);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.listPlans();
      setPlans(data.plans);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (planId) => {
    await api.deletePlan(planId);
    if (selected?.plan_id === planId) setSelected(null);
    load();
  };

  if (loading) return null;

  return (
    <div className="section">
      <h2>Saved plans</h2>
      {error && <div className="alert alert-error">{error}</div>}
      {plans.length === 0 && (
        <div className="empty-state">
          <p>No plans saved yet. Generate one from the "Generate Plan" page.</p>
        </div>
      )}
      {!selected &&
        plans.map((plan) => (
          <div className="list-row" key={plan.plan_id}>
            <div>
              <strong>{plan.nutrition_summary?.estimated_calories ?? "—"} kcal</strong>{" "}
              <span style={{ color: "var(--color-ink-soft)" }}>· {formatDate(plan.created_at)}</span>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-secondary" onClick={() => setSelected(plan)}>
                View
              </button>
              <button className="btn btn-danger" onClick={() => handleDelete(plan.plan_id)}>
                Delete
              </button>
            </div>
          </div>
        ))}
      {selected && (
        <div>
          <button className="btn btn-secondary" onClick={() => setSelected(null)} style={{ marginBottom: 20 }}>
            ← Back to list
          </button>
          <PlanView plan={selected} />
        </div>
      )}
    </div>
  );
}
