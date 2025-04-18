import React, { useState, useEffect } from "react";
import api from "../api/client";

interface EventBase {
  title: string;
  description: string;
  event_type: string;
  location: string;
  start_time: string;
  end_time: string;
  max_participants: number;
  points_reward: number;
  is_active: boolean;
  image_url?: string;
  price?: number;
}
interface Event extends EventBase {
  id: number;
}
// For create, use EventBase; for edit, use Event


interface Props {
  event: Event | null;
  open: boolean;
  onClose: () => void;
  onSave: (updated: Event) => void;
  isCreate?: boolean;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const defaultForm: EventBase = {
  title: "",
  description: "",
  event_type: "general",
  location: "",
  start_time: "",
  end_time: "",
  max_participants: 50,
  points_reward: 0,
  is_active: true,
  image_url: "",
  price: 0,
};

const EventEditDialog: React.FC<Props> = ({ event, open, onClose, onSave, isCreate }) => {
  // Use EventBase for create, Event for edit

  const [form, setForm] = useState<EventBase>(defaultForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    if (event) {
      setForm({ ...defaultForm, ...event });
    } else {
      setForm(defaultForm);
    }
    setError(null);
    setSuccess(null);
    setValidationErrors({});
  }, [event, open]);

  const token = localStorage.getItem("admin_token");

  const validate = (): boolean => {
    const errors: { [key: string]: string } = {};
    if (!form.title.trim()) errors.title = "Title is required.";
    if (!form.description.trim()) errors.description = "Description is required.";
    if (!form.location.trim()) errors.location = "Location is required.";
    if (!form.start_time) errors.start_time = "Start time is required.";
    if (!form.end_time) errors.end_time = "End time is required.";
    if (form.max_participants < 1) errors.max_participants = "Must be at least 1.";
    if (form.points_reward < 0) errors.points_reward = "Cannot be negative.";
    if (form.price !== undefined && form.price < 0) errors.price = "Cannot be negative.";
    if (form.start_time && form.end_time && form.end_time < form.start_time) errors.end_time = "End time must be after start time.";
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    let fieldValue: any = value;
    if (type === "checkbox" && "checked" in e.target) {
      fieldValue = (e.target as HTMLInputElement).checked;
    }
    setForm((prev) => ({
      ...prev,
      [name]: fieldValue,
    }));
    setValidationErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors[name];
      return newErrors;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    if (!validate()) return;
    setLoading(true);
    try {
      let res;
      const axiosConfig = {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 10000, // 10s timeout
      };
      if (isCreate) {
        res = await api.post(`${API_BASE}/events/`, form, axiosConfig);
      } else if (event && 'id' in event) {
        res = await api.put(`${API_BASE}/events/${event.id}`, form, axiosConfig);
      }
      if (res) {
        onSave(res.data);
        setSuccess(isCreate ? "Event created successfully!" : "Event updated successfully!");
        setTimeout(() => {
          setSuccess(null);
          onClose();
        }, 1200);
      }
    } catch (err: any) {
      // Log error for debugging
      console.error("Event save error:", err);
      if (err.code === 'ECONNABORTED') {
        setError("Request timed out. Please check your connection and try again.");
      } else if (err?.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Failed to save event. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.3)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <form onSubmit={handleSubmit} style={{ background: "white", padding: 24, borderRadius: 8, minWidth: 350, maxWidth: 500 }}>
        <h3>{isCreate ? "Create Event" : "Edit Event"}</h3>
        <label>Title<br />
          <input name="title" value={form.title} onChange={handleChange} required style={{ width: "100%" }} disabled={loading}/>
        </label>
        {validationErrors["title"] && <div style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors["title"]}</div>}
        <br />
        <label>Description<br />
          <textarea name="description" value={form.description} onChange={handleChange} required style={{ width: "100%" }} rows={3} disabled={loading}/>
        </label>
        {validationErrors["description"] && <div style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors["description"]}</div>}
        <br />
        <label>Event Type<br />
          <select name="event_type" value={form.event_type} onChange={handleChange} style={{ width: "100%" }} disabled={loading}>
            <option value="general">General</option>
            <option value="trivia">Trivia</option>
            <option value="game">Game</option>
            <option value="mystery">Murder Mystery</option>
            <option value="workshop">Workshop</option>
            <option value="other">Other</option>
          </select>
        </label>
        <br />
        <label>Location<br />
          <input name="location" value={form.location} onChange={handleChange} required style={{ width: "100%" }} disabled={loading}/>
        </label>
        {validationErrors["location"] && <div style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors["location"]}</div>}
        <br />
        <label>Start Time<br />
          <input name="start_time" type="datetime-local" value={form.start_time.slice(0,16)} onChange={handleChange} required style={{ width: "100%" }} disabled={loading}/>
        </label>
        {validationErrors["start_time"] && <div style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors["start_time"]}</div>}
        <br />
        <label>End Time<br />
          <input name="end_time" type="datetime-local" value={form.end_time.slice(0,16)} onChange={handleChange} required style={{ width: "100%" }} disabled={loading}/>
        </label>
        {validationErrors["end_time"] && <div style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors["end_time"]}</div>}
        <br />
        <label>Max Participants<br />
          <input name="max_participants" type="number" min={1} value={form.max_participants} onChange={handleChange} required style={{ width: "100%" }} disabled={loading}/>
        </label>
        {validationErrors["max_participants"] && <div style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors["max_participants"]}</div>}
        <br />
        <label>Points Reward<br />
          <input name="points_reward" type="number" min={0} value={form.points_reward} onChange={handleChange} required style={{ width: "100%" }} disabled={loading}/>
        </label>
        {validationErrors["points_reward"] && <div style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors["points_reward"]}</div>}
        <br />
        <label>Image URL<br />
          <input name="image_url" value={form.image_url || ""} onChange={handleChange} style={{ width: "100%" }} disabled={loading}/>
        </label>
        <br />
        <label>Price<br />
          <input name="price" type="number" min={0} value={form.price || 0} onChange={handleChange} style={{ width: "100%" }} disabled={loading}/>
        </label>
        {validationErrors["price"] && <div style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors["price"]}</div>}
        <br />
        <label>
          <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} disabled={loading}/> Active
        </label>
        <br /><br />
        {error && <div style={{ color: "#d32f2f", marginBottom: 8 }}>{error}</div>}
        {success && <div style={{ color: "#388e3c", marginBottom: 8 }}>{success}</div>}
        <button type="submit" disabled={loading} style={{ marginRight: 8, minWidth: 90 }}>
          {loading ? (isCreate ? "Creating..." : "Saving...") : (isCreate ? "Create" : "Save")}
        </button>
        <button type="button" onClick={onClose} disabled={loading}>Cancel</button>
      </form>
    </div>
  );
};

export default EventEditDialog;
