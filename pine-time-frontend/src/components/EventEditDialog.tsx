import React, { useState, useEffect } from "react";
import api from "../utils/api";
import { Dialog, DialogContent, DialogActions, TextField, Stack, Button, Alert, MenuItem, Checkbox, FormControlLabel } from "@mui/material";
// Removed FormDialog.css; all styling is now via MUI theme and components.

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
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="sm"
      scroll="body"
      PaperProps={{
        sx: {
          borderRadius: 3,
          p: 0,
          m: 0,
          width: '100%',
          maxWidth: 600,
        }
      }}
    >
      <DialogContent>
        <form onSubmit={handleSubmit} autoComplete="off">
          <Stack spacing={2}>
            <TextField
              label="Title"
              name="title"
              value={form.title}
              onChange={handleChange}
              fullWidth
              required
              disabled={loading}
              variant="outlined"
              error={!!validationErrors["title"]}
              helperText={validationErrors["title"] || ''}
            />
            <TextField
              label="Description"
              name="description"
              value={form.description}
              onChange={handleChange}
              fullWidth
              multiline
              minRows={2}
              required
              disabled={loading}
              variant="outlined"
              error={!!validationErrors["description"]}
              helperText={validationErrors["description"] || ''}
            />
            <TextField
              label="Event Type"
              name="event_type"
              value={form.event_type}
              onChange={handleChange}
              fullWidth
              required
              disabled={loading}
              select
              variant="outlined"
            >
              <MenuItem value="general">General</MenuItem>
              <MenuItem value="trivia">Trivia</MenuItem>
              <MenuItem value="game">Game</MenuItem>
              <MenuItem value="mystery">Murder Mystery</MenuItem>
              <MenuItem value="workshop">Workshop</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </TextField>
            <TextField
              label="Location"
              name="location"
              value={form.location}
              onChange={handleChange}
              fullWidth
              required
              disabled={loading}
              variant="outlined"
              error={!!validationErrors["location"]}
              helperText={validationErrors["location"] || ''}
            />
            <TextField
              label="Start Time"
              name="start_time"
              type="datetime-local"
              value={form.start_time}
              onChange={handleChange}
              fullWidth
              required
              disabled={loading}
              InputLabelProps={{ shrink: true }}
              variant="outlined"
              error={!!validationErrors["start_time"]}
              helperText={validationErrors["start_time"] || ''}
            />
            <TextField
              label="End Time"
              name="end_time"
              type="datetime-local"
              value={form.end_time}
              onChange={handleChange}
              fullWidth
              required
              disabled={loading}
              InputLabelProps={{ shrink: true }}
              variant="outlined"
              error={!!validationErrors["end_time"]}
              helperText={validationErrors["end_time"] || ''}
            />
            <TextField
              label="Max Participants"
              name="max_participants"
              type="number"
              value={form.max_participants}
              onChange={handleChange}
              fullWidth
              required
              disabled={loading}
              variant="outlined"
              error={!!validationErrors["max_participants"]}
              helperText={validationErrors["max_participants"] || ''}
            />
            <TextField
              label="Points Reward"
              name="points_reward"
              type="number"
              value={form.points_reward}
              onChange={handleChange}
              fullWidth
              required
              disabled={loading}
              variant="outlined"
              error={!!validationErrors["points_reward"]}
              helperText={validationErrors["points_reward"] || ''}
            />
            <TextField
              label="Image URL"
              name="image_url"
              value={form.image_url || ""}
              onChange={handleChange}
              fullWidth
              disabled={loading}
              variant="outlined"
            />
            <TextField
              label="Price"
              name="price"
              type="number"
              value={form.price || 0}
              onChange={handleChange}
              fullWidth
              disabled={loading}
              variant="outlined"
              error={!!validationErrors["price"]}
              helperText={validationErrors["price"] || ''}
            />
            <FormControlLabel
              control={
                <Checkbox
                  name="is_active"
                  checked={form.is_active}
                  onChange={handleChange}
                  disabled={loading}
                />
              }
              label="Active"
            />
          </Stack>
        </form>
      </DialogContent>
      <DialogActions sx={{ flexDirection: 'column', alignItems: 'stretch', gap: 1, p: 2 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}
        <Stack direction="row" spacing={2} justifyContent="flex-end">
          <Button onClick={onClose} disabled={loading} variant="outlined">Cancel</Button>
          <Button onClick={handleSubmit} disabled={loading} variant="contained" color="primary">
            {isCreate ? "Create" : loading ? "Saving..." : "Save"}
          </Button>
        </Stack>
      </DialogActions>
    </Dialog>
  );
};

export default EventEditDialog;
