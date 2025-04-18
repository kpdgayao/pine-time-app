import React, { useEffect, useState } from "react";
import axios from "axios";

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

const EventRegistrationsDialog: React.FC<Props> = ({ eventId, open, onClose }) => {
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const token = localStorage.getItem("admin_token");

  useEffect(() => {
    if (!open || !eventId) return;
    setLoading(true);
    setError(null);
    axios
      .get(`${API_BASE}/events/${eventId}/registrations`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setRegistrations(res.data))
      .catch((err) => setError(err?.response?.data?.detail || "Failed to fetch registrations."))
      .finally(() => setLoading(false));
  }, [eventId, open]);

  if (!open) return null;

  return (
    <div style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.3)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: "white", padding: 24, borderRadius: 8, minWidth: 400, maxWidth: 600, maxHeight: 600, overflow: "auto" }}>
        <h3>Event Registrations</h3>
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
            </tr>
          </thead>
          <tbody>
            {registrations.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: "center", color: "#999" }}>No registrations found.</td></tr>
            )}
            {registrations.map((reg) => (
              <tr key={reg.id} style={{ borderBottom: "1px solid #ccc" }}>
                <td>{reg.id}</td>
                <td>{reg.user ? `${reg.user.full_name} (${reg.user.email})` : reg.user_id}</td>
                <td>{reg.status}</td>
                <td>{reg.payment_status}</td>
                <td>{new Date(reg.registration_date).toLocaleString()}</td>
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
