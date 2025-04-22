import React, { useState } from "react";
import api from "../api/client";
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Select, MenuItem, FormControlLabel, Checkbox, Alert, Stack
} from "@mui/material";
import PineTimeTextField from './PineTimeTextField';
import PineTimeButton from './PineTimeButton';
import { SelectChangeEvent } from '@mui/material/Select';
// Removed FormDialog.css import; all styling is now via MUI theme and components.

interface Props {
  open: boolean;
  onClose: () => void;
  onCreate: (user: any) => void;
}

const UserCreateDialog: React.FC<Props> = ({ open, onClose, onCreate }) => {
  if (!open) return null;
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    username: "",
    password: "",
    user_type: "user",
    is_superuser: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const token = localStorage.getItem("admin_token");

  /**
 * Handles input changes for both text/select and checkbox inputs.
 * Ensures type safety for the 'checked' property.
 */
const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
  const { name, value } = e.target;
  setForm(prev => ({ ...prev, [name]: value }));
};

const handleSelectChange = (e: SelectChangeEvent) => {
  const name = e.target.name as string;
  setForm(prev => ({ ...prev, [name]: e.target.value }));
};

const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const { name, checked } = e.target;
  setForm(prev => ({ ...prev, [name]: checked }));
};

  /**
 * Handles form submission for user creation.
 * Uses the centralized API client and robust error handling.
 */
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setLoading(true);
  setError(null);
  try {
    const res = await api.post("/users/", form, {
      headers: { Authorization: `Bearer ${token}` },
    });
    onCreate(res.data);
    onClose();
  } catch (err: any) {
    if (err.response && err.response.data && err.response.data.detail) {
      setError(err.response.data.detail);
    } else if (err.message) {
      setError(err.message);
    } else {
      setError("Failed to create user.");
    }
  } finally {
    setLoading(false);
  }
};

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Create New User</DialogTitle>
      <DialogContent>
        <Stack spacing={2}>
          <PineTimeTextField
            autoFocus
            margin="dense"
            label="Full Name"
            name="full_name"
            value={form.full_name}
            onChange={handleInputChange}
            fullWidth
            required
          />
          <PineTimeTextField
            margin="dense"
            label="Email"
            name="email"
            value={form.email}
            onChange={handleInputChange}
            type="email"
            fullWidth
            required
          />
          <PineTimeTextField
            margin="dense"
            label="Username"
            name="username"
            value={form.username}
            onChange={handleInputChange}
            fullWidth
            required
          />
          <PineTimeTextField
            margin="dense"
            label="Password"
            name="password"
            value={form.password}
            onChange={handleInputChange}
            type="password"
            fullWidth
            required
          />
          <Select
            label="User Type"
            name="user_type"
            value={form.user_type}
            onChange={handleSelectChange}
            fullWidth
            disabled={loading}
          >
            <MenuItem value="user">User</MenuItem>
            <MenuItem value="admin">Admin</MenuItem>
          </Select>
          <FormControlLabel
            control={
              <Checkbox
                name="is_superuser"
                checked={form.is_superuser}
                onChange={handleCheckboxChange}
                disabled={loading}
              />
            }
            label="Superuser"
          />
        </Stack>
      </DialogContent>
      <DialogActions sx={{ flexDirection: 'column', alignItems: 'stretch', gap: 1, p: 2 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <Stack direction="row" spacing={2} justifyContent="flex-end">
          <PineTimeButton onClick={onClose} disabled={loading} variantType="text">
            Cancel
          </PineTimeButton>
          <PineTimeButton onClick={handleSubmit} disabled={loading} variantType="primary">
            {loading ? "Creating..." : "Create"}
          </PineTimeButton>
        </Stack>
      </DialogActions>
    </Dialog>
  );
};

export default UserCreateDialog;
