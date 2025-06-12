import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getToken } from "../keycloak";
import "./Dashboard.css";

function Dashboard() {
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    prescriptions: 0,
    notes: 0,
    hasProfile: false
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const token = getToken();
      if (!token) return;
      const prescriptionsResponse = await fetch(`${apiUrl}/prescriptions`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      let prescriptionsCount = 0;
      if (prescriptionsResponse.ok) {
        const prescriptions = await prescriptionsResponse.json();
        prescriptionsCount = prescriptions.length;
      }
      const notesResponse = await fetch(`${apiUrl}/notes`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      let notesCount = 0;
      if (notesResponse.ok) {
        const notes = await notesResponse.json();
        notesCount = notes.length;
      }
      const profileResponse = await fetch(`${apiUrl}/doctors`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      const hasProfile = profileResponse.ok;

      setStats({
        prescriptions: prescriptionsCount,
        notes: notesCount,
        hasProfile
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;

  return (
    <div className="dashboard-page">
      <div className="header">
        <h1>Dashboard</h1>
        <div className="header-buttons">
          <button onClick={() => navigate("/prescriptions")} className="nav-button">
            Prescriptions
          </button>
          <button onClick={() => navigate("/notes")} className="nav-button">
            Notes
          </button>
          <button onClick={() => navigate("/profile")} className="nav-button">
            Profile
          </button>
          <button
            onClick={() => {
              document.cookie = "auth_token=; path=/; max-age=0";
              navigate("/");
            }}
            className="logout-button"
          >
            Logout
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-content">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{stats.prescriptions}</div>
            <div className="stat-label">Prescriptions</div>
            <button 
              onClick={() => navigate("/prescriptions")}
              className="stat-button"
            >
              View All
            </button>
          </div>

          <div className="stat-card">
            <div className="stat-number">{stats.notes}</div>
            <div className="stat-label">Notes</div>
            <button 
              onClick={() => navigate("/notes")}
              className="stat-button"
            >
              View All
            </button>
          </div>

          <div className="stat-card">
            <div className="stat-number">{stats.hasProfile ? "✓" : "✗"}</div>
            <div className="stat-label">Doctor Profile</div>
            <button 
              onClick={() => navigate("/profile")}
              className="stat-button"
            >
              {stats.hasProfile ? "Edit Profile" : "Create Profile"}
            </button>
          </div>
        </div>

        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="action-buttons">
            <button 
              onClick={() => navigate("/prescriptions")}
              className="action-button primary"
            >
              Add New Prescription
            </button>
            <button 
              onClick={() => navigate("/notes")}
              className="action-button secondary"
            >
              Add New Note
            </button>
            {!stats.hasProfile && (
              <button 
                onClick={() => navigate("/profile")}
                className="action-button accent"
              >
                Create Doctor Profile
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
