import React, { useState, useEffect } from "react";
import {
  Box, Typography, Paper, CircularProgress, Alert, Button, IconButton, TextField, List, ListItem, ListItemText, ListItemSecondaryAction, Snackbar, Dialog, DialogTitle, DialogActions
} from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import api from "../api/client";
import BadgeAssignDialog from "./BadgeAssignDialog";
import ListItemButton from '@mui/material/ListItemButton';

interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
}

interface BadgeTypeObj {
  name?: string;
  description?: string;
  image_url?: string;
  level?: string;
  // Add other badge type fields as needed
}

interface Badge {
  id: number;
  name: string;
  description: string;
  level: string;
  earned_date?: string;
  badge_type_obj?: BadgeTypeObj;
}

const AdminUserBadgeManager: React.FC = () => {
  // ...existing state and logic
  const [removeBadge, setRemoveBadge] = useState<any>(null);
  const [submitting, setSubmitting] = useState(false);

  // Remove handler for legacy 'revoking' and 'handleRevoke'

  // Handler for remove button click
  const handleRemove = (badge: any) => {
    setRemoveBadge(badge);
  };

  // Handler for confirming badge removal
  const handleRemoveConfirm = async () => {
    if (!removeBadge) return;
    setSubmitting(true);
    try {
      await api.delete(`/badges_admin/user_badges/${removeBadge.id}`);
      setSnackbar("Badge removed from user.");
      setRemoveBadge(null);
      // Refresh badges list
      if (selectedUser) {
        // Inline fetchUserBadges logic for badge refresh
        setLoadingBadges(true);
        setError(null);
        api.get(`/badges_admin/user_badges/${selectedUser.id}`)
          .then(res => setUserBadges(res.data))
          .catch(err => setError(err?.response?.data?.detail || "Failed to fetch user badges."))
          .finally(() => setLoadingBadges(false));
      }
    } catch (err: any) {
      setSnackbar(err?.response?.data?.detail || "Failed to remove badge.");
    } finally {
      setSubmitting(false);
    }
  };

  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState("");
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [userBadges, setUserBadges] = useState<Badge[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [loadingBadges, setLoadingBadges] = useState(false);
  const [assignOpen, setAssignOpen] = useState(false);
  const [snackbar, setSnackbar] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoadingUsers(true);
    api.get("/users/?limit=1000")
      .then(res => setUsers(res.data.items || res.data))
      .catch(() => setError("Failed to load users."))
      .finally(() => setLoadingUsers(false));
  }, []);

  useEffect(() => {
    if (selectedUser) {
      setLoadingBadges(true);
      api.get(`/badges/users/${selectedUser.id}`)
        .then(res => setUserBadges(res.data.badges || res.data))
        .catch(() => setUserBadges([]))
        .finally(() => setLoadingBadges(false));
    } else {
      setUserBadges([]);
    }
  }, [selectedUser]);

  const handleAssign = () => {
    setAssignOpen(false);
    setSnackbar("Badge assigned.");
    // Refresh badges
    if (selectedUser) {
      setLoadingBadges(true);
      api.get(`/badges/users/${selectedUser.id}`)
        .then(res => setUserBadges(res.data.badges || res.data))
        .catch(() => setUserBadges([]))
        .finally(() => setLoadingBadges(false));
    }
  };

  const filteredUsers = users.filter(u =>
    (u.full_name || u.username).toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom>User Badge Management</Typography>
      <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
        <Paper sx={{ p: 2, minWidth: 320, maxHeight: 400, overflow: 'auto' }}>
          <Typography variant="subtitle1">Users</Typography>
          <TextField
            label="Search users"
            variant="outlined"
            size="small"
            fullWidth
            value={search}
            onChange={e => setSearch(e.target.value)}
            sx={{ mb: 1 }}
          />
          {loadingUsers ? <CircularProgress size={20} /> : (
            <List dense>
              {filteredUsers.map(user => (
                <ListItem key={user.id} disablePadding>
  <ListItemButton
    selected={selectedUser?.id === user.id}
    onClick={() => setSelectedUser(user)}
  >
    <ListItemText primary={user.full_name || user.username} secondary={user.email} />
  </ListItemButton>
</ListItem>
              ))}
            </List>
          )}
        </Paper>
        <Paper sx={{ p: 2, minWidth: 340 }}>
          <Typography variant="subtitle1">{selectedUser ? `Badges for ${selectedUser.full_name || selectedUser.username}` : "Select a user"}</Typography>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {loadingBadges ? (
            <CircularProgress sx={{ display: 'block', mx: 'auto', my: 4 }} />
          ) : (
            <List>
              {userBadges.length === 0 ? (
                <ListItem>
                  <ListItemText primary="No badges assigned." />
                </ListItem>
              ) : (
                userBadges.map((badge) => (
                  <ListItem key={badge.id} divider>
                    <ListItemText
                      primary={badge.badge_type_obj?.image_url || badge.badge_type_obj?.name || 'Unknown Badge'}
                      secondary={badge.badge_type_obj?.description || ''}
                    />
                    <ListItemSecondaryAction>
                      <IconButton edge="end" color="error" onClick={() => handleRemove(badge)}>
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))
              )}
            </List>
          )}
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setAssignOpen(true)} sx={{ mt: 2 }}>
            Assign Badge
          </Button>
        </Paper>
      </Box>
      <BadgeAssignDialog
        open={assignOpen}
        onClose={() => setAssignOpen(false)}
        onAssign={handleAssign}
        userId={selectedUser?.id || null}
      />
      <Dialog open={!!removeBadge} onClose={() => setRemoveBadge(null)}>
        <DialogTitle>Remove Badge?</DialogTitle>
        <Typography sx={{ px: 3 }}>Are you sure you want to remove this badge from the user?</Typography>
        <DialogActions>
          <Button onClick={() => setRemoveBadge(null)} disabled={submitting}>Cancel</Button>
          <Button onClick={handleRemoveConfirm} color="error" disabled={submitting}>Remove</Button>
        </DialogActions>
      </Dialog>
      <Snackbar
        open={!!snackbar}
        autoHideDuration={4000}
        onClose={() => setSnackbar(null)}
        message={snackbar}
      />
    </Box>
  );
};

export default AdminUserBadgeManager;
