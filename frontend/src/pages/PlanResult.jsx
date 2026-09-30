import { useLocation, useNavigate } from "react-router-dom";
import PlanView from "../components/PlanView";

export default function PlanResult() {
  const location = useLocation();
  const navigate = useNavigate();
  const plan = location.state?.plan;

  if (!plan) {
    return (
      <div className="empty-state">
        <p>No plan to show yet.</p>
        <button className="btn btn-primary" onClick={() => navigate("/generate-plan")}>
          Generate a plan
        </button>
      </div>
    );
  }

  return (
    <div className="section" style={{ maxWidth: 640, margin: "40px auto 0 auto" }}>
      <h2>Your meal plan</h2>
      <p style={{ color: "var(--color-ink-soft)" }}>Saved automatically to your account.</p>
      <PlanView plan={plan} />
      <div style={{ marginTop: 24, display: "flex", gap: 12 }}>
        <button className="btn btn-secondary" onClick={() => navigate("/saved-plans")}>
          View saved plans
        </button>
        <button className="btn btn-primary" onClick={() => navigate("/generate-plan")}>
          Generate another
        </button>
      </div>
    </div>
  );
}
