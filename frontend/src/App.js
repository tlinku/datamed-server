import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./App.css";
import { initKeycloak, isAuthenticated, doLogin, doLogout, getToken } from "./keycloak";

function App() {
  const navigate = useNavigate();
  const [initialized, setInitialized] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initKeycloak(() => {
      setInitialized(true);
      setAuthenticated(isAuthenticated());
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (initialized && authenticated) {
      navigate("/prescriptions");
    }
  }, [initialized, authenticated, navigate]);

  const handleLogin = () => {
    setLoading(true);
    doLogin();
  };

  const handleRegister = () => {
    window.location.href = `${process.env.REACT_APP_KEYCLOAK_URL || 'http://localhost:8080'}/auth/realms/${process.env.REACT_APP_KEYCLOAK_REALM || 'datamed'}/protocol/openid-connect/registrations?client_id=${process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'datamed-client'}&response_type=code&redirect_uri=${window.location.origin}`;
  };

  return (
    <div className="container">
      <div className="auth-box">
        <h1>Welcome to Datamed</h1>
        {error && <div className="error">{error}</div>}
        {loading ? (
          <div>
            <div className="loading">Loading...</div>
            <div className="troubleshoot-link">
              <a href="/keycloak-test">Troubleshoot Keycloak Connection</a>
            </div>
          </div>
        ) : initialized && !authenticated ? (
          <div className="auth-buttons">
            <button onClick={handleLogin} className="login-btn">
              Login with Keycloak
            </button>
            <button onClick={handleRegister} className="register-btn">
              Register a New Account
            </button>
            <div className="troubleshoot-link">
              <a href="/keycloak-test">Troubleshoot Keycloak Connection</a>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default App;
