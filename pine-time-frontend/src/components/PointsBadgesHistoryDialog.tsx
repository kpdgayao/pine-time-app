import React, { useEffect, useState } from "react";
import api from "../api/client";
import { exportToCsv } from "./exportToCsv";

interface HistoryEntry {
  id: number;
  user_id: number;
  type: "award" | "redeem" | "badge_assign" | "badge_revoke";
  points?: number;
  badge_name?: string;
  timestamp: string;
  admin_name?: string;
}

interface Props {
  userId: number | null;
  open: boolean;
  onClose: () => void;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

const PointsBadgesHistoryDialog: React.FC<Props> = ({ userId, open, onClose }) => {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [exporting, setExporting] = useState(false);
  const token = localStorage.getItem("admin_token");

  useEffect(() => {
    if (!open || !userId) return;
    setLoading(true);
    setError(null);
    api.get(`${API_BASE}/users/${userId}/points_badges_history`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setHistory(res.data))
      .catch(err => setError(err?.response?.data?.detail || "Failed to fetch history."))
      .finally(() => setLoading(false));
  }, [userId, open]);

  const filtered = history.filter(entry =>
    entry.type.toLowerCase().includes(search.toLowerCase()) ||
    (entry.admin_name || "").toLowerCase().includes(search.toLowerCase()) ||
    (entry.badge_name || "").toLowerCase().includes(search.toLowerCase())
  );

  const handleExport = () => {
    setExporting(true);
    const rows = filtered.map(entry => ({
      Time: new Date(entry.timestamp).toLocaleString(),
      Type: entry.type,
      Points: entry.points ?? "-",
      Badge: entry.badge_name ?? "-",
      Admin: entry.admin_name ?? "-",
    }));
    exportToCsv("points_badges_history.csv", rows);
    setExporting(false);
  };

  if (!open) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Points & Badges History</DialogTitle>
      <DialogContent>
        <Stack direction="row" spacing={2} sx={{ mb: 2 }} alignItems="center">
          <TextField
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by type, admin, badge"
            size="small"
            sx={{ width: 220 }}
          />
          <Button onClick={handleExport} disabled={exporting || filtered.length === 0} variant="outlined" size="small">
            {exporting ? "Exporting..." : "Export CSV"}
          </Button>
        </Stack>
        {loading && <Typography>Loading...</Typography>}
        {error && <Alert severity="error">{error}</Alert>}
        <Box sx={{ overflowX: 'auto', mt: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Time</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Points</TableCell>
                <TableCell>Badge</TableCell>
                <TableCell>Admin</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} sx={{ textAlign: "center", color: "#999" }}>No history found.</TableCell>
                </TableRow>
              )}
              {filtered.map(entry => (
                <TableRow key={entry.id}>
                  <TableCell>{new Date(entry.timestamp).toLocaleString()}</TableCell>
                  <TableCell>{entry.type.replace("_", " ")}</TableCell>
                  <TableCell>{entry.points ?? "-"}</TableCell>
                  <TableCell>{entry.badge_name ?? "-"}</TableCell>
                  <TableCell>{entry.admin_name ?? "-"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default PointsBadgesHistoryDialog;
