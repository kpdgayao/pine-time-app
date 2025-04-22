import React, { useEffect, useState } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Typography, Stack, CircularProgress, Alert } from '@mui/material';
import PineTimeButton from './PineTimeButton';
import api from "../api/client";

interface PaymentReviewDialogProps {
  registrationId: number | null;
  open: boolean;
  onClose: () => void;
  onAction: (action: "approved" | "rejected") => void;
}

interface PaymentDetails {
  payment_id: number;
  registration_id: number;
  user_id: number;
  event_id: number;
  amount_paid: number;
  payment_channel: string;
  payment_reference?: string;
  payment_date: string;
}

const PaymentReviewDialog: React.FC<PaymentReviewDialogProps> = ({ registrationId, open, onClose, onAction }) => {
  const [loading, setLoading] = useState(false);
  const [payment, setPayment] = useState<PaymentDetails | null>(null);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState("");

  useEffect(() => {
    if (!open || !registrationId) return;
    setLoading(true);
    setError("");
    api.get(`/payments/payments/by_registration/${registrationId}`)
      .then(res => setPayment(res.data))
      .catch((err) => {
        if (err.response && err.response.status === 404) {
          setError("No payment found for this registration yet.");
        } else {
          setError("Failed to fetch payment details.");
        }
      })
      .finally(() => setLoading(false));
  }, [open, registrationId]);

  const handleApprove = async () => {
    if (!payment) return;
    setActionLoading(true);
    setActionMsg("");
    try {
      await api.post(`/registrations/${registrationId}/approve`);
      setActionMsg("Registration approved.");
      onAction("approved");
    } catch {
      setActionMsg("Failed to approve registration.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!payment) return;
    setActionLoading(true);
    setActionMsg("");
    try {
      await api.post(`/registrations/${registrationId}/reject`);
      setActionMsg("Registration rejected.");
      onAction("rejected");
    } catch {
      setActionMsg("Failed to reject registration.");
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Review Payment</DialogTitle>
      <DialogContent>
        {loading ? (
          <CircularProgress />
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : payment ? (
          <Stack spacing={1}>
            <Typography><b>Amount Paid:</b> ₱{payment.amount_paid.toFixed(2)}</Typography>
            <Typography><b>Channel:</b> {payment.payment_channel}</Typography>
            {payment.payment_reference && (
              <Typography><b>Reference:</b> {payment.payment_reference}</Typography>
            )}
            <Typography><b>Date:</b> {new Date(payment.payment_date).toLocaleString()}</Typography>
          </Stack>
        ) : (
          <Typography>No payment details found.</Typography>
        )}
        {actionMsg && <Alert severity={actionMsg.includes('approved') ? 'success' : 'error'} sx={{ mt: 2 }}>{actionMsg}</Alert>}
      </DialogContent>
      <DialogActions>
        <PineTimeButton onClick={onClose} disabled={actionLoading}>Close</PineTimeButton>
        <PineTimeButton onClick={handleReject} color="error" variant="contained" disabled={actionLoading || !payment}>Reject</PineTimeButton>
        <PineTimeButton onClick={handleApprove} color="success" variant="contained" disabled={actionLoading || !payment}>Approve</PineTimeButton>
      </DialogActions>
    </Dialog>
  );
};

export default PaymentReviewDialog;
