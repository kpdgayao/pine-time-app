import React, { useEffect, useState } from "react";
import api from "../api/client";
import BadgeTypeFormDialog, { BadgeTypeFormValues } from "./BadgeTypeFormDialog";
import {
  Table, TableHead, TableRow, TableCell, TableBody, Paper, Alert, CircularProgress, Button, IconButton, Snackbar, Stack, Dialog, DialogTitle, DialogActions, Typography, Box
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

interface BadgeType {
  id: number;
  name: string;
  description: string;
  level: string;
  criteria_type: string;
  criteria_threshold: number;
  event_type?: string;
  image_url?: string;
}

const AdminBadgesSection: React.FC = () => {
  const [badgeTypes, setBadgeTypes] = useState<BadgeType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editBadge, setEditBadge] = useState<BadgeType | null>(null);
  const [deleteBadge, setDeleteBadge] = useState<BadgeType | null>(null);
  const [snackbar, setSnackbar] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const fetchBadgeTypes = () => {
    setLoading(true);
    setError(null);
    api.get("/badges_admin/types/")
      .then(res => setBadgeTypes(res.data))
      .catch(err => setError(err?.response?.data?.detail || "Failed to fetch badge types."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchBadgeTypes();
  }, []);

  const handleCreate = () => {
    setEditBadge(null);
    setFormOpen(true);
  };

  const handleEdit = (badge: BadgeType) => {
    setEditBadge(badge);
    setFormOpen(true);
  };

  const handleDelete = (badge: BadgeType) => {
    setDeleteBadge(badge);
  };

  const handleFormSubmit = async (values: BadgeTypeFormValues) => {
    setSubmitting(true);
    try {
      if (editBadge) {
        // Edit existing
        await api.put(`/badges_admin/types/${editBadge.id}`, values);
        setSnackbar("Badge type updated.");
      } else {
        // Create new
        await api.post("/badges_admin/types/", values);
        setSnackbar("Badge type created.");
      }
      setFormOpen(false);
      fetchBadgeTypes();
    } catch (err: any) {
      setSnackbar(err?.response?.data?.detail || "Failed to save badge type.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteBadge) return;
    setSubmitting(true);
    try {
      await api.delete(`/badges_admin/types/${deleteBadge.id}`);
      setSnackbar("Badge type deleted.");
      setDeleteBadge(null);
      fetchBadgeTypes();
    } catch (err: any) {
      setSnackbar(err?.response?.data?.detail || "Failed to delete badge type.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }} elevation={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Badge Types</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreate}>
          Add Badge
        </Button>
      </Stack>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {loading ? (
        <Stack alignItems="center" py={4}><CircularProgress /></Stack>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Level</TableCell>
              <TableCell>Criteria Type</TableCell>
              <TableCell>Threshold</TableCell>
              <TableCell>Event Type</TableCell>
              <TableCell>Image</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {badgeTypes.map(badge => (
              <TableRow key={badge.id} hover>
                <TableCell>{badge.name}</TableCell>
                <TableCell>{badge.description}</TableCell>
                <TableCell>{badge.level}</TableCell>
                <TableCell>{badge.criteria_type}</TableCell>
                <TableCell>{badge.criteria_threshold}</TableCell>
                <TableCell>{badge.event_type || '-'}</TableCell>
                <TableCell>
                  {badge.image_url ? (
                    <img src={badge.image_url} alt={badge.name} style={{ width: 32, height: 32, borderRadius: 4 }} />
                  ) : '-'}
                </TableCell>
                <TableCell align="right">
                  <IconButton color="primary" onClick={() => handleEdit(badge)} size="small">
                    <EditIcon />
                  </IconButton>
                  <IconButton color="error" onClick={() => handleDelete(badge)} size="small">
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
      <BadgeTypeFormDialog
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleFormSubmit}
        initialValues={editBadge ?? {}}
        isEdit={!!editBadge}
        loading={submitting}
      />
      <Dialog open={!!deleteBadge} onClose={() => setDeleteBadge(null)}>
        <DialogTitle>Delete Badge Type?</DialogTitle>
        <Typography sx={{ px: 3 }}>Are you sure you want to delete this badge type? This action cannot be undone.</Typography>
        <DialogActions>
          <Button onClick={() => setDeleteBadge(null)} disabled={submitting}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" disabled={submitting}>Delete</Button>
        </DialogActions>
      </Dialog>
      <Snackbar
        open={!!snackbar}
        autoHideDuration={4000}
        onClose={() => setSnackbar(null)}
        message={snackbar}
      />
    </Paper>
  );
};

import AdminUserBadgeManager from "./AdminUserBadgeManager";

const AdminBadgesSectionWithUserManager: React.FC = () => (
  <>
    <AdminBadgesSection />
    <AdminUserBadgeManager />
  </>
);

export default AdminBadgesSectionWithUserManager;
