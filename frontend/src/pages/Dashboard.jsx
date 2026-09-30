import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";

const GOAL_LABELS = {
  maintenance: "General balanced eating",
  weight_loss: "Weight-management demo",
  weight_gain: "Fitness-oriented demo",
};

export default function Dashboard() {
  const { profile } = useAuth();
  const [plans, setPlans] = useState([]);
  const [files, setFiles] = useState([]);

  useEffect(() => {
    api.listPlans().then((d) => setPlans(d.plans)).catch(() => {});
    api.listFiles().then((d) => setFiles(d.files)).catch(() => {});
  }, []);

  const latestPlan = plans[0];
  const profileIncomplete = !profile?.height_cm || !profile?.weight_kg || !profile?.age;

  return (
    <div className="section">
      <h1 style={{ fontSize: "1.9rem" }}>Welcome, {profile?.name || "there"}</h1>

      {profileIncomplete && (
        <div className="alert alert-info">
          Your profile is incomplete. <Link to="/profile">Finish it</Link> to generate a plan.
        </div>
      )}

      <div className="stat-row" style={{ margin: "24px 0" }}>
        <div className="stat">
          <div className="value" style={{ fontSize: "1.15rem" }}>
            {GOAL_LABELS[profile?.goal] || "Not set"}
          </div>
          <div className="label">Current goal</div>
        </div>
        <div className="stat">
          <div className="value" style={{ fontSize: "1.15rem", textTransform: "capitalize" }}>
            {profile?.dietary_preference || "Not set"}
          </div>
          <div className="label">Diet preference</div>
        </div>
        <div className="stat">
          <div className="value">{plans.length}</div>
          <div className="label">Saved plans</div>
        </div>
        <div className="stat">
          <div className="value">{files.length}</div>
          <div className="label">Uploaded files</div>
        </div>
      </div>

      <hr className="hairline-hr" />

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 32 }}>
        <Link to="/generate-plan" className="btn btn-primary">
          Generate new plan
        </Link>
        <Link to="/saved-plans" className="btn btn-secondary">
          Previous plans
        </Link>
        <Link to="/files" className="btn btn-secondary">
          Uploaded files
        </Link>
      </div>

      <h3>Latest plan</h3>
      {latestPlan ? (
        <p>
          {latestPlan.nutrition_summary?.estimated_calories} kcal (est.) —{" "}
          <Link to="/saved-plans">view details</Link>
        </p>
      ) : (
        <p style={{ color: "var(--color-ink-soft)" }}>No plans generated yet.</p>
      )}
    </div>
  );
}
