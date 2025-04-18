import React, { useEffect, useState } from "react";
import api from "../api/client";
import { exportToCsv } from "./exportToCsv";

interface Registration {
  id: number;
  user_id: number;
  event_id: number;
  registration_date: string;
  status: string;
  payment_status: string;
  user?: { id: number; username: string; email: string; full_name: string };
}

interface Props {
  eventId: number | null;
  open: boolean;
  onClose: () => void;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

const statusActions = [
  { label: "Approve", next: "approved" },
  { label: "Reject", next: "rejected" },
  { label: "Cancel", next: "cancelled" },
];

const EventRegistrationsDialog: React.FC<Props> = ({ eventId, open, onClose }) => {
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [exporting, setExporting] = useState(false);

  const token = localStorage.getItem("admin_token");

  const fetchRegistrations = () => {
    if (!open || !eventId) return;
    setLoading(true);
    setError(null);
    api
      .get(`${API_BASE}/events/${eventId}/registrations`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setRegistrations(res.data))
      .catch((err) => setError(err?.response?.data?.detail || "Failed to fetch registrations."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchRegistrations();
    // eslint-disable-next-line
  }, [eventId, open]);

  const handleStatusChange = (regId: number, nextStatus: string) => {
    setActionLoading(regId);
    api
      .patch(
        `${API_BASE}/registrations/${regId}`,
        { status: nextStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      .then(() => fetchRegistrations())
      .catch((err) => setError(err?.response?.data?.detail || "Failed to update registration."))
      .finally(() => setActionLoading(null));
  };

  const handleExport = () => {
    setExporting(true);
    const rows = registrations.map((reg) => ({
      ID: reg.id,
      User: reg.user ? reg.user.full_name : reg.user_id,
      Email: reg.user?.email || "",
      Status: reg.status,
      Payment: reg.payment_status,
      Date: reg.registration_date,
    }));
    exportToCsv("registrations.csv", rows);
    setExporting(false);
  };

  // Analytics
  const registrationCount = registrations.length;
  const approvedCount = registrations.filter((r) => r.status === "approved").length;
  const attendanceRate = registrationCount ? Math.round((approvedCount / registrationCount) * 100) : 0;
  const totalRevenue = registrations.reduce((sum, r) => sum + (r.payment_status === "paid" ? 1 : 0), 0); // Replace with actual amount if available

  if (!open) return null;

  return (
    <div style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.3)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: "white", padding: 24, borderRadius: 8, minWidth: 400, maxWidth: 700, maxHeight: 600, overflow: "auto" }}>
        <h3>Event Registrations</h3>
        <div style={{ marginBottom: 12, display: "flex", gap: 32 }}>
          <div><strong>Total Registrations:</strong> {registrationCount}</div>
          <div><strong>Approved:</strong> {approvedCount}</div>
          <div><strong>Attendance Rate:</strong> {attendanceRate}%</div>
          <div><strong>Revenue:</strong> {totalRevenue}</div>
        </div>
        <div style={{ marginBottom: 12, textAlign: "right" }}>
          <button onClick={handleExport} disabled={exporting || registrations.length === 0}>
            {exporting ? "Exporting..." : "Export CSV"}
          </button>
        </div>
        {loading && <div>Loading registrations...</div>}
        {error && <div style={{ color: "red" }}>{error}</div>}
        <table style={{ width: "100%", marginTop: 8, borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#e0e0e0" }}>
              <th>ID</th>
              <th>User</th>
              <th>Status</th>
              <th>Payment</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {registrations.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: "center", color: "#999" }}>No registrations found.</td></tr>
            )}
            {registrations.map((reg) => (
              <tr key={reg.id} style={{ borderBottom: "1px solid #ccc" }}>
                <td>{reg.id}</td>
                <td>{reg.user ? `${reg.user.full_name} (${reg.user.email})` : reg.user_id}</td>
                <td>{reg.status}</td>
                <td>{reg.payment_status}</td>
                <td>{new Date(reg.registration_date).toLocaleString()}</td>
                <td>
                  {statusActions.map((action) => (
                    <button
                      key={action.next}
                      style={{ marginRight: 6, padding: "2px 8px", fontSize: 13 }}
                      disabled={actionLoading === reg.id || reg.status === action.next}
                      onClick={() => handleStatusChange(reg.id, action.next)}
                    >
                      {action.label}
                    </button>
                  ))}
                </td>
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

export default EventRegistrationsDialog;
