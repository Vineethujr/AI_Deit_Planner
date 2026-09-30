import { createContext, useContext, useEffect, useState } from "react";
import { api } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("dp_token"));
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .getProfile()
      .then(setProfile)
      .catch(() => {
        localStorage.removeItem("dp_token");
        setToken(null);
      })
      .finally(() => setLoading(false));
  }, [token]);

  const login = async (email, password) => {
    const data = await api.login({ email, password });
    localStorage.setItem("dp_token", data.token);
    setToken(data.token);
  };

  const register = async (name, email, password) => {
    const data = await api.register({ name, email, password });
    localStorage.setItem("dp_token", data.token);
    setToken(data.token);
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch {
      /* ignore network errors on logout */
    }
    localStorage.removeItem("dp_token");
    setToken(null);
    setProfile(null);
  };

  const refreshProfile = async () => {
    const data = await api.getProfile();
    setProfile(data);
    return data;
  };

  return (
    <AuthContext.Provider
      value={{ token, profile, loading, login, register, logout, refreshProfile, setProfile }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
