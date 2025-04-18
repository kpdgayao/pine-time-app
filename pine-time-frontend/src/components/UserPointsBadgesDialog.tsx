import React, { useEffect, useState } from "react";
import api from "../api/client";
import PointsBadgesHistoryDialog from "./PointsBadgesHistoryDialog";

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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const token = localStorage.getItem("admin_token");

  const fetchData = () => {
    if (!open || !userId) return;
    setLoading(true);
    setError(null);
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
      .catch((err) => setError(err?.response?.data?.detail || "Failed to fetch user data."))
      .finally(() => setLoading(false));
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
      .catch((err) => setError(err?.response?.data?.detail || "Failed to award points."));
  };
  const handleRedeemPoints = () => {
    setActionMsg("");
    api.post(`${API_BASE}/points/redeem`, { user_id: userId, points: redeemPoints }, { headers: { Authorization: `Bearer ${token}` } })
      .then(() => { setActionMsg("Points redeemed!"); fetchData(); setRedeemPoints(0); })
      .catch((err) => setError(err?.response?.data?.detail || "Failed to redeem points."));
  };
  const handleAssignBadge = () => {
    setActionMsg("");
    if (!badgeToAssign) return;
    api.post(`${API_BASE}/badges/assign`, { user_id: userId, badge_id: badgeToAssign }, { headers: { Authorization: `Bearer ${token}` } })
      .then(() => { setActionMsg("Badge assigned!"); fetchData(); setBadgeToAssign(null); })
      .catch((err) => setError(err?.response?.data?.detail || "Failed to assign badge."));
  };

  if (!open) return null;

  return (
    <div style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.3)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: "white", padding: 24, borderRadius: 8, minWidth: 400, maxWidth: 600, maxHeight: 600, overflow: "auto" }}>
        <h3>User Points & Badges</h3>
        {/* Analytics */}
        <div style={{ marginBottom: 12, display: "flex", gap: 24 }}>
          <div><strong>Points:</strong> {points}</div>
          <div><strong>Badges:</strong> {badges.length}</div>
          {rank && <div><strong>Leaderboard Rank:</strong> {rank} / {totalUsers}</div>}
        </div>
        <div style={{ marginBottom: 12, display: "flex", gap: 8 }}>
          <button onClick={() => setHistoryOpen(true)}>View History</button>
          <button onClick={() => setBulkOpen(true)}>Bulk Assign</button>
        </div>
        {/* History dialog */}
        <PointsBadgesHistoryDialog
          userId={userId}
          open={historyOpen}
          onClose={() => setHistoryOpen(false)}
        />
        {/* Bulk assign modal */}
        {bulkOpen && (
          <div style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.3)", zIndex: 1100, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ background: "white", padding: 24, borderRadius: 8, minWidth: 400, maxWidth: 500 }}>
              <h4>Bulk Points/Badge Assignment</h4>
              <div style={{ marginBottom: 8 }}>
                <label>User IDs (comma-separated): </label>
                <input type="text" style={{ width: 320 }}
                  value={bulkUserIds.join(",")}
                  onChange={e => setBulkUserIds(e.target.value.split(",").map(v => Number(v.trim())).filter(Boolean))}
                  placeholder="e.g. 1,2,3" />
              </div>
              <div style={{ marginBottom: 8, display: "flex", gap: 8 }}>
                <input type="number" min={1} value={bulkPoints} onChange={e => setBulkPoints(Number(e.target.value))} placeholder="Points to award" style={{ width: 120 }} />
                <button onClick={() => {
                  setBulkMsg("");
                  api.post(`${API_BASE}/points/award_bulk`, { user_ids: bulkUserIds, points: bulkPoints }, { headers: { Authorization: `Bearer ${token}` } })
                    .then(() => setBulkMsg("Points awarded!"))
                    .catch(err => setBulkMsg(err?.response?.data?.detail || "Failed to award points."));
                }} disabled={bulkUserIds.length === 0 || bulkPoints <= 0}>Bulk Award Points</button>
              </div>
              <div style={{ marginBottom: 8, display: "flex", gap: 8 }}>
                <select value={bulkBadgeId ?? ""} onChange={e => setBulkBadgeId(Number(e.target.value))}>
                  <option value="">Select badge</option>
                  {allBadges.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                </select>
                <button onClick={() => {
                  setBulkMsg("");
                  api.post(`${API_BASE}/badges/assign_bulk`, { user_ids: bulkUserIds, badge_id: bulkBadgeId }, { headers: { Authorization: `Bearer ${token}` } })
                    .then(() => setBulkMsg("Badge assigned!"))
                    .catch(err => setBulkMsg(err?.response?.data?.detail || "Failed to assign badge."));
                }} disabled={bulkUserIds.length === 0 || !bulkBadgeId}>Bulk Assign Badge</button>
              </div>
              {bulkMsg && <div style={{ color: bulkMsg.includes("Failed") ? "red" : "green" }}>{bulkMsg}</div>}
              <div style={{ marginTop: 12, textAlign: "right" }}>
                <button onClick={() => setBulkOpen(false)}>Close</button>
              </div>
            </div>
          </div>
        )}

        <div style={{ display: "flex", gap: 16, marginBottom: 12 }}>
          <input
            type="number"
            value={awardPoints}
            min={1}
            onChange={e => setAwardPoints(Number(e.target.value))}
            placeholder="Points to award"
            style={{ width: 100 }}
          />
          <button onClick={handleAwardPoints} disabled={awardPoints <= 0}>Award</button>
          <input
            type="number"
            value={redeemPoints}
            min={1}
            onChange={e => setRedeemPoints(Number(e.target.value))}
            placeholder="Points to redeem"
            style={{ width: 100 }}
          />
          <button onClick={handleRedeemPoints} disabled={redeemPoints <= 0}>Redeem</button>
        </div>
        <div style={{ marginBottom: 12 }}>
          <strong>Badges:</strong>
          <ul>
            {badges.length === 0 && <li>No badges.</li>}
            {badges.map(badge => (
              <li key={badge.id} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                {badge.icon_url && <img src={badge.icon_url} alt={badge.name} style={{ width: 24, height: 24 }} />}
                {badge.name} - {badge.description}
              </li>
            ))}
          </ul>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
          <select value={badgeToAssign ?? ""} onChange={e => setBadgeToAssign(Number(e.target.value))}>
            <option value="">Select badge</option>
            {allBadges.filter(b => !badges.some(ub => ub.id === b.id)).map(badge => (
              <option key={badge.id} value={badge.id}>{badge.name}</option>
            ))}
          </select>
          <button onClick={handleAssignBadge} disabled={!badgeToAssign}>Assign Badge</button>
        </div>
        {actionMsg && <div style={{ color: "green", marginBottom: 8 }}>{actionMsg}</div>}
        <div style={{ marginTop: 16, textAlign: "right" }}>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default UserPointsBadgesDialog;
