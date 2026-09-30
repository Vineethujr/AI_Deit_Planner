import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";

const emptyForm = {
  age: "", height_cm: "", weight_kg: "", sex: "female",
  activity_level: "sedentary", goal: "maintenance",
  dietary_preference: "vegetarian",
};

export default function Profile() {
  const { profile, refreshProfile } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (profile) {
      setForm({
        age: profile.age ?? "",
        height_cm: profile.height_cm ?? "",
        weight_kg: profile.weight_kg ?? "",
        sex: profile.sex ?? "female",
        activity_level: profile.activity_level ?? "sedentary",
        goal: profile.goal ?? "maintenance",
        dietary_preference: profile.dietary_preference ?? "vegetarian",
      });
    }
  }, [profile]);

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setSubmitting(true);
    try {
      await api.updateProfile({
        ...form,
        age: Number(form.age),
        height_cm: Number(form.height_cm),
        weight_kg: Number(form.weight_kg),
      });
      await refreshProfile();
      setMessage("Profile saved.");
    } catch (err) {
      setError(err.details ? err.details.join(" ") : err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="form-panel wide">
      <h2>Your profile</h2>
      <p style={{ color: "var(--color-ink-soft)" }}>
        Demo profile data only. Used to estimate calorie and macro targets — not a medical assessment.
      </p>
      <hr className="hairline-hr" />
      {error && <div className="alert alert-error">{error}</div>}
      {message && <div className="alert alert-info">{message}</div>}
      <form onSubmit={handleSubmit}>
        <div className="field-row">
          <div className="field">
            <label htmlFor="age">Age</label>
            <input id="age" type="number" required value={form.age} onChange={handleChange("age")} />
          </div>
          <div className="field">
            <label htmlFor="sex">Sex</label>
            <select id="sex" value={form.sex} onChange={handleChange("sex")}>
              <option value="female">Female</option>
              <option value="male">Male</option>
            </select>
          </div>
        </div>
        <div className="field-row">
          <div className="field">
            <label htmlFor="height">Height (cm)</label>
            <input
              id="height" type="number" required value={form.height_cm} onChange={handleChange("height_cm")}
            />
          </div>
          <div className="field">
            <label htmlFor="weight">Weight (kg)</label>
            <input
              id="weight" type="number" required value={form.weight_kg} onChange={handleChange("weight_kg")}
            />
          </div>
        </div>
        <div className="field">
          <label htmlFor="activity">Activity level</label>
          <select id="activity" value={form.activity_level} onChange={handleChange("activity_level")}>
            <option value="sedentary">Sedentary — little to no exercise</option>
            <option value="light">Light — 1-3 days/week</option>
            <option value="moderate">Moderate — 3-5 days/week</option>
            <option value="active">Active — 6-7 days/week</option>
            <option value="very_active">Very active — physical job or training twice a day</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="goal">Goal</label>
          <select id="goal" value={form.goal} onChange={handleChange("goal")}>
            <option value="maintenance">General balanced eating (maintenance)</option>
            <option value="weight_loss">Weight-management demo (calorie deficit)</option>
            <option value="weight_gain">Fitness-oriented demo (calorie surplus)</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="diet_pref">Dietary preference</label>
          <select id="diet_pref" value={form.dietary_preference} onChange={handleChange("dietary_preference")}>
            <option value="vegetarian">Vegetarian</option>
            <option value="vegan">Vegan</option>
            <option value="non-vegetarian">Non-vegetarian</option>
          </select>
        </div>
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? "Saving…" : "Save profile"}
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          style={{ marginLeft: 10 }}
          onClick={() => navigate("/generate-plan")}
        >
          Generate a plan →
        </button>
      </form>
    </div>
  );
}
