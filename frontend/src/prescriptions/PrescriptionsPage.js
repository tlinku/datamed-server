import { useState, useEffect } from "react";
import "./PrescriptionsPage.css";
import { useNavigate } from "react-router-dom";

function PrescriptionsPage() {
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
  });

  useEffect(() => {
    fetchPrescriptions();
  }, []);

  const fetchPrescriptions = async () => {
    console.log(document.cookie);
    const token = document.cookie;
    try {
      const response = await fetch("http://localhost:5000/prescriptions", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      const responce_data = response;
      if (response.status === 401) {
        console.log(responce_data.json());
        return;
      }

      const data = await response.json();
      setPrescriptions(data);
    } catch (err) {
      console.error("Fetch error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    const token = document.cookie;
    try {
      let response;

      if (formData.pdf_file) {
        const formDataToSend = new FormData();
        Object.keys(formData).forEach((key) => {
          if (key === "pdf_file" && formData[key]) {
            formDataToSend.append("pdf_file", formData[key]);
          } else {
            formDataToSend.append(key, formData[key]);
          }
        });

        response = await fetch("http://localhost:5000/prescriptions", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formDataToSend,
        });
      } else {
        const { pdf_file, ...dataWithoutFile } = formData;
        response = await fetch("http://localhost:5000/prescriptions/no-pdf", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(dataWithoutFile),
        });
      }

      if (!response.ok) throw new Error("Failed to add prescription");

      await fetchPrescriptions();
      setShowAddForm(false);
      setFormData({
        first_name: "",
        last_name: "",
        pesel: "",
        issue_date: "",
        expiry_date: "",
        pdf_file: null,
      });
    } catch (err) {
      setError(err.message);
    }
  };
  const handleLogout = () => {
    document.cookie = "";
    window.location.href = "/";
  };
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this prescription?"))
      return;

    const token = document.cookie
      .split("; ")
      .find((row) => row.startsWith("auth_token="))
      ?.split("=")[1];

    try {
      const response = await fetch(
        `http://localhost:5000/prescriptions/${id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) throw new Error("Failed to delete prescription");
      await fetchPrescriptions();
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredPrescriptions = prescriptions.filter(
    (p) =>
      p.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.pesel.includes(searchTerm)
  );

  if (loading) return <div className="loading">Loading prescriptions...</div>;

  return (
    <div className="prescriptions-page">
      <div className="header">
        <h1>Prescriptions Management</h1>
        <div className="header-buttons">
          <button
            className="add-button"
            onClick={() => setShowAddForm(!showAddForm)}
          >
            {showAddForm ? "Cancel" : "Add New Prescription"}
          </button>
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showAddForm && (
        <form onSubmit={handleSubmit} className="prescription-form">
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
          <div className="form-group">
            <label>PESEL:</label>
            <input
              type="text"
              required
              pattern="[0-9]{11}"
              value={formData.pesel}
              onChange={(e) =>
                setFormData({ ...formData, pesel: e.target.value })
              }
            />
          </div>
          <div className="form-row">
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
            <label>PDF File:</label>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) =>
                setFormData({ ...formData, pdf_file: e.target.files[0] })
              }
            />
          </div>
          <button type="submit" className="submit-button">
            Add Prescription
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
        {filteredPrescriptions.map((prescription) => (
          <div key={prescription.id} className="prescription-card">
            <div className="card-header">
              <h3>
                {prescription.first_name} {prescription.last_name}
              </h3>
              <button
                className="delete-button"
                onClick={() => handleDelete(prescription.id)}
              >
                ×
              </button>
            </div>
            <p>
              <strong>PESEL:</strong> {prescription.pesel}
            </p>
            <p>
              <strong>Issue Date:</strong>{" "}
              {new Date(prescription.issue_date).toLocaleDateString()}
            </p>
            <p>
              <strong>Expiry Date:</strong>{" "}
              {new Date(prescription.expiry_date).toLocaleDateString()}
            </p>
            {prescription.pdf_url && (
              <a
                href={prescription.pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                className="view-pdf-button"
              >
                View PDF
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default PrescriptionsPage;
