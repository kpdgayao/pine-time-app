import React, { useState } from "react";
import api from "../api/client";

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

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

const UserEditDialog: React.FC<Props> = ({ user, open, onClose, onSave }) => {
  const [form, setForm] = useState({
    full_name: user?.full_name || "",
    email: user?.email || "",
    user_type: user?.user_type || "user",
    is_active: user?.is_active ?? true,
    is_superuser: user?.is_superuser ?? false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    if (user) {
      setForm({
        full_name: user.full_name,
        email: user.email,
        user_type: user.user_type,
        is_active: user.is_active,
        is_superuser: user.is_superuser,
      });
    }
  }, [user]);

  const token = localStorage.getItem("admin_token");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const target = e.target as HTMLInputElement | HTMLSelectElement;
    const { name, value, type } = target;
    const checked = (target instanceof HTMLInputElement) ? target.checked : undefined;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.put(`${API_BASE}/users/${user.id}`, form, {
        headers: { Authorization: `Bearer ${token}` },
      });
      onSave(res.data);
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to update user.");
    } finally {
      setLoading(false);
    }
  };

  if (!open || !user) return null;

  return (
    <div style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.3)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <form onSubmit={handleSubmit} style={{ background: "white", padding: 24, borderRadius: 8, minWidth: 320 }}>
        <h3>Edit User</h3>
        <label>Full Name<br />
          <input name="full_name" value={form.full_name} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>Email<br />
          <input name="email" value={form.email} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>User Type<br />
          <select name="user_type" value={form.user_type} onChange={handleChange} style={{ width: "100%" }}>
            <option value="user">User</option>
            <option value="admin">Admin</option>
            <option value="business">Business</option>
          </select>
        </label><br /><br />
        <label>
          <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} /> Active
        </label>
        <label style={{ marginLeft: 16 }}>
          <input type="checkbox" name="is_superuser" checked={form.is_superuser} onChange={handleChange} /> Superuser
        </label><br /><br />
        {error && <div style={{ color: "red" }}>{error}</div>}
        <button type="submit" disabled={loading} style={{ marginRight: 8 }}>Save</button>
        <button type="button" onClick={onClose} disabled={loading}>Cancel</button>
      </form>
    </div>
  );
};

export default UserEditDialog;
