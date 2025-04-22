import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Avatar, 
  Paper, 
  Divider, 
  Chip,
  CircularProgress,
  Alert,
  useTheme
} from '@mui/material';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import StarIcon from '@mui/icons-material/Star';
import EventIcon from '@mui/icons-material/Event';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';
import api from '../api/client';
import { Event } from '../types/events';
import { Badge, RecentActivity, UserStats } from '../types/badges';
import StatsCard from '../components/dashboard/StatsCard';
import RecentActivities from '../components/dashboard/RecentActivities';
import UpcomingEvents from '../components/dashboard/UpcomingEvents';
import BadgeProgressSection from '../components/dashboard/BadgeProgressSection';
import PointsHistoryChart from '../components/dashboard/PointsHistoryChart';
import EventRecommendations from '../components/dashboard/EventRecommendations';
import BadgeEarnedCelebration from '../components/BadgeEarnedCelebration';

const ProfilePage: React.FC = () => {
  const theme = useTheme();
  const [profile, setProfile] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  
  // Dashboard data states
  const [stats, setStats] = useState<UserStats | null>(null);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [upcomingEvents, setUpcomingEvents] = useState<Event[]>([]);
  const [recommendedEvents, setRecommendedEvents] = useState<Event[]>([]);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [pointsHistory, setPointsHistory] = useState<{date: string; points: number}[]>([]);
  
  // States for badge celebration
  const [showCelebration, setShowCelebration] = useState(false);
  const [celebrationBadge, setCelebrationBadge] = useState<Badge | null>(null);
  
  // Fetch user profile
  useEffect(() => {
    api.get('/users/me')
      .then(res => {
        setProfile(res.data);
        // Check if there's a new badge to celebrate (this would be passed from another page)
        const urlParams = new URLSearchParams(window.location.search);
        const newBadgeId = urlParams.get('new_badge');
        if (newBadgeId) {
          // Remove the query parameter to prevent showing the celebration again on refresh
          window.history.replaceState({}, document.title, window.location.pathname);
          // Fetch the badge details to show in celebration
          api.get(`/badges/${newBadgeId}`)
            .then(badgeRes => {
              setCelebrationBadge(badgeRes.data);
              setShowCelebration(true);
            })
            .catch(() => {/* Silently fail */});
        }
      })
      .catch(err => {
        let message = 'Failed to load profile.';
        const data = err.response?.data;
        if (typeof data === 'string') {
          message = data;
        } else if (Array.isArray(data)) {
          message = data.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        } else if (typeof data === 'object' && data !== null) {
          message = data.detail || data.msg || JSON.stringify(data);
        }
        setError(message);
      })
      .finally(() => setLoading(false));
  }, []);
  
  // Fetch dashboard data when profile is loaded
  useEffect(() => {
    if (!profile) return;
    
    const userId = profile.id;
    
    // Fetch user stats
    api.get(`/users/${userId}/stats`)
      .then(res => {
        setStats(res.data);
      })
      .catch(() => {/* Set default stats or handle error */});
    
    // Fetch badges with progress
    api.get(`/users/${userId}/badges?include_progress=true`)
      .then(res => {
        // Handle both array and object (paginated) formats
        if (Array.isArray(res.data)) {
          setBadges(res.data);
        } else if (res.data && Array.isArray(res.data.items)) {
          setBadges(res.data.items);
        }
      })
      .catch(() => {/* Handle error */});
    
    // Fetch upcoming events (registered by user)
    api.get(`/users/${userId}/events?status=upcoming&limit=3`)
      .then(res => {
        // Handle both array and object (paginated) formats
        if (Array.isArray(res.data)) {
          setUpcomingEvents(res.data);
        } else if (res.data && Array.isArray(res.data.items)) {
          setUpcomingEvents(res.data.items);
        }
      })
      .catch(() => {/* Handle error */});
    
    // Fetch recommended events
    api.get(`/events/recommended?user_id=${userId}&limit=3`)
      .then(res => {
        // Handle both array and object (paginated) formats
        if (Array.isArray(res.data)) {
          setRecommendedEvents(res.data);
        } else if (res.data && Array.isArray(res.data.items)) {
          setRecommendedEvents(res.data.items);
        }
      })
      .catch(() => {/* Handle error */});
    
    // Fetch recent activities
    api.get(`/users/${userId}/activities?limit=10`)
      .then(res => {
        // Handle both array and object (paginated) formats
        if (Array.isArray(res.data)) {
          setRecentActivities(res.data);
        } else if (res.data && Array.isArray(res.data.items)) {
          setRecentActivities(res.data.items);
        }
      })
      .catch(() => {/* Handle error */});
    
    // Fetch points history for chart
    api.get(`/users/${userId}/points/history?limit=30`)
      .then(res => {
        // Handle both array and object (paginated) formats
        let historyData = [];
        if (Array.isArray(res.data)) {
          historyData = res.data;
        } else if (res.data && Array.isArray(res.data.items)) {
          historyData = res.data.items;
        }
        
        // Transform data for chart
        const chartData = historyData.map((item: any) => ({
          date: item.timestamp,
          points: item.points
        }));
        
        setPointsHistory(chartData);
      })
      .catch(() => {/* Handle error */});
    
  }, [profile]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }
  
  if (!profile) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="warning">No profile found. Please log in.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      {/* Profile Header */}
      <Paper 
        elevation={1} 
        sx={{ 
          p: 3, 
          mb: 4, 
          borderRadius: 2,
          background: `linear-gradient(135deg, ${theme.palette.primary.main}15 0%, ${theme.palette.primary.main}05 100%)`
        }}
      >
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
          <Box sx={{ width: { xs: '100%', md: '16.666%' } }}>
            <Box sx={{ display: 'flex', justifyContent: { xs: 'center', md: 'flex-start' } }}>
              <Avatar 
                src={profile.avatar_url} 
                alt={profile.full_name || profile.username}
                sx={{ 
                  width: 100, 
                  height: 100,
                  border: `4px solid ${theme.palette.primary.main}`,
                  boxShadow: theme.shadows[3]
                }}
              >
                {(profile.full_name || profile.username || '').substring(0, 1).toUpperCase()}
              </Avatar>
            </Box>
          </Box>
          
          <Box sx={{ width: { xs: '100%', md: '50%' } }}>
            <Typography variant="h4" fontWeight="bold">
              {profile.full_name || profile.username}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
              {profile.email}
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
              {profile.user_type && (
                <Chip 
                  label={profile.user_type.charAt(0).toUpperCase() + profile.user_type.slice(1)} 
                  color="primary" 
                  size="small" 
                />
              )}
              {stats?.streak_count && stats.streak_count > 0 && (
                <Chip 
                  icon={<LocalFireDepartmentIcon />}
                  label={`${stats.streak_count} week streak`} 
                  color="secondary" 
                  size="small" 
                />
              )}
            </Box>
          </Box>
          
          <Box sx={{ width: { xs: '100%', md: '33.333%' } }}>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-around',
              flexWrap: 'wrap',
              gap: 2 
            }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="primary">
                  {stats?.total_points || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Points
                </Typography>
              </Box>
              
              <Divider orientation="vertical" flexItem />
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="secondary">
                  {stats?.total_badges || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Badges
                </Typography>
              </Box>
              
              <Divider orientation="vertical" flexItem />
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" fontWeight="bold" color="primary">
                  {stats?.rank || '-'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Rank
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </Paper>
      
      {/* Stats Cards */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', mx: -1.5 }}>
          <Box sx={{ width: { xs: '100%', sm: '50%', md: '25%' }, p: 1.5 }}>
            <StatsCard 
              title="Total Points" 
              value={stats?.total_points || 0} 
              icon={<StarIcon />}
              color="primary"
            />
          </Box>
          <Box sx={{ width: { xs: '100%', sm: '50%', md: '25%' }, p: 1.5 }}>
            <StatsCard 
              title="Total Badges" 
              value={stats?.total_badges || 0} 
              icon={<EmojiEventsIcon />}
              color="secondary"
            />
          </Box>
          <Box sx={{ width: { xs: '100%', sm: '50%', md: '25%' }, p: 1.5 }}>
            <StatsCard 
              title="Events Attended" 
              value={stats?.events_attended || 0} 
              icon={<EventIcon />}
              color="info"
            />
          </Box>
          <Box sx={{ width: { xs: '100%', sm: '50%', md: '25%' }, p: 1.5 }}>
            <StatsCard 
              title="Week Streak" 
              value={stats?.streak_count || 0} 
              icon={<LocalFireDepartmentIcon />}
              color="warning"
              trend={stats?.streak_count ? {
                value: 10, // This would be calculated based on previous data
                label: 'vs last month'
              } : undefined}
            />
          </Box>
        </Box>
      </Box>
      
      {/* Main Dashboard Content */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        {/* Left Column */}
        <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(66.666% - 12px)' } }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Points History Chart */}
            <Box>
              <PointsHistoryChart data={pointsHistory} />
            </Box>
            
            {/* Upcoming Events */}
            <Box>
              <UpcomingEvents events={upcomingEvents} />
            </Box>
          </Box>
        </Box>
        
        {/* Right Column */}
        <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(33.333% - 12px)' } }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Badge Progress */}
            <Box>
              <BadgeProgressSection badges={badges} />
            </Box>
            
            {/* Recent Activities */}
            <Box>
              <RecentActivities activities={recentActivities} />
            </Box>
          </Box>
        </Box>
      </Box>
      
      {/* Recommendations Section */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" fontWeight="bold" sx={{ mb: 2 }}>
          Personalized Recommendations
        </Typography>
        <EventRecommendations events={recommendedEvents} />
      </Box>
      
      {/* Badge Earned Celebration Dialog */}
      <BadgeEarnedCelebration 
        badge={celebrationBadge} 
        open={showCelebration} 
        onClose={() => setShowCelebration(false)} 
      />
    </Container>
  );
};

export default ProfilePage;
