import React, { useState } from "react";
import api from "../api/client";
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Select, MenuItem, FormControlLabel, Checkbox, Alert, Stack
} from "@mui/material";
import PineTimeTextField from './PineTimeTextField';
import PineTimeButton from './PineTimeButton';
import { SelectChangeEvent } from "@mui/material/Select";
// Removed custom CSS; all styling is now via MUI theme and components.

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  user_type: string;
}

interface Props {
  user: User | null;
  open: boolean;
  onClose: () => void;
  onSave: (updated: User) => void;
}


const UserEditDialog: React.FC<Props> = ({ user, open, onClose, onSave }) => {
  // Handler functions for correct event typing
  function handleInputChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  }
  function handleSelectChange(e: SelectChangeEvent) {
    const name = e.target.name as string;
    setForm(prev => ({ ...prev, [name]: e.target.value }));
  }
  function handleCheckboxChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, checked } = e.target;
    setForm(prev => ({ ...prev, [name]: checked }));
  }

  const [form, setForm] = useState({
    full_name: user?.full_name || "",
    email: user?.email || "",
    username: user?.username || "",
    user_type: user?.user_type || "regular",
    is_active: user?.is_active ?? true,
    is_superuser: user?.is_superuser ?? false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    if (user) {
      setForm({
        full_name: user.full_name ?? "",
        email: user.email ?? "",
        username: user.username ?? "",
        user_type: user.user_type ?? "regular",
        is_active: user.is_active ?? true,
        is_superuser: user.is_superuser ?? false,
      });
    }
  }, [user]);

  const token = localStorage.getItem("admin_token");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      // Role and superuser status are now updated as part of the main user update
      // No need for a separate API call
      // Status is now updated as part of the main user update
      // No need for a separate API call
      // PUT profile fields if changed
      if (
        form.full_name !== user.full_name ||
        form.email !== user.email ||
        form.username !== user.username
      ) {
        await api.put(`/users/${user.id}`,
          {
            full_name: form.full_name,
            email: form.email,
            username: form.username,
            is_active: form.is_active,
            user_type: form.user_type,
            is_superuser: form.is_superuser,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
      }
      onSave({ ...user, ...form });
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to update user.");
    } finally {
      setLoading(false);
    }
  };


  if (!open || !user) return null;

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Edit User</DialogTitle>
      <DialogContent>
        <Stack spacing={2}>
          <PineTimeTextField
            label="Full Name"
            name="full_name"
            value={form.full_name}
            onChange={handleInputChange}
            fullWidth
            required
            disabled={loading}
            variant="outlined"
          />
          <PineTimeTextField
            label="Email"
            name="email"
            value={form.email}
            onChange={handleInputChange}
            fullWidth
            required
            disabled={loading}
            variant="outlined"
            type="email"
          />
          <PineTimeTextField
            label="Username"
            name="username"
            value={form.username}
            onChange={handleInputChange}
            fullWidth
            required
            disabled={loading}
            variant="outlined"
          />
          <Select
            label="User Type"
            name="user_type"
            value={form.user_type}
            onChange={handleSelectChange}
            fullWidth
            disabled={loading}
            variant="outlined"
          >
            <MenuItem value="regular">Regular</MenuItem>
            <MenuItem value="business">Business</MenuItem>
            <MenuItem value="admin">Admin</MenuItem>
          </Select>
          <FormControlLabel
            control={
              <Checkbox
                name="is_active"
                checked={form.is_active}
                onChange={handleCheckboxChange}
                disabled={loading}
              />
            }
            label="Active"
          />
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
          <PineTimeButton type="button" onClick={onClose} disabled={loading} variant="outlined">Cancel</PineTimeButton>
          <PineTimeButton type="button" onClick={handleSubmit} disabled={loading} variant="contained" color="primary">
            {loading ? "Saving..." : "Save"}
          </PineTimeButton>
        </Stack>
      </DialogActions>
    </Dialog>
  );
};


export default UserEditDialog;
