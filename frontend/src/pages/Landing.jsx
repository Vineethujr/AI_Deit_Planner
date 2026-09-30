import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="hero">
      <h1>Plan meals that fit your day, not a template.</h1>
      <p className="lede">
        Nourish turns a short profile — your activity level, goal, and dietary preference — into a
        daily meal plan with an estimated nutrition breakdown. Everything is saved to your account
        so it's there on any device you sign into.
      </p>
      <div className="hero-actions">
        <Link to="/register" className="btn btn-auth">
          Create your plan
        </Link>
        <Link to="/login" className="btn btn-auth">
          I already have an account
        </Link>
      </div>
      <p className="disclaimer" style={{ marginTop: 40 }}>
        Educational / general wellness demo project. Generated plans are not medical or clinical
        nutrition advice. All data used in this demo is synthetic.
      </p>
    </div>
  );
}
