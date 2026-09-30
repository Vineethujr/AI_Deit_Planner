import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";

export default function GeneratePlan() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const plan = await api.generatePlan({});
      navigate("/plan-result", { state: { plan } });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="section" style={{ maxWidth: 640, margin: "40px auto 0 auto" }}>
      <h2>Generate today's plan</h2>
      <p style={{ color: "var(--color-ink-soft)" }}>
        We'll use the profile you saved — activity level, goal, and dietary preference — to build a
        one-day plan with an estimated nutrition summary. If an AI service isn't configured, a
        rule-based engine builds the plan instead, so this always works.
      </p>
      {error && <div className="alert alert-error">{error}</div>}
      <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
        {loading ? "Generating…" : "Generate my plan"}
      </button>
    </div>
  );
}
