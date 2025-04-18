import React, { useEffect, useState } from "react";
import api from "../api/client";
import { exportToCsv } from "./exportToCsv";

interface HistoryEntry {
  id: number;
  user_id: number;
  type: "award" | "redeem" | "badge_assign" | "badge_revoke";
  points?: number;
  badge_name?: string;
  timestamp: string;
  admin_name?: string;
}

interface Props {
  userId: number | null;
  open: boolean;
  onClose: () => void;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

const PointsBadgesHistoryDialog: React.FC<Props> = ({ userId, open, onClose }) => {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [exporting, setExporting] = useState(false);
  const token = localStorage.getItem("admin_token");

  useEffect(() => {
    if (!open || !userId) return;
    setLoading(true);
    setError(null);
    api.get(`${API_BASE}/users/${userId}/points_badges_history`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setHistory(res.data))
      .catch(err => setError(err?.response?.data?.detail || "Failed to fetch history."))
      .finally(() => setLoading(false));
  }, [userId, open]);

  const filtered = history.filter(entry =>
    entry.type.toLowerCase().includes(search.toLowerCase()) ||
    (entry.admin_name || "").toLowerCase().includes(search.toLowerCase()) ||
    (entry.badge_name || "").toLowerCase().includes(search.toLowerCase())
  );

  const handleExport = () => {
    setExporting(true);
    const rows = filtered.map(entry => ({
      Time: new Date(entry.timestamp).toLocaleString(),
      Type: entry.type,
      Points: entry.points ?? "-",
      Badge: entry.badge_name ?? "-",
      Admin: entry.admin_name ?? "-",
    }));
    exportToCsv("points_badges_history.csv", rows);
    setExporting(false);
  };

  if (!open) return null;

  return (
    <div style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.3)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: "white", padding: 24, borderRadius: 8, minWidth: 400, maxWidth: 700, maxHeight: 600, overflow: "auto" }}>
        <h3>Points & Badges History</h3>
        <div style={{ display: "flex", gap: 16, marginBottom: 8 }}>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by type, admin, badge"
            style={{ padding: 4, width: 220 }}
          />
          <button onClick={handleExport} disabled={exporting || filtered.length === 0}>
            {exporting ? "Exporting..." : "Export CSV"}
          </button>
        </div>
        {loading && <div>Loading...</div>}
        {error && <div style={{ color: "red" }}>{error}</div>}
        <table style={{ width: "100%", marginTop: 8, borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#e0e0e0" }}>
              <th>Time</th>
              <th>Type</th>
              <th>Points</th>
              <th>Badge</th>
              <th>Admin</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: "center", color: "#999" }}>No history found.</td></tr>
            )}
            {filtered.map(entry => (
              <tr key={entry.id} style={{ borderBottom: "1px solid #ccc" }}>
                <td>{new Date(entry.timestamp).toLocaleString()}</td>
                <td>{entry.type.replace("_", " ")}</td>
                <td>{entry.points ?? "-"}</td>
                <td>{entry.badge_name ?? "-"}</td>
                <td>{entry.admin_name ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div style={{ marginTop: 16, textAlign: "right" }}>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default PointsBadgesHistoryDialog;
