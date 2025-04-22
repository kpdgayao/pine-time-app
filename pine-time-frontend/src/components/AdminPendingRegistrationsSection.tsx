import React, { useEffect, useState } from "react";
import api from "../api/client";
import PaymentReviewDialog from "./PaymentReviewDialog";
import {
  Table, TableHead, TableRow, TableCell, TableBody,
  CircularProgress, Alert, Typography, Snackbar, Stack, Tooltip
} from "@mui/material";
import PineTimeButton from './PineTimeButton';
import PineTimeCard from './PineTimeCard';
import { useTheme } from '@mui/material/styles';

interface Registration {
  id: number;
  user_id: number;
  event_id: number;
  registration_date: string;
  status: string;
  payment_status: string;
  user?: {
    full_name?: string;
    username?: string;
    email?: string;
  };
  event?: {
    title?: string;
    location?: string;
  };
}

const AdminPendingRegistrationsSection: React.FC = () => {
  const theme = useTheme();
  // All hooks must be declared before any conditional return
  
  const [pending, setPending] = useState<Registration[]>([]);
const [loading, setLoading] = useState(false);
const [actionLoading, setActionLoading] = useState<number | null>(null);
const [statusFilter, setStatusFilter] = useState<string>('All');
const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({ open: false, message: '', severity: 'success' });
const [reviewDialogOpen, setReviewDialogOpen] = useState(false);
const [reviewRegistrationId, setReviewRegistrationId] = useState<number | null>(null);
  
  
  
  
  
  const token = localStorage.getItem("admin_token");

  // Fetch all registrations, not just pending
  const fetchAll = async () => {
    setLoading(true);
    try {
      const res = await api.get("/registrations", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPending(Array.isArray(res.data) ? res.data : []);
    } catch (err: any) {
      setSnackbar({ open: true, message: "Failed to fetch registrations", severity: "error" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    // eslint-disable-next-line
  }, []);

  // Removed fetchPending; now using fetchAll above

  // All hooks declared above; safe to use conditional returns now
  if (loading) return <PineTimeCard sx={{ p: 2 }}><CircularProgress /></PineTimeCard>;

  // Approve handler
  const handleApprove = async (id: number) => {
    setActionLoading(id);
    try {
      await api.post(`/registrations/${id}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSnackbar({ open: true, message: 'Registration approved.', severity: 'success' });
      fetchAll();
    } catch (err: any) {
      setSnackbar({ open: true, message: 'Failed to approve registration.', severity: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  // Unregister handler for admin (if applicable)
  

  // Reject handler
  const handleReject = async (id: number) => {
    setActionLoading(id);
    try {
      await api.post(`/registrations/${id}/reject`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSnackbar({ open: true, message: 'Registration rejected.', severity: 'success' });
      fetchAll();
    } catch (err: any) {
      setSnackbar({ open: true, message: 'Failed to reject registration.', severity: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  // Review dialog open
  const handleOpenReviewDialog = (registrationId: number) => {
    setReviewRegistrationId(registrationId);
    setReviewDialogOpen(true);
  };

  // Review dialog close
  const handleCloseReviewDialog = () => {
    setReviewDialogOpen(false);
    setReviewRegistrationId(null);
  };

  // Payment action handler
  const handlePaymentAction = (action: "approved" | "rejected") => {
    setReviewDialogOpen(false);
    setReviewRegistrationId(null);
    fetchAll();
    setSnackbar({ open: true, message: `Payment ${action}.`, severity: action === 'approved' ? 'success' : 'error' });
  };

  // Sort and filter logic
  const sorted = [...pending].sort((a, b) => new Date(b.registration_date).getTime() - new Date(a.registration_date).getTime());
  const filtered = statusFilter === 'All' ? sorted : sorted.filter(reg => reg.status === statusFilter.toLowerCase());

  return (
    <PineTimeCard sx={{ p: 2 }}>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
      <Typography variant="h6" mb={2}>Pending Event Registrations</Typography>
      <Stack direction="row" alignItems="center" spacing={2} mb={2}>
        <label htmlFor="status-filter">Filter by status: </label>
        <select
          id="status-filter"
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          style={{ marginLeft: theme.spacing(1), padding: theme.spacing(0.5), borderRadius: 4 }}
        >
          <option value="All">All</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </Stack>
      <PaymentReviewDialog
        registrationId={reviewRegistrationId}
        open={reviewDialogOpen}
        onClose={handleCloseReviewDialog}
        onAction={handlePaymentAction}
      />
      {filtered.length === 0 ? (
        <Typography>No registrations found 🎉</Typography>
      ) : (
        <Table size="small">
          <TableHead>
  <TableRow>
    <TableCell>Event</TableCell>
    <TableCell>User</TableCell>
    <TableCell>Status</TableCell>
    <TableCell>Payment Status</TableCell>
    <TableCell>Registration Date</TableCell>
    <TableCell>Actions</TableCell>
  </TableRow>
</TableHead>
<TableBody>
  {filtered.map((reg: Registration) => (
    <TableRow key={reg.id}>
      <TableCell>
        {reg.event?.title || reg.event_id}
        <br />
        <span style={{ color: theme.palette.text.secondary, fontSize: 12 }}>{reg.event?.location}</span>
      </TableCell>
      <TableCell>
        {reg.user?.full_name || reg.user?.username || reg.user_id}
        <br />
        {reg.user?.email && <span style={{ color: theme.palette.text.secondary, fontSize: 12 }}>{reg.user.email}</span>}
      </TableCell>
      <TableCell>{reg.status}</TableCell>
      <TableCell>{reg.payment_status}</TableCell>
      <TableCell>{new Date(reg.registration_date).toLocaleString()}</TableCell>
      <TableCell>
        {reg.status === 'pending' && reg.payment_status === 'pending' ? (
          <PineTimeButton
            variantType="secondary"
            size="small"
            onClick={() => handleOpenReviewDialog(reg.id)}
            sx={{ minWidth: 120 }}
          >
            Review Payment
          </PineTimeButton>
        ) : reg.status === 'pending' ? (
          <Stack direction="row" spacing={1}>
            <Tooltip title="Approve registration">
              <PineTimeButton
                variantType="primary"
                color="success"
                size="small"
                disabled={actionLoading === reg.id}
                onClick={() => handleApprove(reg.id)}
                sx={{ minWidth: 90 }}
              >
                {actionLoading === reg.id ? <CircularProgress size={18} /> : "Approve"}
              </PineTimeButton>
            </Tooltip>
            <Tooltip title="Reject registration">
              <PineTimeButton
                variantType="primary"
                color="error"
                size="small"
                disabled={actionLoading === reg.id}
                onClick={() => handleReject(reg.id)}
                sx={{ minWidth: 90 }}
              >
                {actionLoading === reg.id ? <CircularProgress size={18} /> : "Reject"}
              </PineTimeButton>
            </Tooltip>
          </Stack>
        ) : null}
      </TableCell>
    </TableRow>
  ))}
          </TableBody>
        </Table>
      )}
    </PineTimeCard>
  );
}

export default AdminPendingRegistrationsSection;
