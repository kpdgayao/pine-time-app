import React, { useEffect, useState } from "react";
import api from "../api/client";
import { exportToCsv } from "./exportToCsv";

interface Transaction {
  id: number;
  user_id: number;
  user_email?: string;
  user_name?: string;
  type: string;
  points: number;
  description: string;
  event_id?: number;
  event_title?: string;
  admin_id?: number;
  admin_email?: string;
  transaction_date: string;
}

import { useTheme } from '@mui/material/styles';

const AdminPointsTransactionsTable: React.FC = () => {
  const theme = useTheme();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchTransactions();
    // eslint-disable-next-line
  }, []);

  const fetchTransactions = () => {
    setLoading(true);
    setError(null);
    api.get("/admin/points/transactions")
      .then(res => {
        setTransactions(res.data || []);
      })
      .catch(err => setError(err?.response?.data?.detail || "Failed to fetch transactions."))
      .finally(() => setLoading(false));
  };

  const filtered = transactions.filter(t => {
    const matchesSearch =
      (t.user_email?.toLowerCase().includes(search.toLowerCase()) || "") ||
      (t.user_name?.toLowerCase().includes(search.toLowerCase()) || "") ||
      (t.description?.toLowerCase().includes(search.toLowerCase()) || "");
    const matchesType = typeFilter ? t.type === typeFilter : true;
    return matchesSearch && matchesType;
  });

  const handleExport = () => {
    setExporting(true);
    const rows = filtered.map((t) => ({
      ID: t.id,
      User: t.user_name || t.user_id,
      Email: t.user_email || "",
      Type: t.type,
      Points: t.points,
      Description: t.description,
      Event: t.event_title || t.event_id || "",
      Admin: t.admin_email || t.admin_id || "",
      Date: t.transaction_date,
    }));
    exportToCsv("points_transactions.csv", rows);
    setExporting(false);
  };

  return (
    <div style={{ marginBottom: 32 }}>
      <h3>Points Transactions</h3>
      <div style={{ display: "flex", gap: 16, marginBottom: 8 }}>
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search by user, email, or description"
          style={{ padding: 4, width: 240 }}
        />
        <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          <option value="">All Types</option>
          <option value="earned">Earned</option>
          <option value="redeemed">Redeemed</option>
          <option value="awarded">Awarded</option>
        </select>
        <button onClick={handleExport} disabled={exporting || filtered.length === 0}>
          {exporting ? "Exporting..." : "Export CSV"}
        </button>
        <button onClick={fetchTransactions} disabled={loading}>
          Refresh
        </button>
      </div>
      {loading && <div>Loading transactions...</div>}
      {error && <div style={{ color: theme.palette.error.main }}>{error}</div>}
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: theme.palette.grey[300] }}>
            <th>ID</th>
            <th>User</th>
            <th>Email</th>
            <th>Type</th>
            <th>Points</th>
            <th>Description</th>
            <th>Event</th>
            <th>Admin</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 ? (
            <tr><td colSpan={9} style={{ textAlign: "center" }}>No transactions found.</td></tr>
          ) : (
            filtered.map((t) => (
              <tr key={t.id} style={{ borderBottom: `1px solid ${theme.palette.divider}` }}>
                <td>{t.id}</td>
                <td>{t.user_name || t.user_id}</td>
                <td>{t.user_email || ""}</td>
                <td>{t.type}</td>
                <td>{t.points}</td>
                <td>{t.description}</td>
                <td>{t.event_title || t.event_id || ""}</td>
                <td>{t.admin_email || t.admin_id || ""}</td>
                <td>{new Date(t.transaction_date).toLocaleString()}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default AdminPointsTransactionsTable;
