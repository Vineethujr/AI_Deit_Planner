import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <nav className="topnav">
      <NavLink to="/" className="brand">
        Nourish
      </NavLink>
      <div className="nav-links">
        {token ? (
          <>
            <NavLink to="/dashboard">Dashboard</NavLink>
            <NavLink to="/generate-plan">Generate Plan</NavLink>
            <NavLink to="/saved-plans">Saved Plans</NavLink>
            <NavLink to="/files">Files</NavLink>
            <NavLink to="/profile">Profile</NavLink>
            <button className="btn btn-secondary" onClick={handleLogout}>
              Log out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login" className="auth-nav-link">Log in</NavLink>
            <NavLink to="/register" className="btn btn-auth">
              Sign up
            </NavLink>
          </>
        )}
      </div>
    </nav>
  );
}
