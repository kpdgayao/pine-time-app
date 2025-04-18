import React, { useState } from "react";
import axios from "axios";

interface Props {
  open: boolean;
  onClose: () => void;
  onCreate: (user: any) => void;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

const UserCreateDialog: React.FC<Props> = ({ open, onClose, onCreate }) => {
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API_BASE}/users/`, form, {
        headers: { Authorization: `Bearer ${token}` },
      });
      onCreate(res.data);
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to create user.");
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.3)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <form onSubmit={handleSubmit} style={{ background: "white", padding: 24, borderRadius: 8, minWidth: 320 }}>
        <h3>Create New User</h3>
        <label>Full Name<br />
          <input name="full_name" value={form.full_name} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>Email<br />
          <input name="email" value={form.email} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>Username<br />
          <input name="username" value={form.username} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>Password<br />
          <input name="password" type="password" value={form.password} onChange={handleChange} required style={{ width: "100%" }} />
        </label><br /><br />
        <label>User Type<br />
          <select name="user_type" value={form.user_type} onChange={handleChange} style={{ width: "100%" }}>
            <option value="user">User</option>
            <option value="admin">Admin</option>
            <option value="business">Business</option>
          </select>
        </label><br /><br />
        <label>
          <input type="checkbox" name="is_superuser" checked={form.is_superuser} onChange={handleChange} /> Superuser
        </label><br /><br />
        {error && <div style={{ color: "red" }}>{error}</div>}
        <button type="submit" disabled={loading} style={{ marginRight: 8 }}>Create</button>
        <button type="button" onClick={onClose} disabled={loading}>Cancel</button>
      </form>
    </div>
  );
};

export default UserCreateDialog;
