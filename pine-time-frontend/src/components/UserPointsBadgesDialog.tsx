import React, { useEffect, useState } from "react";
import api from "../api/client";
import PointsBadgesHistoryDialog from "./PointsBadgesHistoryDialog";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Box,
  Typography,
  Button,
  TextField,
  MenuItem,
  Alert
} from "@mui/material";

interface Badge {
  id: number;
  name: string;
  description: string;
  icon_url?: string;
}

interface Props {
  userId: number | null;
  open: boolean;
  onClose: () => void;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

const UserPointsBadgesDialog: React.FC<Props> = ({ userId, open, onClose }) => {
  // Analytics/history dialog state
  const [historyOpen, setHistoryOpen] = useState(false);
  // Bulk assign state
  const [bulkOpen, setBulkOpen] = useState(false);
  const [bulkUserIds, setBulkUserIds] = useState<number[]>([]);
  const [bulkPoints, setBulkPoints] = useState(0);
  const [bulkBadgeId, setBulkBadgeId] = useState<number | null>(null);
  const [bulkMsg, setBulkMsg] = useState<string>("");
  const [points, setPoints] = useState<number>(0);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [allBadges, setAllBadges] = useState<Badge[]>([]);

  const [awardPoints, setAwardPoints] = useState(0);
  const [redeemPoints, setRedeemPoints] = useState(0);
  const [badgeToAssign, setBadgeToAssign] = useState<number | null>(null);
  const [actionMsg, setActionMsg] = useState<string>("");

  const token = localStorage.getItem("admin_token");

  const fetchData = () => {
    if (!open || !userId) return;
    Promise.all([
      api.get(`${API_BASE}/users/${userId}/points`, { headers: { Authorization: `Bearer ${token}` } }),
      api.get(`${API_BASE}/users/${userId}/badges`, { headers: { Authorization: `Bearer ${token}` } }),
      api.get(`${API_BASE}/badges/`, { headers: { Authorization: `Bearer ${token}` } }),
    ])
      .then(([pointsRes, badgesRes, allBadgesRes]) => {
        setPoints(pointsRes.data.points ?? 0);
        setBadges(badgesRes.data ?? []);
        setAllBadges(allBadgesRes.data ?? []);
      })
      .catch(() => {/* error handling removed: setError no longer exists */})
      ;
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line
  }, [userId, open]);

  // Analytics: Fetch leaderboard rank, total points/badges
  const [rank, setRank] = useState<number | null>(null);
  const [totalUsers, setTotalUsers] = useState(0);
  useEffect(() => {
    if (!open || !userId) return;
    api.get(`${API_BASE}/leaderboard`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => {
        setTotalUsers(res.data.length);
        const idx = res.data.findIndex((u: any) => u.id === userId);
        setRank(idx >= 0 ? idx + 1 : null);
      });
  }, [userId, open]);

  const handleAwardPoints = () => {
    setActionMsg("");
    api.post(`${API_BASE}/points/award`, { user_id: userId, points: awardPoints }, { headers: { Authorization: `Bearer ${token}` } })
      .then(() => { setActionMsg("Points awarded!"); fetchData(); setAwardPoints(0); })
      .catch(() => {/* error handling removed: setError no longer exists */});
  };
  const handleRedeemPoints = () => {
    setActionMsg("");
    api.post(`${API_BASE}/points/redeem`, { user_id: userId, points: redeemPoints }, { headers: { Authorization: `Bearer ${token}` } })
      .then(() => { setActionMsg("Points redeemed!"); fetchData(); setRedeemPoints(0); })
      .catch(() => {/* error handling removed: setError no longer exists */});
  };
  const handleAssignBadge = () => {
    setActionMsg("");
    if (!badgeToAssign) return;
    api.post(`${API_BASE}/badges/assign`, { user_id: userId, badge_id: badgeToAssign }, { headers: { Authorization: `Bearer ${token}` } })
      .then(() => { setActionMsg("Badge assigned!"); fetchData(); setBadgeToAssign(null); })
      .catch(() => {/* error handling removed: setError no longer exists */});
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>User Points & Badges</DialogTitle>
      <DialogContent>
        <Stack direction="row" spacing={3} sx={{ mb: 2 }}>
          <Typography><strong>Points:</strong> {points}</Typography>
          <Typography><strong>Badges:</strong> {badges.length}</Typography>
          {rank && <Typography><strong>Leaderboard Rank:</strong> {rank} / {totalUsers}</Typography>}
        </Stack>
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          <Button onClick={() => setHistoryOpen(true)} variant="outlined" size="small">View History</Button>
          <Button onClick={() => setBulkOpen(true)} variant="outlined" size="small">Bulk Assign</Button>
        </Stack>
        <Stack direction="row" spacing={2} sx={{ mb: 2, mt: 2 }} alignItems="center">
          <TextField
            type="number"
            label="Points to award"
            value={awardPoints}
            onChange={e => setAwardPoints(Number(e.target.value))}
            sx={{ width: 100 }}
            inputProps={{ min: 1 }}
          />
          <Button onClick={handleAwardPoints} disabled={awardPoints <= 0} variant="contained">Award</Button>
          <TextField
            type="number"
            label="Points to redeem"
            value={redeemPoints}
            onChange={e => setRedeemPoints(Number(e.target.value))}
            sx={{ width: 100 }}
            inputProps={{ min: 1 }}
          />
          <Button onClick={handleRedeemPoints} disabled={redeemPoints <= 0} variant="contained" color="secondary">Redeem</Button>
        </Stack>
        <PointsBadgesHistoryDialog
          userId={userId}
          open={historyOpen}
          onClose={() => setHistoryOpen(false)}
        />
        <Dialog open={bulkOpen} onClose={() => setBulkOpen(false)} maxWidth="xs" fullWidth>
          <DialogTitle>Bulk Points/Badge Assignment</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ minWidth: 300 }}>
              <TextField
                label="User IDs (comma-separated)"
                value={bulkUserIds.join(",")}
                onChange={e => setBulkUserIds(e.target.value.split(",").map(v => Number(v.trim())).filter(Boolean))}
                placeholder="e.g. 1,2,3"
                fullWidth
              />
              <Stack direction="row" spacing={1} alignItems="center">
                <TextField
                  type="number"
                  label="Points to award"
                  value={bulkPoints}
                  onChange={e => setBulkPoints(Number(e.target.value))}
                  sx={{ width: 120 }}
                  inputProps={{ min: 1 }}
                />
                <Button
                  onClick={() => {
                    setBulkMsg("");
                    api.post(`${API_BASE}/points/award_bulk`, { user_ids: bulkUserIds, points: bulkPoints }, { headers: { Authorization: `Bearer ${token}` } })
                      .then(() => setBulkMsg("Points awarded!"))
                      .catch(err => setBulkMsg(err?.response?.data?.detail || "Failed to award points."));
                  }}
                  disabled={bulkUserIds.length === 0 || bulkPoints <= 0}
                  variant="contained"
                >Bulk Award Points</Button>
              </Stack>
              <Stack direction="row" spacing={1} alignItems="center">
                <TextField
                  select
                  label="Badge"
                  value={bulkBadgeId ?? ""}
                  onChange={e => setBulkBadgeId(Number(e.target.value))}
                  sx={{ minWidth: 120 }}
                >
                  <MenuItem value="">Select badge</MenuItem>
                  {allBadges.map(b => <MenuItem key={b.id} value={b.id}>{b.name}</MenuItem>)}
                </TextField>
                <Button
                  onClick={() => {
                    setBulkMsg("");
                    api.post(`${API_BASE}/badges/assign_bulk`, { user_ids: bulkUserIds, badge_id: bulkBadgeId }, { headers: { Authorization: `Bearer ${token}` } })
                      .then(() => setBulkMsg("Badge assigned!"))
                      .catch(err => setBulkMsg(err?.response?.data?.detail || "Failed to assign badge."));
                  }}
                  disabled={bulkUserIds.length === 0 || !bulkBadgeId}
                  variant="contained"
                >Bulk Assign Badge</Button>
              </Stack>
              {bulkMsg && <Alert severity={bulkMsg.includes("Failed") ? "error" : "success"}>{bulkMsg}</Alert>}
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setBulkOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>
        <Box sx={{ mb: 2 }}>
          <Typography fontWeight={600}>Badges:</Typography>
          <Stack component="ul" spacing={1} sx={{ pl: 2 }}>
            {badges.length === 0 && <Typography component="li">No badges.</Typography>}
            {badges.map(badge => (
              <li key={badge.id} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                {badge.icon_url && <img src={badge.icon_url} alt={badge.name} style={{ width: 24, height: 24 }} />}
                {badge.name} - {badge.description}
              </li>
            ))}
          </Stack>
        </Box>
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <TextField
            select
            label="Assign Badge"
            value={badgeToAssign ?? ""}
            onChange={e => setBadgeToAssign(Number(e.target.value))}
            sx={{ minWidth: 120 }}
          >
            <MenuItem value="">Select badge</MenuItem>
            {allBadges.filter(b => !badges.some(ub => ub.id === b.id)).map(badge => (
              <MenuItem key={badge.id} value={badge.id}>{badge.name}</MenuItem>
            ))}
          </TextField>
          <Button onClick={handleAssignBadge} disabled={!badgeToAssign} variant="contained">Assign Badge</Button>
        </Stack>
        {actionMsg && <Alert severity="success" sx={{ mb: 2 }}>{actionMsg}</Alert>}
      </DialogContent>
    </Dialog>
  );
};
export default UserPointsBadgesDialog;
