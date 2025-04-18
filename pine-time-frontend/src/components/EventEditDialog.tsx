import React, { useState, useEffect } from "react";
import axios from "axios";

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

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

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

  useEffect(() => {
    if (event) {
      // Editing: use event (has id)
      setForm({ ...defaultForm, ...event });
    } else {
      // Creating: use defaultForm
      setForm(defaultForm);
    }
  }, [event, open]);

  const token = localStorage.getItem("admin_token");

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
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      let res;
      if (isCreate) {
        res = await axios.post(`${API_BASE}/events/`, form, {
          headers: { Authorization: `Bearer ${token}` },
        });
      } else if (event && 'id' in event) {
        res = await axios.put(`${API_BASE}/events/${event.id}`, form, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }
      if (res) {
        onSave(res.data);
        onClose();
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to save event.");
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
          <input name="title" value={form.title} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>Description<br />
          <textarea name="description" value={form.description} onChange={handleChange} required style={{ width: "100%" }} rows={3} />
        </label><br /><br />
        <label>Event Type<br />
          <select name="event_type" value={form.event_type} onChange={handleChange} style={{ width: "100%" }}>
            <option value="general">General</option>
            <option value="trivia">Trivia</option>
            <option value="game">Game</option>
            <option value="mystery">Murder Mystery</option>
            <option value="workshop">Workshop</option>
            <option value="other">Other</option>
          </select>
        </label><br /><br />
        <label>Location<br />
          <input name="location" value={form.location} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>Start Time<br />
          <input name="start_time" type="datetime-local" value={form.start_time.slice(0,16)} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>End Time<br />
          <input name="end_time" type="datetime-local" value={form.end_time.slice(0,16)} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>Max Participants<br />
          <input name="max_participants" type="number" min={1} value={form.max_participants} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>Points Reward<br />
          <input name="points_reward" type="number" min={0} value={form.points_reward} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>Image URL<br />
          <input name="image_url" value={form.image_url || ""} onChange={handleChange} style={{ width: "100%" }} />
        </label><br /><br />
        <label>Price<br />
          <input name="price" type="number" min={0} value={form.price || 0} onChange={handleChange} style={{ width: "100%" }} />
        </label><br /><br />
        <label>
          <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} /> Active
        </label><br /><br />
        {error && <div style={{ color: "red" }}>{error}</div>}
        <button type="submit" disabled={loading} style={{ marginRight: 8 }}>{isCreate ? "Create" : "Save"}</button>
        <button type="button" onClick={onClose} disabled={loading}>Cancel</button>
      </form>
    </div>
  );
};

export default EventEditDialog;
