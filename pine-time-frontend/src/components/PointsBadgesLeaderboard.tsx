import React, { useEffect, useState } from "react";
import api from "../api/client";
import { exportToCsv } from "./exportToCsv";
import PointsBadgesDistributionChart from "./PointsBadgesDistributionChart";

interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  points: number;
  badges: number;
}


const PointsBadgesLeaderboard: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.get('/points/leaderboard')
      .then(res => {
        // Support both array and object (paginated) formats
        if (Array.isArray(res.data)) {
          setUsers(res.data);
        } else if (res.data && Array.isArray(res.data.items)) {
          setUsers(res.data.items);
        } else {
          setUsers([]); // fallback
        }
      })
      .catch(err => setError(err?.response?.data?.detail || "Failed to fetch leaderboard."))
      .finally(() => setLoading(false));
  }, []);

  const filtered = users.filter(u =>
    (u.full_name || u.username).toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  const handleExport = () => {
    setExporting(true);
    const rows = filtered.map((u, i) => ({
      Rank: i + 1,
      Name: u.full_name || u.username,
      Email: u.email,
      Points: u.points,
      Badges: u.badges,
    }));
    exportToCsv("leaderboard.csv", rows);
    setExporting(false);
  };

  return (
    <div style={{ marginBottom: 32 }}>
      <h3>Points & Badges Leaderboard</h3>
      <div style={{ display: "flex", gap: 16, marginBottom: 8 }}>
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search by name or email"
          style={{ padding: 4, width: 220 }}
        />
        <button onClick={handleExport} disabled={exporting || filtered.length === 0}>
          {exporting ? "Exporting..." : "Export CSV"}
        </button>
      </div>
      {loading && <div>Loading leaderboard...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#e0e0e0" }}>
            <th>Rank</th>
            <th>User</th>
            <th>Points</th>
            <th>Badges</th>
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 && (
            <tr><td colSpan={4} style={{ textAlign: "center", color: "#999" }}>No data.</td></tr>
          )}
          {filtered.map((u, i) => (
            <tr key={u.id ?? `row-${i}`} style={{ borderBottom: "1px solid #ccc" }}>
              <td>{i + 1}</td>
              <td>{u.full_name || u.username} ({u.email})</td>
              <td>{u.points}</td>
              <td>{u.badges}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {filtered.length > 0 && (
        <PointsBadgesDistributionChart leaderboard={filtered.map(u => ({ points: u.points, badges: u.badges }))} />
      )}
    </div>
  );
};

export default PointsBadgesLeaderboard;
