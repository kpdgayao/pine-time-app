import React, { useEffect, useState } from "react";
import api from "../api/client";
import { exportToCsv } from "./exportToCsv";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Button,
  Stack,
  Alert,
  Typography,
  CircularProgress
} from "@mui/material";

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
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Event Registrations</DialogTitle>
      <DialogContent sx={{ minWidth: 400, maxWidth: 700, maxHeight: 600 }}>
        <Stack direction="row" spacing={4} sx={{ mb: 2 }}>
          <Typography variant="body2"><strong>Total Registrations:</strong> {registrationCount}</Typography>
          <Typography variant="body2"><strong>Approved:</strong> {approvedCount}</Typography>
          <Typography variant="body2"><strong>Attendance Rate:</strong> {attendanceRate}%</Typography>
          <Typography variant="body2"><strong>Revenue:</strong> {totalRevenue}</Typography>
        </Stack>
        <Stack direction="row" justifyContent="flex-end" sx={{ mb: 2 }}>
          <Button onClick={handleExport} disabled={exporting || registrations.length === 0} variant="outlined">
            {exporting ? "Exporting..." : "Export CSV"}
          </Button>
        </Stack>
        {loading && (
          <Stack alignItems="center" sx={{ my: 3 }}>
            <CircularProgress size={32} />
            <Typography variant="body2" sx={{ mt: 1 }}>Loading registrations...</Typography>
          </Stack>
        )}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
        )}
        <Table size="small" sx={{ mt: 1 }}>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>User</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Payment</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {registrations.length === 0 && !loading && (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ color: '#999' }}>
                  No registrations found.
                </TableCell>
              </TableRow>
            )}
            {registrations.map((reg) => (
              <TableRow key={reg.id}>
                <TableCell>{reg.id}</TableCell>
                <TableCell>{reg.user ? `${reg.user.full_name} (${reg.user.email})` : reg.user_id}</TableCell>
                <TableCell>{reg.status}</TableCell>
                <TableCell>{reg.payment_status}</TableCell>
                <TableCell>{new Date(reg.registration_date).toLocaleString()}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1}>
                    {statusActions.map((action) => (
                      <Button
                        key={action.next}
                        size="small"
                        variant="contained"
                        color={action.next === "approved" ? "success" : action.next === "rejected" ? "error" : "warning"}
                        disabled={actionLoading === reg.id || reg.status === action.next}
                        onClick={() => handleStatusChange(reg.id, action.next)}
                        sx={{ minWidth: 0, px: 1, fontSize: 13 }}
                      >
                        {action.label}
                      </Button>
                    ))}
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DialogContent>
      <DialogActions sx={{ justifyContent: "flex-end" }}>
        <Button onClick={onClose} variant="outlined">Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default EventRegistrationsDialog;
