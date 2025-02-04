import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./profile.css";

function Profile() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [doctorInfo, setDoctorInfo] = useState(null);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
  });
  const [isEditing, setIsEditing] = useState(false);

  const getToken = () => {
    return document.cookie
      .split("; ")
      .find((row) => row.startsWith("auth_token="))
      ?.split("=")[1];
  };

  const fetchDoctorInfo = async () => {
    try {
      const token = getToken();
      if (!token) {
        navigate("/");
        return;
      }

      const response = await fetch("https://localhost:5000/doctors", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 404) {
        setDoctorInfo(null);
        return;
      }

      if (!response.ok) throw new Error("Failed to fetch doctor info");

      const data = await response.json();
      setDoctorInfo(data);
      setFormData({
        first_name: data.first_name,
        last_name: data.last_name,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDoctorInfo();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const token = getToken();
      if (!token) return;

      const method = doctorInfo ? "PUT" : "POST";

      const response = await fetch("https://localhost:5000/doctors", {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error("Failed to save doctor info");

      await fetchDoctorInfo();
      setIsEditing(false);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async () => {
    if (
      !window.confirm(
        "Are you sure you want to delete your doctor information?"
      )
    )
      return;

    try {
      const token = getToken();
      if (!token) return;

      const response = await fetch("https://localhost:5000/doctors", {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to delete doctor info");

      setDoctorInfo(null);
      setFormData({
        first_name: "",
        last_name: "",
      });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="profile-page">
      <div className="header">
        <h1>Doctor Profile</h1>
        <div className="header-buttons">
          <button
            onClick={() => navigate("/prescriptions")}
            className="nav-button"
          >
            Prescriptions
          </button>
          <button onClick={() => navigate("/notes")} className="nav-button">
            Notes
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

      {loading ? (
        <div className="loading">Loading profile...</div>
      ) : (
        <div className="profile-content">
          {!isEditing && doctorInfo ? (
            <div className="info-display">
              <h2>Current Information</h2>
              <p>
                <strong>First Name:</strong> {doctorInfo.first_name}
              </p>
              <p>
                <strong>Last Name:</strong> {doctorInfo.last_name}
              </p>
              <div className="button-group">
                <button
                  onClick={() => setIsEditing(true)}
                  className="edit-button"
                >
                  Edit Information
                </button>
                <button onClick={handleDelete} className="delete-button">
                  Delete Information
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="profile-form">
              <h2>
                {doctorInfo ? "Edit Information" : "Add Doctor Information"}
              </h2>
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
              <div className="button-group">
                <button type="submit" className="save-button">
                  {doctorInfo ? "Update" : "Save"}
                </button>
                {doctorInfo && (
                  <button
                    type="button"
                    onClick={() => setIsEditing(false)}
                    className="cancel-button"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          )}
        </div>
      )}
    </div>
  );
}

export default Profile;
