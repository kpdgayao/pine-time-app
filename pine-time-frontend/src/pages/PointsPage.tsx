import React, { useEffect, useState } from 'react';
import { 
  Typography, 
  Container, 
  Grid, 
  Box, 
  Tabs, 
  Tab, 
  Paper, 
  useTheme,
  Skeleton,
  Alert,
  alpha,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  Chip,
  Button
} from '@mui/material';
import {
  StarOutlined,
  TrendingUp,
  TrendingDown,
  History,
  EmojiEvents,
  DateRange,
  ArrowUpward,
  ArrowDownward
} from '@mui/icons-material';
import api from '../api/client';
import { safeApiCall } from '../utils/api';
import { UserStats, RecentActivity } from '../types/badges';
import { format, parseISO } from 'date-fns';

// Define time period filters
const TIME_PERIODS = [
  { id: 'all_time', label: 'All Time' },
  { id: 'monthly', label: 'This Month' },
  { id: 'weekly', label: 'This Week' }
];

// Define activity types with their icons and colors
const ACTIVITY_TYPES = {
  'event_registration': {
    icon: <DateRange />,
    color: '#2196F3',
    label: 'Event Registration'
  },
  'badge_earned': {
    icon: <EmojiEvents />,
    color: '#FF9800',
    label: 'Badge Earned'
  },
  'points_earned': {
    icon: <TrendingUp />,
    color: '#4CAF50',
    label: 'Points Earned'
  },
  'points_redeemed': {
    icon: <TrendingDown />,
    color: '#F44336',
    label: 'Points Redeemed'
  }
};

const PointsPage: React.FC = () => {
  const theme = useTheme();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [timePeriod, setTimePeriod] = useState('all_time');
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [activitiesLoading, setActivitiesLoading] = useState(true);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  // Pine Time green theme color
  const pineTimeGreen = '#2E7D32';

  // Fetch user points stats
  useEffect(() => {
    const fetchPointsStats = async () => {
      try {
        setLoading(true);
        setError('');
        
        // Use the safe API call helper for better error handling
        const statsData = await safeApiCall(
          api.get(`/points/stats?time_period=${timePeriod}`),
          null
        );
        
        if (statsData) {
          // Process the stats data to ensure it has all required properties
          setStats({
            total_points: statsData.current_balance || statsData.total_points || 0,
            total_badges: statsData.total_badges || 0,
            rank: statsData.user_rank || statsData.rank || 0,
            total_users: statsData.total_users || 100,
            streak_count: statsData.streak_count || 0,
            events_attended: statsData.events_attended || 0,
            recent_activities: statsData.recent_activities || [],
            total_points_change: statsData.total_points_change || 0
          });
        }
      } catch (err: any) {
        console.error('Error fetching points stats:', err);
        setError('Failed to load points statistics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPointsStats();
  }, [timePeriod]);

  // Fetch recent activities
  useEffect(() => {
    const fetchActivities = async () => {
      try {
        setActivitiesLoading(true);
        
        // Use the safe API call helper for better error handling
        const activitiesData = await safeApiCall(
          api.get(`/points/activities?time_period=${timePeriod}&sort=${sortOrder}`),
          { activities: [] }
        );
        
        // Handle both array and object response formats
        let activitiesList: RecentActivity[] = [];
        
        if (Array.isArray(activitiesData)) {
          activitiesList = activitiesData;
        } else if (activitiesData.activities && Array.isArray(activitiesData.activities)) {
          activitiesList = activitiesData.activities;
        }
        
        setActivities(activitiesList);
      } catch (err: any) {
        console.error('Error fetching activities:', err);
        // Don't set the main error state here to avoid disrupting the main UI
      } finally {
        setActivitiesLoading(false);
      }
    };
    
    fetchActivities();
  }, [timePeriod, sortOrder]);

  // Handle time period change
  const handleTimePeriodChange = (_event: React.SyntheticEvent, newValue: string) => {
    setTimePeriod(newValue);
  };

  // Toggle sort order
  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      return format(parseISO(dateString), 'MMM d, yyyy h:mm a');
    } catch (e) {
      return dateString;
    }
  };

  // Render loading skeletons for stats
  const renderStatSkeletons = () => {
    return Array(4).fill(0).map((_, index) => (
      <Grid key={`stat-skeleton-${index}`} sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
        <Box sx={{ width: '100%', p: 1 }}>
          <Skeleton variant="rectangular" width="100%" height={100} sx={{ borderRadius: 2 }} />
        </Box>
      </Grid>
    ));
  };

  // Render loading skeletons for activities
  const renderActivitiesSkeleton = () => (
    <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
      {Array(5).fill(0).map((_, index) => (
        <ListItem key={`activity-skeleton-${index}`} divider>
          <ListItemIcon>
            <Skeleton variant="circular" width={24} height={24} />
          </ListItemIcon>
          <ListItemText
            primary={<Skeleton variant="text" width="60%" />}
            secondary={<Skeleton variant="text" width="40%" />}
          />
          <Skeleton variant="text" width={50} />
        </ListItem>
      ))}
    </List>
  );

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
          <StarOutlined sx={{ mr: 1, fontSize: 32 }} />
          Your Points
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" sx={{ mt: 1 }}>
          Track your points, rewards, and activity history
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
      
      {/* Stats cards */}
      {loading ? (
        <Grid container spacing={3}>
          {renderStatSkeletons()}
        </Grid>
      ) : stats ? (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Points Balance */}
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
            <Paper 
              elevation={3} 
              sx={{ 
                p: 2.5, 
                borderRadius: 2,
                height: '100%',
                width: '100%',
                background: `linear-gradient(135deg, ${alpha(pineTimeGreen, 0.05)} 0%, ${alpha(pineTimeGreen, 0.1)} 100%)`,
                borderLeft: `4px solid ${pineTimeGreen}`,
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Current Balance
              </Typography>
              <Typography variant="h4" fontWeight="bold" sx={{ color: pineTimeGreen, mb: 1 }}>
                {stats.total_points.toLocaleString()}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 'auto' }}>
                {stats.total_points_change && stats.total_points_change > 0 ? (
                  <Chip 
                    icon={<TrendingUp fontSize="small" />} 
                    label={`+${stats.total_points_change}%`} 
                    size="small" 
                    sx={{ 
                      backgroundColor: alpha('#4CAF50', 0.1),
                      color: '#4CAF50',
                      fontWeight: 'bold',
                      fontSize: '0.75rem'
                    }} 
                  />
                ) : stats.total_points_change && stats.total_points_change < 0 ? (
                  <Chip 
                    icon={<TrendingDown fontSize="small" />} 
                    label={`${stats.total_points_change}%`} 
                    size="small" 
                    sx={{ 
                      backgroundColor: alpha('#F44336', 0.1),
                      color: '#F44336',
                      fontWeight: 'bold',
                      fontSize: '0.75rem'
                    }} 
                  />
                ) : null}
                <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                  vs. previous period
                </Typography>
              </Box>
            </Paper>
          </Grid>
          
          {/* Rank */}
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
            <Paper 
              elevation={3} 
              sx={{ 
                p: 2.5, 
                borderRadius: 2,
                height: '100%',
                width: '100%',
                borderLeft: `4px solid #9C27B0`,
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Your Rank
              </Typography>
              <Typography variant="h4" fontWeight="bold" sx={{ color: '#9C27B0', mb: 1 }}>
                #{stats.rank}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 'auto' }}>
                out of {stats.total_users} users
              </Typography>
            </Paper>
          </Grid>
          
          {/* Badges */}
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
            <Paper 
              elevation={3} 
              sx={{ 
                p: 2.5, 
                borderRadius: 2,
                height: '100%',
                width: '100%',
                borderLeft: `4px solid #FF9800`,
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Total Badges
              </Typography>
              <Typography variant="h4" fontWeight="bold" sx={{ color: '#FF9800', mb: 1 }}>
                {stats.total_badges}
              </Typography>
              <Button 
                size="small" 
                sx={{ 
                  mt: 'auto', 
                  color: '#FF9800', 
                  '&:hover': { backgroundColor: alpha('#FF9800', 0.1) } 
                }}
                href="/badges"
              >
                View Badges
              </Button>
            </Paper>
          </Grid>
          
          {/* Streak */}
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
            <Paper 
              elevation={3} 
              sx={{ 
                p: 2.5, 
                borderRadius: 2,
                height: '100%',
                width: '100%',
                borderLeft: `4px solid #F44336`,
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Current Streak
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="h4" fontWeight="bold" sx={{ color: '#F44336', mb: 1 }}>
                  {stats.streak_count}
                </Typography>
                <Typography variant="body2" sx={{ ml: 1, mb: 1 }}>
                  weeks
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 'auto' }}>
                {stats.events_attended} events attended
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      ) : null}
      
      {/* Recent Activity */}
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" fontWeight="bold">
            Recent Activity
          </Typography>
          <Tooltip title={`Sort ${sortOrder === 'asc' ? 'Newest First' : 'Oldest First'}`}>
            <IconButton onClick={toggleSortOrder} size="small">
              {sortOrder === 'desc' ? <ArrowDownward /> : <ArrowUpward />}
            </IconButton>
          </Tooltip>
        </Box>
        
        <Paper elevation={2} sx={{ borderRadius: 2, overflow: 'hidden' }}>
          {activitiesLoading ? (
            renderActivitiesSkeleton()
          ) : activities.length > 0 ? (
            <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
              {activities.map((activity) => {
                const activityType = ACTIVITY_TYPES[activity.activity_type] || {
                  icon: <History />,
                  color: '#757575',
                  label: 'Activity'
                };
                
                return (
                  <ListItem key={activity.id} divider>
                    <ListItemIcon sx={{ color: activityType.color }}>
                      {activityType.icon}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body1">
                          {activity.description}
                        </Typography>
                      }
                      secondary={
                        <Typography variant="caption" color="text.secondary">
                          {formatDate(activity.timestamp)}
                        </Typography>
                      }
                    />
                    {activity.points && (
                      <Chip
                        label={activity.activity_type === 'points_redeemed' ? 
                          `-${activity.points}` : 
                          `+${activity.points}`}
                        size="small"
                        sx={{
                          backgroundColor: activity.activity_type === 'points_redeemed' ? 
                            alpha('#F44336', 0.1) : 
                            alpha('#4CAF50', 0.1),
                          color: activity.activity_type === 'points_redeemed' ? 
                            '#F44336' : 
                            '#4CAF50',
                          fontWeight: 'bold'
                        }}
                      />
                    )}
                  </ListItem>
                );
              })}
            </List>
          ) : (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <History sx={{ fontSize: 60, color: alpha(theme.palette.text.secondary, 0.3), mb: 2 }} />
              <Typography variant="h6">
                No Activity Found
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Participate in events and earn badges to see your activity here!
              </Typography>
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default PointsPage;
