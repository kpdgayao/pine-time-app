import React, { useEffect, useState } from "react";
import axios from "axios";
import UserEditDialog from "./UserEditDialog";
import UserCreateDialog from "./UserCreateDialog";

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  user_type: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";
const PAGE_SIZE = 10;

const AdminUsersSection: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editUser, setEditUser] = useState<User | null>(null);
  const [editOpen, setEditOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  // TODO: Replace with secure token retrieval
  const token = localStorage.getItem("admin_token");

  const fetchUsers = async (searchVal = search, pageVal = page) => {
    setLoading(true);
    setError(null);
    try {
      const params: any = { skip: (pageVal - 1) * PAGE_SIZE, limit: PAGE_SIZE };
      if (searchVal) params.q = searchVal;
      const res = await axios.get(`${API_BASE}/users/`, {
        headers: { Authorization: `Bearer ${token}` },
        params,
      });
      setUsers(res.data);
      // For demo: assume backend returns total count in header or add logic here
      setTotal(res.data.length < PAGE_SIZE ? (pageVal - 1) * PAGE_SIZE + res.data.length : pageVal * PAGE_SIZE + 1);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail || "Failed to fetch users. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
    // eslint-disable-next-line
  }, [page]);

  const handleEdit = (user: User) => {
    setEditUser(user);
    setEditOpen(true);
  };
  const handleEditSave = (updated: User) => {
    setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
  };
  const handleDeactivate = async (user: User) => {
    if (!window.confirm(`Deactivate user ${user.username}?`)) return;
    setLoading(true);
    setError(null);
    try {
      const res = await axios.put(
        `${API_BASE}/users/${user.id}`,
        { ...user, is_active: false },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setUsers((prev) => prev.map((u) => (u.id === user.id ? res.data : u)));
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to deactivate user.");
    } finally {
      setLoading(false);
    }
  };
  const handleCreate = (user: User) => {
    setUsers((prev) => [user, ...prev]);
    setPage(1); // Show new user on first page
  };
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchUsers(search, 1);
  };
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    fetchUsers(search, newPage);
  };

  // Filter users client-side if backend search not implemented
  const filteredUsers = users.filter(
    (u) =>
      u.username.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase()) ||
      u.full_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <h2>User Management</h2>
      <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
        <form onSubmit={handleSearch} style={{ flex: 1 }}>
          <input
            placeholder="Search by username, email, or name"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ padding: 8, width: 260, marginRight: 8 }}
          />
          <button type="submit" style={{ padding: "8px 16px" }}>Search</button>
        </form>
        <button onClick={() => setCreateOpen(true)} style={{ marginLeft: 16, padding: "8px 16px", background: "#2E7D32", color: "white", border: "none", borderRadius: 4 }}>
          + Create User
        </button>
      </div>
      {loading && <div>Loading users...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
      <table style={{ width: "100%", marginTop: 8, borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#e0e0e0" }}>
            <th>ID</th>
            <th>Email</th>
            <th>Username</th>
            <th>Full Name</th>
            <th>Type</th>
            <th>Active</th>
            <th>Superuser</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredUsers.length === 0 && (
            <tr><td colSpan={8} style={{ textAlign: "center", color: "#999" }}>No users found.</td></tr>
          )}
          {filteredUsers.map((user) => (
            <tr key={user.id} style={{ borderBottom: "1px solid #ccc" }}>
              <td>{user.id}</td>
              <td>{user.email}</td>
              <td>{user.username}</td>
              <td>{user.full_name}</td>
              <td>{user.user_type}</td>
              <td>{user.is_active ? "Yes" : "No"}</td>
              <td>{user.is_superuser ? "Yes" : "No"}</td>
              <td>
                <button style={{ marginRight: 8 }} onClick={() => handleEdit(user)}>Edit</button>
                <button onClick={() => handleDeactivate(user)} disabled={!user.is_active} style={{ color: user.is_active ? "#c62828" : "#aaa" }}>Deactivate</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {/* Pagination */}
      <div style={{ marginTop: 16, display: "flex", justifyContent: "center" }}>
        <button onClick={() => handlePageChange(page - 1)} disabled={page === 1} style={{ marginRight: 8 }}>Prev</button>
        <span>Page {page}</span>
        <button onClick={() => handlePageChange(page + 1)} disabled={filteredUsers.length < PAGE_SIZE} style={{ marginLeft: 8 }}>Next</button>
      </div>
      {/* Dialogs */}
      <UserEditDialog
        user={editUser}
        open={editOpen}
        onClose={() => setEditOpen(false)}
        onSave={handleEditSave}
      />
      <UserCreateDialog
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreate={handleCreate}
      />
    </div>
  );
};

export default AdminUsersSection;
