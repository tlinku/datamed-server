import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./notes.css";
import { getToken } from "../keycloak";

function Notes() {
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
  const navigate = useNavigate();
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedNote, setSelectedNote] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    content: "",
  });


  const fetchNotes = async () => {
    try {
      const token = getToken();
      if (!token) {
        navigate("/");
        return;
      }

      const response = await fetch(`${apiUrl}/notes`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        document.cookie = "auth_token=; path=/; max-age=0";
        navigate("/");
        return;
      }

      if (!response.ok) throw new Error("Failed to fetch notes");
      const data = await response.json();
      setNotes(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = getToken();
      if (!token) return;

      const url = selectedNote
        ? `${apiUrl}/notes/${selectedNote.id}`
        : `${apiUrl}/notes`;

      const response = await fetch(url, {
        method: selectedNote ? "PUT" : "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error("Failed to save note");

      await fetchNotes();
      setShowAddForm(false);
      setSelectedNote(null);
      setFormData({ name: "", content: "" });
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (noteId) => {
    if (!window.confirm("Are you sure you want to delete this note?")) return;

    try {
      const token = getToken();
      if (!token) return;

      const response = await fetch(`${apiUrl}/notes/${noteId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to delete note");
      await fetchNotes();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = async (note) => {
    try {
      const token = getToken();
      if (!token) return;

      const response = await fetch(`${apiUrl}/notes/${note.id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to fetch note");
      const data = await response.json();
      const noteContent = JSON.parse(data.note);

      setSelectedNote(note);
      setFormData({
        name: noteContent.name,
        content: noteContent.content,
      });
      setShowAddForm(true);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="notes-page">
      <div className="header">
        <h1>Notes</h1>
        <div className="header-buttons">
          <button
            onClick={() => navigate("/prescriptions")}
            className="nav-button"
          >
            Prescriptions
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
          <button
            onClick={() => {
              setShowAddForm(!showAddForm);
              setSelectedNote(null);
              setFormData({ name: "", content: "" });
            }}
            className="add-button"
          >
            {showAddForm ? "Cancel" : "Add Note"}
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showAddForm && (
        <form onSubmit={handleSubmit} className="note-form">
          <div className="form-group">
            <label>Title:</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
            />
          </div>
          <div className="form-group">
            <label>Content:</label>
            <textarea
              required
              value={formData.content}
              onChange={(e) =>
                setFormData({ ...formData, content: e.target.value })
              }
              rows="4"
            />
          </div>
          <button type="submit">
            {selectedNote ? "Update Note" : "Save Note"}
          </button>
        </form>
      )}

      {loading ? (
        <div className="loading">Loading notes...</div>
      ) : (
        <div className="notes-grid">
          {notes.map((note) => {
            let noteContent;
            try {
              noteContent =
                typeof note.note === "string"
                  ? JSON.parse(note.note)
                  : note.note;
            } catch (e) {
              console.error("Failed to parse note:", note);
              noteContent = { name: "Error", content: "Failed to load note" };
            }
            return (
              <div key={note.id} className="note-card">
                <div className="note-header">
                  <h3>{noteContent.name}</h3>
                  <div className="note-actions">
                    <button
                      onClick={() => handleEdit(note)}
                      className="edit-button"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(note.id)}
                      className="delete-button"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <p className="note-content">{noteContent.content}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default Notes;
