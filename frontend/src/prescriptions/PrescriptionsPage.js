import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./PrescriptionsPage.css";
import { getToken, doLogout } from "../keycloak";

function PrescriptionsPage() {
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
  const navigate = useNavigate();
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    pesel: "",
    issue_date: "",
    expiry_date: "",
    pdf_file: null,
    med_info_for_search: "",
  });
  const [advancedTools, setAdvancedTools] = useState(false);
  const [uploadWithPdf, setUploadWithPdf] = useState(true); 

  const [searchByID, setSearchByID] = useState("");
  const [singlePrescription, setSinglePrescription] = useState(null);
  const [searchPerson, setSearchPerson] = useState({
    first_name: "",
    last_name: "",
    start_date: "",
    end_date: "",
  });
  const [searchMedication, setSearchMedication] = useState("");
  const [deleteName, setDeleteName] = useState({
    first_name: "",
    last_name: "",
  });
  const [deleteExpiredDate, setDeleteExpiredDate] = useState("");
  const [accountInfo, setAccountInfo] = useState({ email: "", password: "" });
  const [newPassword, setNewPassword] = useState({
    email: "",
    old_password: "",
    new_password: "",
  });
  const fetchPrescriptions = async () => {
    setLoading(true);
    try {
      const token = getToken();
      const response = await fetch(`${apiUrl}/prescriptions`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        credentials: "include",
      });
      if (response.status === 401) {
        return;
      }
      if (response.status === 404) {
        setPrescriptions([]);
        return;
      }
      if (!response.ok) throw new Error("Failed to fetch prescriptions");
      const data = await response.json();
      setPrescriptions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrescriptions();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const token = getToken();
      if (!token) return setError("No token found");

      let response;
      if (uploadWithPdf && formData.pdf_file) {
        const formDataToSend = new FormData();
        Object.keys(formData).forEach((key) => {
          if (key === "pdf_file" && formData[key]) {
            formDataToSend.append("pdf_file", formData[key]);
          } else if (key !== "pdf_file") {
            formDataToSend.append(key, formData[key]);
          }
        });
        response = await fetch(`${apiUrl}/prescriptions`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formDataToSend,
          credentials: "include",
        });
      } else {
        const { pdf_file, ...dataWithoutFile } = formData;
        response = await fetch(`${apiUrl}/prescriptions/no-pdf`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(dataWithoutFile),
          credentials: "include",
        });
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to add prescription");
      }
      
      await fetchPrescriptions();
      setShowAddForm(false);
      setUploadWithPdf(true); 
      setFormData({
        first_name: "",
        last_name: "",
        pesel: "",
        issue_date: "",
        expiry_date: "",
        pdf_file: null,
        med_info_for_search: "",
      });
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeletePrescription = async (prescriptionId) => {
    if (!window.confirm("Are you sure you want to delete this prescription?"))
      return;
    try {
      const token = getToken();
      if (!token) return setError("No token found");

      const response = await fetch(
        `${apiUrl}/prescriptions/${prescriptionId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
        }
      );
      if (!response.ok) throw new Error("Failed to delete prescription");
      await fetchPrescriptions();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleGetById = async () => {
    if (!searchByID) return;
    setSinglePrescription(null);
    try {
      const token = getToken();
      const response = await fetch(
        `${apiUrl}/prescriptions/${searchByID}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
        }
      );
      if (!response.ok) throw new Error("Could not fetch prescription by ID");
      const data = await response.json();
      setSinglePrescription(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSearchByPerson = async () => {
    try {
      const token = getToken();
      const queryParams = new URLSearchParams({
        first_name: searchPerson.first_name,
        last_name: searchPerson.last_name,
        start_date: searchPerson.start_date,
        end_date: searchPerson.end_date,
      });
      const response = await fetch(
        `${apiUrl}/prescriptions/search/person?${queryParams}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
        }
      );
      if (!response.ok) throw new Error("Failed to search by person");
      const data = await response.json();
      setPrescriptions(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSearchByMedication = async () => {
    try {
      const token = getToken();
      const response = await fetch(
        `${apiUrl}/prescriptions/search/medication?medication=${searchMedication}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
        }
      );
      if (!response.ok) throw new Error("Failed to search by medication");
      const data = await response.json();
      setPrescriptions(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteByName = async () => {
    try {
      const token = getToken();
      const response = await fetch(
        `${apiUrl}/prescriptions/person`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
          body: JSON.stringify(deleteName),
        }
      );
      if (!response.ok) throw new Error("Failed to delete by name");
      await fetchPrescriptions();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteExpired = async () => {
    try {
      const token = getToken();
      const response = await fetch(
        `${apiUrl}/prescriptions/expired?before_date=${deleteExpiredDate}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
        }
      );
      if (!response.ok)
        throw new Error("Failed to delete expired prescriptions");
      await fetchPrescriptions();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleChangePassword = async () => {
    try {
      const token = getToken();
      const response = await fetch(`${apiUrl}/auth/password`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        credentials: "include",
        body: JSON.stringify(newPassword),
      });
      if (!response.ok) throw new Error("Failed to update password");
      alert("Password updated successfully");
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm("Are you sure you want to delete your entire account?"))
      return;
    try {
      const token = getToken();
      const response = await fetch(`${apiUrl}/auth/account`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        credentials: "include",
        body: JSON.stringify(accountInfo),
      });
      if (!response.ok) throw new Error("Failed to delete account");
      alert("Account deleted successfully");
      document.cookie = "auth_token=; path=/; max-age=0";
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  };


  if (loading) return <div className="loading">Loading prescriptions...</div>;

  return (
    <div className="prescriptions-page">      
      <div className="header">
        <div className="header-buttons">
          <button onClick={() => navigate("/dashboard")} className="nav-button">
            🏠 Dashboard
          </button>
          <button onClick={() => navigate("/notes")} className="nav-button">
            📝 Notes
          </button>
          <button onClick={() => navigate("/profile")} className="nav-button">
            👤 Profile
          </button>
          <button
            onClick={() => doLogout(navigate)}
            className="logout-button"
          >
            🚪 Logout
          </button>
        </div>
        <div className="header-buttons">
          <button 
            onClick={() => setShowAddForm(!showAddForm)}
            className={showAddForm ? "nav-button" : "add-button"}
          >
            {showAddForm ? "❌ Cancel" : "➕ Add Prescription"}
          </button>
          <button 
            onClick={() => setAdvancedTools(!advancedTools)}
            className="upload-option-toggle"
          >
            {advancedTools ? "🔧 Hide Tools" : "🔧 Advanced Tools"}
          </button>
        </div>
      </div>

      {error && <div className="error-message">⚠️ {error}</div>}

      {showAddForm && (
        <form onSubmit={handleSubmit} className="prescription-form">
          <div className="medical-header">
            <h3>📋 Add New Prescription</h3>
          </div>
          
          <div className="upload-options">
            <h4>Choose prescription type:</h4>
            <div className="option-buttons">
              <button
                type="button"
                className={`option-button ${uploadWithPdf ? 'active' : ''}`}
                onClick={() => setUploadWithPdf(true)}
              >
                📄 With PDF Document
              </button>
              <button
                type="button"
                className={`option-button ${!uploadWithPdf ? 'active' : ''}`}
                onClick={() => setUploadWithPdf(false)}
              >
                ✍️ Manual Entry Only
              </button>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>First Name:</label>
              <input
                type="text"
                required
                value={formData.first_name}
                onChange={(e) =>
                  setFormData({ ...formData, first_name: e.target.value })
                }
              />
            </div>
            <div className="form-group">
              <label>Last Name:</label>
              <input
                type="text"
                required
                value={formData.last_name}
                onChange={(e) =>
                  setFormData({ ...formData, last_name: e.target.value })
                }
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>PESEL:</label>
              <input
                type="text"
                required
                pattern="[0-9]{11}"
                maxLength="11"
                value={formData.pesel}
                onChange={(e) =>
                  setFormData({ ...formData, pesel: e.target.value })
                }
              />
            </div>
            <div className="form-group">
              <label>Issue Date:</label>
              <input
                type="date"
                required
                value={formData.issue_date}
                onChange={(e) =>
                  setFormData({ ...formData, issue_date: e.target.value })
                }
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Expiry Date:</label>
              <input
                type="date"
                required
                value={formData.expiry_date}
                onChange={(e) =>
                  setFormData({ ...formData, expiry_date: e.target.value })
                }
              />
            </div>
          </div>

          <div className="form-group">
            <label>💊 Medication Information:</label>
            <textarea
              rows="3"
              placeholder="Enter medication details, dosage, instructions..."
              value={formData.med_info_for_search}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  med_info_for_search: e.target.value,
                })
              }
            />
          </div>

          {uploadWithPdf && (
            <div className="form-group">
              <label>📄 PDF Document:</label>
              <input
                type="file"
                onChange={(e) =>
                  setFormData({ ...formData, pdf_file: e.target.files[0] })
                }
                accept=".pdf"
                required={uploadWithPdf}
              />
            </div>
          )}

          <button type="submit" className="submit-button">
            {uploadWithPdf ? '💾 Save Prescription with PDF' : '💾 Save Prescription'}
          </button>
        </form>
      )}

      <div className="search-box">
        <input
          type="text"
          placeholder="Search by name or PESEL..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="prescriptions-grid">
        {loading ? (
          <div className="loading">⏳ Loading prescriptions...</div>
        ) : prescriptions.length === 0 ? (
          <div className="loading">📝 No prescriptions found. Add your first prescription above!</div>
        ) : (
          prescriptions
            .filter((p) =>
              [p.first_name, p.last_name, p.pesel, p.med_info_for_search || ""].some((field) =>
                field.toLowerCase().includes(searchTerm.toLowerCase())
              )
            )
            .map((p) => {
              const isExpired = new Date(p.expiry_date) < new Date();
              return (
                <div key={p.id} className="prescription-card">
                  <div className="card-header">
                    <div>
                      <h4>👤 {p.first_name} {p.last_name}</h4>
                      <span className={`status-badge ${isExpired ? 'status-expired' : 'status-active'}`}>
                        {isExpired ? '❌ EXPIRED' : '✅ ACTIVE'}
                      </span>
                    </div>
                    <button 
                      onClick={() => handleDeletePrescription(p.id)}
                      className="delete-button"
                      title="Delete prescription"
                    >
                      🗑️
                    </button>
                  </div>
                  <div className="prescription-info">
                    <p><strong>🆔 PESEL:</strong> {p.pesel}</p>
                    <p><strong>📅 Issue Date:</strong> {new Date(p.issue_date).toLocaleDateString()}</p>
                    <p><strong>⏰ Expiry Date:</strong> {new Date(p.expiry_date).toLocaleDateString()}</p>
                    {p.med_info_for_search && (
                      <p><strong>💊 Medication:</strong> {p.med_info_for_search}</p>
                    )}
                    {p.pdf_url ? (
                      <a 
                        href={p.pdf_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="view-pdf-button"
                      >
                        📄 View PDF Document
                      </a>
                    ) : (
                      <div className="no-pdf-notice">
                        📝 Manual entry - No PDF document
                      </div>
                    )}
                  </div>
                </div>
              );
            })
        )}
      </div>

      {advancedTools && (
        <div className="advanced-tools">
          <h2>Advanced Tools</h2>
          <div className="tool-box">
            <h3>Get Prescription by ID</h3>
            <input
              type="text"
              placeholder="ID..."
              value={searchByID}
              onChange={(e) => setSearchByID(e.target.value)}
            />
            <button onClick={handleGetById}>Fetch</button>
            {singlePrescription && (
              <div className="single-prescription">
                <pre>{JSON.stringify(singlePrescription, null, 2)}</pre>
              </div>
            )}
          </div>

          <div className="tool-box">
            <h3>Search by Person</h3>
            <input
              type="text"
              placeholder="First Name"
              value={searchPerson.first_name}
              onChange={(e) =>
                setSearchPerson({ ...searchPerson, first_name: e.target.value })
              }
            />
            <input
              type="text"
              placeholder="Last Name"
              value={searchPerson.last_name}
              onChange={(e) =>
                setSearchPerson({ ...searchPerson, last_name: e.target.value })
              }
            />
            <input
              type="date"
              value={searchPerson.start_date}
              onChange={(e) =>
                setSearchPerson({ ...searchPerson, start_date: e.target.value })
              }
            />
            <input
              type="date"
              value={searchPerson.end_date}
              onChange={(e) =>
                setSearchPerson({ ...searchPerson, end_date: e.target.value })
              }
            />
            <button onClick={handleSearchByPerson}>Search</button>
          </div>

          <div className="tool-box">
            <h3>Search by Medication</h3>
            <input
              type="text"
              placeholder="Medication pattern..."
              value={searchMedication}
              onChange={(e) => setSearchMedication(e.target.value)}
            />
            <button onClick={handleSearchByMedication}>Search</button>
          </div>

          <div className="tool-box">
            <h3>Delete by Name</h3>
            <input
              type="text"
              placeholder="First Name"
              value={deleteName.first_name}
              onChange={(e) =>
                setDeleteName({ ...deleteName, first_name: e.target.value })
              }
            />
            <input
              type="text"
              placeholder="Last Name"
              value={deleteName.last_name}
              onChange={(e) =>
                setDeleteName({ ...deleteName, last_name: e.target.value })
              }
            />
            <button onClick={handleDeleteByName}>Delete</button>
          </div>

          <div className="tool-box">
            <h3>Delete Expired</h3>
            <input
              type="date"
              value={deleteExpiredDate}
              onChange={(e) => setDeleteExpiredDate(e.target.value)}
            />
            <button onClick={handleDeleteExpired}>
              Delete Expired Before Date
            </button>
          </div>

          <div className="tool-box">
            <h3>Change Password</h3>
            <input
              type="email"
              placeholder="Email"
              value={newPassword.email}
              onChange={(e) =>
                setNewPassword({ ...newPassword, email: e.target.value })
              }
            />
            <input
              type="password"
              placeholder="Old password"
              value={newPassword.old_password}
              onChange={(e) =>
                setNewPassword({ ...newPassword, old_password: e.target.value })
              }
            />
            <input
              type="password"
              placeholder="New password"
              value={newPassword.new_password}
              onChange={(e) =>
                setNewPassword({ ...newPassword, new_password: e.target.value })
              }
            />
            <button onClick={handleChangePassword}>Update Password</button>
          </div>

          <div className="tool-box">
            <h3>Delete Account</h3>
            <input
              type="email"
              placeholder="Email"
              value={accountInfo.email}
              onChange={(e) =>
                setAccountInfo({ ...accountInfo, email: e.target.value })
              }
            />
            <input
              type="password"
              placeholder="Password"
              value={accountInfo.password}
              onChange={(e) =>
                setAccountInfo({ ...accountInfo, password: e.target.value })
              }
            />
            <button onClick={handleDeleteAccount}>Delete Account</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default PrescriptionsPage;
