import React, { useEffect, useState, useRef, useCallback } from "react";
import { 
  Box, 
  Typography, 
  TextField, 
  // Button, - removed unused import
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel, 
  Paper, 
  Avatar, 
  Chip, 
  CircularProgress, 
  useTheme, 
  Tooltip,
  InputAdornment,
  IconButton
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import FilterListIcon from "@mui/icons-material/FilterList";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import DownloadIcon from "@mui/icons-material/Download";
import api from "../api/client";
import { exportToCsv } from "./exportToCsv";
import PointsBadgesDistributionChart from "./PointsBadgesDistributionChart";
import { LeaderboardEntry, LeaderboardFilter } from "../types/badges";

const ITEMS_PER_PAGE = 15;

const PointsBadgesLeaderboard: React.FC = () => {
  const theme = useTheme();
  const [users, setUsers] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [exporting, setExporting] = useState(false);
  const [filter, setFilter] = useState<LeaderboardFilter>({
    time_period: 'all_time',
    page: 1,
    limit: ITEMS_PER_PAGE
  });
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const observerTarget = useRef<HTMLDivElement>(null);

  // Get current user ID
  useEffect(() => {
    api.get('/users/me')
      .then(res => {
        if (res.data && res.data.id) {
          setCurrentUserId(res.data.id);
        }
      })
      .catch(() => {
        // Silently fail - user might not be logged in
      });
  }, []);

  // Fetch leaderboard data
  const fetchLeaderboard = useCallback(async (isLoadMore = false) => {
    if (isLoadMore) {
      setLoadingMore(true);
    } else {
      setLoading(true);
      setError(null);
    }

    try {
      const res = await api.get(
        `/points/leaderboard?time_period=${filter.time_period}&page=${filter.page}&limit=${filter.limit}`
      );
      
      // Support both array and object (paginated) formats
      let newUsers: LeaderboardEntry[] = [];
      
      if (Array.isArray(res.data)) {
        newUsers = res.data;
        setHasMore(false); // No pagination info available
      } else if (res.data && Array.isArray(res.data.items)) {
        newUsers = res.data.items;
        setHasMore(res.data.total > filter.page * filter.limit);
      } else {
        newUsers = []; // fallback
        setHasMore(false);
      }
      
      // Add rank property to each user
      newUsers = newUsers.map((user, index) => ({
        ...user,
        rank: (filter.page - 1) * filter.limit + index + 1
      }));
      
      if (isLoadMore) {
        setUsers(prev => [...prev, ...newUsers]);
      } else {
        setUsers(newUsers);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to fetch leaderboard.");
      setHasMore(false);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [filter]);

  // Initial data fetch
  useEffect(() => {
    // Reset to page 1 when filter changes
    setFilter(prev => ({ ...prev, page: 1 }));
    setUsers([]);
    fetchLeaderboard();
  }, [filter.time_period]);

  // Intersection observer for infinite scroll
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasMore && !loading && !loadingMore) {
          setFilter(prev => ({ ...prev, page: prev.page + 1 }));
          fetchLeaderboard(true);
        }
      },
      { threshold: 1.0 }
    );

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => {
      if (observerTarget.current) {
        observer.unobserve(observerTarget.current);
      }
    };
  }, [hasMore, loading, loadingMore, fetchLeaderboard]);

  // Filter users based on search
  const filtered = users.filter(u =>
    (u.full_name || u.username).toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  // Handle export
  const handleExport = () => {
    setExporting(true);
    const rows = filtered.map(u => ({
      Rank: u.rank,
      Name: u.full_name || u.username,
      Email: u.email,
      Points: u.points,
      Badges: u.badges,
    }));
    exportToCsv("leaderboard.csv", rows);
    setExporting(false);
  };

  // Get medal color based on rank
  const getMedalColor = (rank: number) => {
    switch (rank) {
      case 1: return theme.palette.secondary.main; // Gold
      case 2: return "#C0C0C0"; // Silver
      case 3: return "#CD7F32"; // Bronze
      default: return theme.palette.primary.main;
    }
  };

  // Render avatar with initials or image
  const renderAvatar = (user: LeaderboardEntry) => {
    const name = user.full_name || user.username;
    const initials = name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
    
    return (
      <Avatar 
        src={user.avatar_url} 
        alt={name}
        sx={{ 
          width: 40, 
          height: 40,
          bgcolor: user.id === currentUserId 
            ? theme.palette.secondary.main 
            : theme.palette.primary.main,
          border: user.id === currentUserId 
            ? `2px solid ${theme.palette.secondary.dark}` 
            : 'none'
        }}
      >
        {initials}
      </Avatar>
    );
  };

  return (
    <Paper 
      elevation={2} 
      sx={{ 
        p: 3, 
        borderRadius: 2, 
        mb: 4,
        overflow: 'hidden'
      }}
    >
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold', color: theme.palette.primary.main }}>
        <EmojiEventsIcon sx={{ mr: 1, verticalAlign: 'bottom' }} />
        Points & Badges Leaderboard
      </Typography>
      
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, mb: 3, alignItems: 'center' }}>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel id="time-period-label">Time Period</InputLabel>
          <Select
            labelId="time-period-label"
            id="leaderboard-time-period"
            value={filter.time_period}
            label="Time Period"
            onChange={e => setFilter(prev => ({ 
              ...prev, 
              time_period: e.target.value as 'all_time' | 'weekly' | 'monthly' 
            }))}
            startAdornment={
              <FilterListIcon fontSize="small" sx={{ mr: 1, color: theme.palette.primary.main }} />
            }
          >
            <MenuItem value="all_time">All Time</MenuItem>
            <MenuItem value="weekly">This Week</MenuItem>
            <MenuItem value="monthly">This Month</MenuItem>
          </Select>
        </FormControl>
        
        <TextField
          size="small"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search users"
          sx={{ flexGrow: 1, minWidth: 200 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
        />
        
        <Tooltip title="Export to CSV">
          <IconButton 
            onClick={handleExport} 
            disabled={exporting || filtered.length === 0}
            color="primary"
          >
            <DownloadIcon />
          </IconButton>
        </Tooltip>
      </Box>
      
      {loading && filtered.length === 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}
      
      {error && (
        <Box sx={{ color: "error.main", p: 2, textAlign: 'center' }}>
          {error}
        </Box>
      )}
      
      {filtered.length === 0 && !loading && (
        <Box sx={{ textAlign: "center", color: "text.secondary", p: 4 }}>
          No users found.
        </Box>
      )}
      
      {filtered.length > 0 && (
        <Box sx={{ overflowX: 'auto' }}>
          <Box component="table" sx={{ 
            width: "100%", 
            borderCollapse: "separate", 
            borderSpacing: "0 8px",
          }}>
            <Box component="thead">
              <Box component="tr" sx={{ 
                "& th": { 
                  py: 1.5, 
                  px: 2, 
                  fontWeight: 'bold',
                  color: theme.palette.text.secondary,
                  borderBottom: `2px solid ${theme.palette.divider}`
                } 
              }}>
                <Box component="th" align="center" width="80px">Rank</Box>
                <Box component="th" align="left">User</Box>
                <Box component="th" align="center" width="100px">Points</Box>
                <Box component="th" align="center" width="100px">Badges</Box>
              </Box>
            </Box>
            <Box component="tbody">
              {filtered.map((user) => {
                const isCurrentUser = user.id === currentUserId;
                
                return (
                  <Box 
                    component="tr" 
                    key={user.id ?? `row-${user.rank}`} 
                    sx={{ 
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      backgroundColor: isCurrentUser 
                        ? `${theme.palette.primary.main}10` 
                        : 'transparent',
                      '&:hover': {
                        backgroundColor: `${theme.palette.primary.main}15`,
                      }
                    }}
                  >
                    <Box component="td" align="center" sx={{ py: 1.5, px: 2 }}>
                      {user.rank && user.rank <= 3 ? (
                        <Tooltip title={`Rank #${user.rank}`}>
                          <Avatar
                            sx={{
                              width: 32,
                              height: 32,
                              bgcolor: getMedalColor(user.rank),
                              color: '#fff',
                              fontWeight: 'bold',
                              fontSize: '0.875rem',
                              margin: '0 auto'
                            }}
                          >
                            {user.rank}
                          </Avatar>
                        </Tooltip>
                      ) : (
                        <Typography variant="body2">{user.rank}</Typography>
                      )}
                    </Box>
                    <Box component="td" sx={{ py: 1.5, px: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {renderAvatar(user)}
                        <Box>
                          <Typography variant="body1" fontWeight={isCurrentUser ? 'bold' : 'normal'}>
                            {user.full_name || user.username}
                            {isCurrentUser && (
                              <Chip 
                                label="You" 
                                size="small" 
                                color="secondary" 
                                sx={{ ml: 1, height: 20, fontSize: '0.7rem' }} 
                              />
                            )}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {user.email}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                    <Box component="td" align="center" sx={{ py: 1.5, px: 2 }}>
                      <Chip 
                        label={user.points} 
                        color="primary" 
                        variant={isCurrentUser ? "filled" : "outlined"}
                        sx={{ fontWeight: 'bold' }} 
                      />
                    </Box>
                    <Box component="td" align="center" sx={{ py: 1.5, px: 2 }}>
                      <Chip 
                        label={user.badges} 
                        color="secondary" 
                        variant={isCurrentUser ? "filled" : "outlined"}
                        sx={{ fontWeight: 'bold' }} 
                      />
                    </Box>
                  </Box>
                );
              })}
            </Box>
          </Box>
        </Box>
      )}
      
      {/* Infinite scroll loading indicator */}
      {hasMore && (
        <Box 
          ref={observerTarget} 
          sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            p: 2 
          }}
        >
          {loadingMore && <CircularProgress size={24} />}
        </Box>
      )}
      
      {filtered.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Points & Badges Distribution</Typography>
          <PointsBadgesDistributionChart 
            leaderboard={filtered.map(u => ({ points: u.points, badges: u.badges }))} 
          />
        </Box>
      )}
    </Paper>
  );
};

export default PointsBadgesLeaderboard;
