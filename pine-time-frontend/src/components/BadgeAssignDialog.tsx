import React, { useState, useEffect } from "react";
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, MenuItem, Select, InputLabel, FormControl, CircularProgress, Alert
} from "@mui/material";
import api from "../api/client";
import Stack from '@mui/material/Stack';
interface BadgeType {
  id: number;
  name: string;
  level: string;
}

interface BadgeAssignDialogProps {
  open: boolean;
  onClose: () => void;
  onAssign: () => void;
  userId: number | null;
}

const BadgeAssignDialog: React.FC<BadgeAssignDialogProps> = ({ open, onClose, onAssign, userId }) => {
  const [badgeTypes, setBadgeTypes] = useState<BadgeType[]>([]);
  const [selectedBadgeType, setSelectedBadgeType] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      setLoading(true);
      setError(null);
      api.get("/badges_admin/types/")
        .then(res => setBadgeTypes(res.data))
        .catch(err => setError(err?.response?.data?.detail || "Failed to load badge types."))
        .finally(() => setLoading(false));
      setSelectedBadgeType("");
    }
  }, [open]);

  const handleAssign = async () => {
    if (!userId || !selectedBadgeType) return;
    setSubmitting(true);
    setError(null);
    try {
      const badgeTypeId = Number(selectedBadgeType);
      await api.post("/badges_admin/assign", {
        user_id: userId,
        badge_type_id: badgeTypeId,
        level: badgeTypes.find(b => b.id === badgeTypeId)?.level || "bronze"
      });
      onAssign();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to assign badge.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Assign Badge</DialogTitle>
      <DialogContent>
  <Stack spacing={2}>
    {loading && <CircularProgress />}
    {error && <Alert severity="error">{error}</Alert>}
    <FormControl fullWidth margin="normal" disabled={loading || submitting}>
      <InputLabel id="badge-type-label">Badge Type</InputLabel>
      <Select
        labelId="badge-type-label"
        value={selectedBadgeType}
        label="Badge Type"
        onChange={e => setSelectedBadgeType(e.target.value)}
      >
        {badgeTypes.map(badge => (
          <MenuItem key={badge.id} value={badge.id}>{badge.name} ({badge.level})</MenuItem>
        ))}
      </Select>
    </FormControl>
  </Stack>
</DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={submitting}>Cancel</Button>
        <Button onClick={handleAssign} variant="contained" disabled={!selectedBadgeType || submitting}>
          Assign
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BadgeAssignDialog;
