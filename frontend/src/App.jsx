import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";

import Landing from "./pages/Landing";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import GeneratePlan from "./pages/GeneratePlan";
import PlanResult from "./pages/PlanResult";
import SavedPlans from "./pages/SavedPlans";
import Files from "./pages/Files";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <div className="app-shell">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route
              path="/generate-plan"
              element={
                <ProtectedRoute>
                  <GeneratePlan />
                </ProtectedRoute>
              }
            />
            <Route
              path="/plan-result"
              element={
                <ProtectedRoute>
                  <PlanResult />
                </ProtectedRoute>
              }
            />
            <Route
              path="/saved-plans"
              element={
                <ProtectedRoute>
                  <SavedPlans />
                </ProtectedRoute>
              }
            />
            <Route
              path="/files"
              element={
                <ProtectedRoute>
                  <Files />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
