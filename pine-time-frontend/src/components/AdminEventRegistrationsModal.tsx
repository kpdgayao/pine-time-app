import React, { useState } from "react";
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress';
import { useTheme } from '@mui/material/styles';
import { useAdminEventRegistrations } from "../hooks/useAdminEventRegistrations";

interface Props {
  eventId: number | undefined;
  open: boolean;
  onClose: () => void;
}

const PAGE_SIZE = 10;

const AdminEventRegistrationsModal: React.FC<Props> = ({ eventId, open, onClose }) => {
  const theme = useTheme();
  const [page, setPage] = useState(1);
  const { items, total, approved, attendance_rate, revenue, loading, error, refetch } = useAdminEventRegistrations(eventId, page, PAGE_SIZE);

  const totalPages = total ? Math.ceil(total / PAGE_SIZE) : 1;

  if (!open) return null;

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        bgcolor: theme.palette.action.disabledBackground,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
    >
      <Box
        sx={{
          bgcolor: theme.palette.background.paper,
          borderRadius: 2,
          maxWidth: 800,
          width: '90vw',
          p: 4,
          boxShadow: theme.shadows[2],
        }}
      >
        <Typography variant="h5" mb={2}>Event Registrations</Typography>
        <Box sx={{ display: 'flex', gap: 4, mb: 2 }}>
          <Typography><b>Total Registrations:</b> {total ?? 0}</Typography>
          <Typography><b>Approved:</b> {approved ?? 0}</Typography>
          <Typography><b>Attendance Rate:</b> {attendance_rate ?? 0}%</Typography>
          <Typography><b>Revenue:</b> ₱{revenue?.toLocaleString() ?? 0}</Typography>
        </Box>
        {loading && (
          <Box sx={{ textAlign: 'center', my: 4 }}><CircularProgress /></Box>
        )}
        {error && (
          <Typography sx={{ color: theme.palette.error.main, mb: 2 }}>{error}</Typography>
        )}
        {!loading && !error && (
          <>
            <TableContainer component={Paper} sx={{ mb: 2 }}>
              <Table>
                <TableHead>
                  <TableRow sx={{ background: theme.palette.grey[100] }}>
                    <TableCell>ID</TableCell>
                    <TableCell>User</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Payment</TableCell>
                    <TableCell>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {items && items.length > 0 ? (
                    items.map((reg) => (
                      <TableRow key={reg.id}>
                        <TableCell>{reg.id}</TableCell>
                        <TableCell>{reg.user?.full_name || reg.user_id}</TableCell>
                        <TableCell>{reg.status}</TableCell>
                        <TableCell>{reg.payment_status}</TableCell>
                        <TableCell>{new Date(reg.registration_date).toLocaleString()}</TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        No registrations found.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, justifyContent: 'center', mb: 2 }}>
              <Button variant="outlined" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>Prev</Button>
              <Typography>Page {page} of {totalPages}</Typography>
              <Button variant="outlined" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</Button>
            </Box>
          </>
        )}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <Button variant="contained" onClick={refetch}>Refresh</Button>
          <Button variant="contained" color="secondary" onClick={onClose}>Close</Button>
        </Box>
      </Box>
    </Box>
  );
};

export default AdminEventRegistrationsModal;

