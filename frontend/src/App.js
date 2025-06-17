import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { initKeycloak, isAuthenticated, doLogin, doLogout, getToken } from "./keycloak";
import Dashboard from "./dashboard/Dashboard";
import PrescriptionsPage from "./prescriptions/PrescriptionsPage";
import Profile from "./profile/profile";
import Notes from "./notes/notes";
import "./App.css";


function App() {
  const [initialized, setInitialized] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    
    initKeycloak(() => {
      setInitialized(true);
      const authStatus = isAuthenticated();
      console.log('Keycloak initialized. Authenticated:', authStatus, 'Token exists:', !!getToken());
      setAuthenticated(authStatus);
      setLoading(false);
    });
  }, []);

  // Debug info
  useEffect(() => {
    console.log('App state - initialized:', initialized, 'authenticated:', authenticated, 'loading:', loading);
  }, [initialized, authenticated, loading]);

  const handleLogin = () => {
    setLoading(true);
    doLogin();
  };

  const handleRegister = () => {
    window.location.href = `${process.env.REACT_APP_KEYCLOAK_URL || 'https://localhost'}/auth/realms/${process.env.REACT_APP_KEYCLOAK_REALM || 'datamed'}/protocol/openid-connect/registrations?client_id=${process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'datamed-client'}&response_type=code&redirect_uri=${window.location.origin}`;
  };


  if (authenticated) {
    return (
      <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/prescriptions" element={<PrescriptionsPage />} />
          <Route path="/notes" element={<Notes />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    );
  }
  return (
    <div className="container">
      <div className="auth-box">
        <h1>Welcome to Datamed</h1>
        <div style={{fontSize: '12px', color: 'gray'}}>
        </div>
        {error && <div className="error">{error}</div>}
        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <div className="auth-buttons">
            <button onClick={handleLogin} className="login-btn">
              Login with Keycloak
            </button>
            <button onClick={handleRegister} className="register-btn">
              Register a New Account
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;