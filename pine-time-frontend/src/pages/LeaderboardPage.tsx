import React, { useEffect, useState, useCallback } from 'react';
import {
  Typography,
  Container,
  Box,
  Paper,
  useTheme,
  alpha,
  Tabs,
  Tab,
  Alert,
  Skeleton,
  Avatar,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  InputAdornment,
  IconButton,
  Tooltip,
  Button
} from '@mui/material';
import {
  EmojiEvents,
  Search,
  Download,
  StarOutlined,
  Person,
  ArrowUpward,
  ArrowDownward
} from '@mui/icons-material';
import api from '../api/client';
import { safeApiCall } from '../utils/api';
import { LeaderboardEntry } from '../types/badges';
import { exportToCsv } from '../utils/exportUtils';

// Extend LeaderboardEntry type to include current_balance property
interface ExtendedLeaderboardEntry extends LeaderboardEntry {
  current_balance?: number;
}

// Define time period filters
const TIME_PERIODS = [
  { id: 'all_time', label: 'All Time' },
  { id: 'monthly', label: 'This Month' },
  { id: 'weekly', label: 'This Week' }
];

const ITEMS_PER_PAGE = 20;

const LeaderboardPage: React.FC = () => {
  const theme = useTheme();
  const [leaderboard, setLeaderboard] = useState<ExtendedLeaderboardEntry[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [timePeriod, setTimePeriod] = useState('all_time');
  const [search, setSearch] = useState('');
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  // Pine Time green theme color
  const pineTimeGreen = '#2E7D32';

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
    try {
      if (isLoadMore) {
        setLoadingMore(true);
      } else {
        setLoading(true);
        setError('');
      }

      // Use the safe API call helper for better error handling
      const leaderboardData = await safeApiCall(
        api.get(`/points/leaderboard?time_period=${timePeriod}&page=${page}&limit=${ITEMS_PER_PAGE}&sort=${sortOrder}`),
        { items: [] }
      );

      // Handle both array and object response formats
      let leaderboardEntries: ExtendedLeaderboardEntry[] = [];
      
      if (Array.isArray(leaderboardData)) {
        leaderboardEntries = leaderboardData;
        setHasMore(false); // No pagination info available
      } else if (leaderboardData.items && Array.isArray(leaderboardData.items)) {
        leaderboardEntries = leaderboardData.items;
        setHasMore(leaderboardData.total > page * ITEMS_PER_PAGE);
      }
      
      // Add rank property to each entry if not already present
      leaderboardEntries = leaderboardEntries.map((entry, index) => ({
        ...entry,
        rank: entry.rank || (page - 1) * ITEMS_PER_PAGE + index + 1
      }));
      
      if (isLoadMore) {
        setLeaderboard(prev => [...prev, ...leaderboardEntries]);
      } else {
        setLeaderboard(leaderboardEntries);
      }
    } catch (err: any) {
      console.error('Error fetching leaderboard:', err);
      setError('Failed to load leaderboard. Please try again later.');
      setHasMore(false);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [timePeriod, page, sortOrder]);

  // Initial data fetch
  useEffect(() => {
    // Reset to page 1 when filter changes
    setPage(1);
    setLeaderboard([]);
    fetchLeaderboard();
  }, [timePeriod, sortOrder, fetchLeaderboard]);

  // Handle time period change
  const handleTimePeriodChange = (_event: React.SyntheticEvent, newValue: string) => {
    setTimePeriod(newValue);
  };

  // Toggle sort order
  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  // Handle load more
  const handleLoadMore = () => {
    if (hasMore && !loadingMore) {
      setPage(prev => prev + 1);
      fetchLeaderboard(true);
    }
  };

  // Filter leaderboard entries based on search
  const filteredLeaderboard = leaderboard.filter(entry =>
    search === '' ||
    (entry.username && entry.username.toLowerCase().includes(search.toLowerCase())) ||
    (entry.full_name && entry.full_name.toLowerCase().includes(search.toLowerCase()))
  );

  // Handle export
  const handleExport = async () => {
    try {
      setExporting(true);
      
      // Fetch all data for export
      const exportData = await safeApiCall(
        api.get(`/points/leaderboard?time_period=${timePeriod}&limit=1000&sort=${sortOrder}`),
        { items: [] }
      );
      
      let exportEntries: ExtendedLeaderboardEntry[] = [];
      
      if (Array.isArray(exportData)) {
        exportEntries = exportData;
      } else if (exportData.items && Array.isArray(exportData.items)) {
        exportEntries = exportData.items;
      }
      
      // Format data for CSV
      const csvData = exportEntries.map((entry, index) => ({
        Rank: entry.rank || index + 1,
        Username: entry.username || '',
        'Full Name': entry.full_name || '',
        Points: entry.points || entry.current_balance || 0,
        Badges: entry.badges || 0
      }));
      
      // Export to CSV
      const fileName = `pine_time_leaderboard_${timePeriod}_${new Date().toISOString().split('T')[0]}.csv`;
      exportToCsv(fileName, csvData);
    } catch (err) {
      console.error('Error exporting leaderboard:', err);
    } finally {
      setExporting(false);
    }
  };

  // Render loading skeletons for leaderboard
  const renderSkeletons = () => (
    <TableBody>
      {Array(10).fill(0).map((_, index) => (
        <TableRow key={`skeleton-${index}`}>
          <TableCell>
            <Skeleton variant="text" width={30} />
          </TableCell>
          <TableCell>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Skeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
              <Box>
                <Skeleton variant="text" width={120} />
                <Skeleton variant="text" width={80} />
              </Box>
            </Box>
          </TableCell>
          <TableCell align="right">
            <Skeleton variant="text" width={60} />
          </TableCell>
          <TableCell align="right">
            <Skeleton variant="text" width={40} />
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  );

  // Get medal color based on rank
  const getMedalColor = (rank: number) => {
    switch (rank) {
      case 1: return '#FFD700'; // Gold
      case 2: return '#C0C0C0'; // Silver
      case 3: return '#CD7F32'; // Bronze
      default: return 'transparent';
    }
  };

  // Render avatar with initials or image
  const renderAvatar = (entry: LeaderboardEntry) => {
    const name = entry.full_name || entry.username || '';
    const initials = name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
    
    const isCurrentUser = entry.id === currentUserId;
    
    return (
      <Avatar 
        src={entry.avatar_url} 
        alt={name}
        sx={{ 
          width: 40, 
          height: 40,
          bgcolor: isCurrentUser ? theme.palette.secondary.main : theme.palette.primary.main,
          border: isCurrentUser ? `2px solid ${theme.palette.secondary.dark}` : 'none',
          mr: 2
        }}
      >
        {initials || <Person />}
      </Avatar>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header section */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h4" 
          fontWeight="bold" 
          sx={{ 
            color: pineTimeGreen,
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <EmojiEvents sx={{ mr: 1, fontSize: 32 }} />
          Leaderboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" sx={{ mt: 1 }}>
          See how you rank against other Pine Time users
        </Typography>
      </Box>
      
      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      {/* Time period tabs */}
      <Paper sx={{ mb: 4, borderRadius: 2 }}>
        <Tabs 
          value={timePeriod} 
          onChange={handleTimePeriodChange}
          variant="fullWidth"
          sx={{ 
            borderBottom: 1, 
            borderColor: 'divider',
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 'medium',
              fontSize: '0.95rem',
            },
            '& .Mui-selected': {
              color: pineTimeGreen,
              fontWeight: 'bold'
            },
            '& .MuiTabs-indicator': {
              backgroundColor: pineTimeGreen
            }
          }}
        >
          {TIME_PERIODS.map(period => (
            <Tab 
              key={period.id} 
              label={period.label} 
              value={period.id} 
            />
          ))}
        </Tabs>
      </Paper>
      
      {/* Search and export controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <TextField
          placeholder="Search users..."
          size="small"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ width: 250 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search fontSize="small" />
              </InputAdornment>
            ),
          }}
        />
        
        <Box>
          <Tooltip title={`Sort by ${sortOrder === 'desc' ? 'Highest First' : 'Lowest First'}`}>
            <IconButton onClick={toggleSortOrder} size="small" sx={{ mr: 1 }}>
              {sortOrder === 'desc' ? <ArrowDownward /> : <ArrowUpward />}
            </IconButton>
          </Tooltip>
          
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={handleExport}
            disabled={exporting || loading}
            size="small"
            sx={{ 
              borderColor: pineTimeGreen, 
              color: pineTimeGreen,
              '&:hover': {
                borderColor: pineTimeGreen,
                backgroundColor: alpha(pineTimeGreen, 0.1)
              }
            }}
          >
            {exporting ? 'Exporting...' : 'Export'}
          </Button>
        </Box>
      </Box>
      
      {/* Leaderboard table */}
      <TableContainer component={Paper} sx={{ borderRadius: 2, overflow: 'hidden', mb: 4 }}>
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow sx={{ backgroundColor: alpha(pineTimeGreen, 0.1) }}>
              <TableCell width="10%" sx={{ fontWeight: 'bold' }}>#</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>User</TableCell>
              <TableCell align="right" sx={{ fontWeight: 'bold' }}>Points</TableCell>
              <TableCell align="right" sx={{ fontWeight: 'bold' }}>Badges</TableCell>
            </TableRow>
          </TableHead>
          
          {loading && !loadingMore ? (
            renderSkeletons()
          ) : filteredLeaderboard.length > 0 ? (
            <TableBody>
              {filteredLeaderboard.map((entry) => {
                const isCurrentUser = entry.id === currentUserId;
                const medalColor = getMedalColor(entry.rank || 0);
                
                return (
                  <TableRow 
                    key={entry.id}
                    sx={{ 
                      backgroundColor: isCurrentUser ? alpha(theme.palette.secondary.main, 0.1) : 'inherit',
                      '&:hover': {
                        backgroundColor: isCurrentUser 
                          ? alpha(theme.palette.secondary.main, 0.15) 
                          : alpha(theme.palette.action.hover, 0.1)
                      }
                    }}
                  >
                    <TableCell>
                      <Box 
                        sx={{ 
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          width: 30,
                          height: 30,
                          borderRadius: '50%',
                          backgroundColor: medalColor !== 'transparent' ? alpha(medalColor, 0.2) : 'transparent',
                          border: medalColor !== 'transparent' ? `2px solid ${medalColor}` : 'none',
                          fontWeight: 'bold',
                          color: medalColor !== 'transparent' ? theme.palette.getContrastText(medalColor) : 'inherit'
                        }}
                      >
                        {entry.rank}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {renderAvatar(entry)}
                        <Box>
                          <Typography variant="body1" fontWeight="medium">
                            {entry.full_name || entry.username}
                            {isCurrentUser && (
                              <Chip 
                                label="You" 
                                size="small" 
                                sx={{ 
                                  ml: 1, 
                                  height: 20,
                                  backgroundColor: alpha(theme.palette.secondary.main, 0.1),
                                  color: theme.palette.secondary.main,
                                  fontWeight: 'bold',
                                  fontSize: '0.7rem'
                                }} 
                              />
                            )}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {entry.username}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Typography 
                        variant="body1" 
                        fontWeight="bold" 
                        sx={{ 
                          color: pineTimeGreen,
                          display: 'inline-flex',
                          alignItems: 'center'
                        }}
                      >
                        <StarOutlined sx={{ fontSize: 16, mr: 0.5 }} />
                        {(entry.points || entry.current_balance || 0).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip 
                        label={entry.badges || 0} 
                        size="small"
                        sx={{ 
                          backgroundColor: alpha('#FF9800', 0.1),
                          color: '#FF9800',
                          fontWeight: 'bold'
                        }} 
                      />
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          ) : (
            <TableBody>
              <TableRow>
                <TableCell colSpan={4} align="center" sx={{ py: 4 }}>
                  <Box sx={{ textAlign: 'center' }}>
                    <EmojiEvents sx={{ fontSize: 60, color: alpha(theme.palette.text.secondary, 0.3), mb: 2 }} />
                    <Typography variant="h6">
                      {search ? 'No matching users found' : 'No leaderboard data available'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {search ? 'Try a different search term' : 'Participate in events to earn points and appear on the leaderboard!'}
                    </Typography>
                  </Box>
                </TableCell>
              </TableRow>
            </TableBody>
          )}
        </Table>
      </TableContainer>
      
      {/* Load more button */}
      {hasMore && filteredLeaderboard.length > 0 && (
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Button
            variant="outlined"
            onClick={handleLoadMore}
            disabled={loadingMore}
            sx={{ 
              borderColor: pineTimeGreen, 
              color: pineTimeGreen,
              '&:hover': {
                borderColor: pineTimeGreen,
                backgroundColor: alpha(pineTimeGreen, 0.1)
              }
            }}
          >
            {loadingMore ? 'Loading...' : 'Load More'}
          </Button>
        </Box>
      )}
    </Container>
  );
};

export default LeaderboardPage;
