import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(form.name, form.email, form.password);
      navigate("/profile");
    } catch (err) {
      setError(err.details ? err.details.join(" ") : err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="form-panel">
      <h2>Create your account</h2>
      <p style={{ color: "var(--color-ink-soft)" }}>Demo data only — no real health information needed.</p>
      <hr className="hairline-hr" />
      {error && <div className="alert alert-error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="name">Name</label>
          <input
            id="name"
            required
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </div>
        <button className="btn btn-auth" type="submit" disabled={submitting} style={{ width: "100%" }}>
          {submitting ? "Creating account…" : "Sign up"}
        </button>
      </form>
      <p style={{ marginTop: 20, fontSize: "0.9rem" }}>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
