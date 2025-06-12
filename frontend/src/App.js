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
    console.log('App mounted, initializing Keycloak...');
    
    initKeycloak(() => {
      console.log('Keycloak callback executed');
      console.log('Is authenticated:', isAuthenticated());
      console.log('Token:', getToken() ? 'Present' : 'Missing');
      setInitialized(true);
      setAuthenticated(isAuthenticated());
      console.log('Setting loading to false...');
      setLoading(false);
    });
  }, []);

  const handleLogin = () => {
    setLoading(true);
    console.log("Starting login process...");
    doLogin();
  };

  const handleRegister = () => {
    window.location.href = `${process.env.REACT_APP_KEYCLOAK_URL || 'http://localhost:8080'}/auth/realms/${process.env.REACT_APP_KEYCLOAK_REALM || 'datamed'}/protocol/openid-connect/registrations?client_id=${process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'datamed-client'}&response_type=code&redirect_uri=${window.location.origin}`;
  };

  // Render authenticated content full-screen
  if (authenticated) {
    console.log('Showing full-screen authenticated content');
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
          Debug: loading={loading.toString()}, authenticated={authenticated.toString()}, initialized={initialized.toString()}
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