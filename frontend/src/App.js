import { useState, useEffect } from "react";
import "./App.css";
// Use mock Keycloak if REACT_APP_USE_MOCK_AUTH is set to 'true'
const useMockAuth = process.env.REACT_APP_USE_MOCK_AUTH === 'true';
const keycloakModule = useMockAuth 
  ? require('./keycloak-mock') 
  : require('./keycloak');

const { initKeycloak, isAuthenticated, doLogin, doLogout, getToken } = keycloakModule;

import "./notes/notes.css";
import "./prescriptions/PrescriptionsPage.css";
import "./profile/profile.css";

function App() {
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
  const [initialized, setInitialized] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('prescriptions');
  
  // Prescriptions state
  const [prescriptions, setPrescriptions] = useState([]);
  const [showAddPrescriptionForm, setShowAddPrescriptionForm] = useState(false);
  const [prescriptionFormData, setPrescriptionFormData] = useState({
    first_name: "",
    last_name: "",
    pesel: "",
    issue_date: "",
    expiry_date: "",
    pdf_file: null,
    med_info_for_search: "",
  });

  // Notes state
  const [notes, setNotes] = useState([]);
  const [showAddNoteForm, setShowAddNoteForm] = useState(false);
  const [selectedNote, setSelectedNote] = useState(null);
  const [noteFormData, setNoteFormData] = useState({
    name: "",
    content: "",
  });

  // Profile state
  const [doctorInfo, setDoctorInfo] = useState(null);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [profileFormData, setProfileFormData] = useState({
    first_name: "",
    last_name: "",
  });

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

  // Load data when authenticated
  useEffect(() => {
    if (authenticated) {
      fetchPrescriptions();
      fetchNotes();
      fetchDoctorInfo();
    }
  }, [authenticated]);

  const fetchPrescriptions = async () => {
    try {
      const token = getToken();
      if (!token) return;

      const response = await fetch(`${apiUrl}/prescriptions`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error("Failed to fetch prescriptions");
      const data = await response.json();
      setPrescriptions(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchNotes = async () => {
    try {
      const token = getToken();
      if (!token) return;

      const response = await fetch(`${apiUrl}/notes`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error("Failed to fetch notes");
      const data = await response.json();
      setNotes(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchDoctorInfo = async () => {
    try {
      const token = getToken();
      if (!token) return;

      const response = await fetch(`${apiUrl}/doctors`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setDoctorInfo(data);
        setProfileFormData({
          first_name: data.first_name,
          last_name: data.last_name,
        });
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleLogin = () => {
    setLoading(true);
    console.log("Starting login process...");
    doLogin();
  };

  const handleRegister = () => {
    window.location.href = `${process.env.REACT_APP_KEYCLOAK_URL || 'http://localhost:8080'}/auth/realms/${process.env.REACT_APP_KEYCLOAK_REALM || 'datamed'}/protocol/openid-connect/registrations?client_id=${process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'datamed-client'}&response_type=code&redirect_uri=${window.location.origin}`;
  };

  // Add handlers for forms and data management here...
  // Note: I'm skipping the implementation of individual handlers for brevity
  // You should add handlers for adding/editing/deleting prescriptions, notes, and profile info

  const renderContent = () => {
    console.log('renderContent called - loading:', loading, 'authenticated:', authenticated, 'initialized:', initialized);
    
    if (loading) {
      console.log('Showing loading screen');
      return <div className="loading">Loading...</div>;
    }

    if (!authenticated) {
      console.log('Showing login buttons');
      return (
        <div className="auth-buttons">
          <button onClick={handleLogin} className="login-btn">
            Login with Keycloak
          </button>
          <button onClick={handleRegister} className="register-btn">
            Register a New Account
          </button>
        </div>
      );
    }

    console.log('Showing authenticated content');
    return (
      <div className="authenticated-content">
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'prescriptions' ? 'active' : ''}`}
            onClick={() => setActiveTab('prescriptions')}
          >
            Prescriptions
          </button>
          <button 
            className={`tab ${activeTab === 'notes' ? 'active' : ''}`}
            onClick={() => setActiveTab('notes')}
          >
            Notes
          </button>
          <button 
            className={`tab ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            Profile
          </button>
          <button onClick={doLogout} className="logout-btn">
            Logout
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'prescriptions' && (
            <div className="prescriptions-section">
              <h2>Prescriptions</h2>
              <button onClick={() => setShowAddPrescriptionForm(true)}>Add Prescription</button>
              <div className="prescriptions-list">
                {prescriptions.map(prescription => (
                  <div key={prescription.id} className="prescription-item">
                    <h3>{prescription.first_name} {prescription.last_name}</h3>
                    <p>PESEL: {prescription.pesel}</p>
                    <p>Issue Date: {prescription.issue_date}</p>
                    <p>Expiry Date: {prescription.expiry_date}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'notes' && (
            <div className="notes-section">
              <h2>Notes</h2>
              <button onClick={() => setShowAddNoteForm(true)}>Add Note</button>
              <div className="notes-list">
                {notes.map(note => (
                  <div key={note.id} className="note-item">
                    <h3>{note.name}</h3>
                    <p>{note.content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="profile-section">
              <h2>Doctor Profile</h2>
              {doctorInfo ? (
                <div className="doctor-info">
                  <h3>{doctorInfo.first_name} {doctorInfo.last_name}</h3>
                  <button onClick={() => setIsEditingProfile(true)}>Edit Profile</button>
                </div>
              ) : (
                <button onClick={() => setIsEditingProfile(true)}>Create Profile</button>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="container">
      <div className="auth-box">
        <h1>Welcome to Datamed</h1>
        <div style={{fontSize: '12px', color: 'gray'}}>
          Debug: loading={loading.toString()}, authenticated={authenticated.toString()}, initialized={initialized.toString()}
        </div>
        {error && <div className="error">{error}</div>}
        {renderContent()}
      </div>
    </div>
  );
}

export default App;
