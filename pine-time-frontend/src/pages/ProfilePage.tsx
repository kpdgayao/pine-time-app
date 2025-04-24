import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Avatar, 
  Paper, 
  Chip,
  Alert,
  useTheme,
  IconButton,
  Tooltip,
  Grid,
  Button
} from '@mui/material';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import StarIcon from '@mui/icons-material/Star';
import EventIcon from '@mui/icons-material/Event';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';
import EditIcon from '@mui/icons-material/Edit';
import RefreshIcon from '@mui/icons-material/Refresh';
import api from '../api/client';
import { safeApiCall } from '../utils/api';
import { Event } from '../types/events';
import { Badge, RecentActivity, UserStats } from '../types/badges';
import StatsCard from '../components/dashboard/StatsCard';
import RecentActivities from '../components/dashboard/RecentActivities';
import UpcomingEvents from '../components/dashboard/UpcomingEvents';
import BadgeProgressSection from '../components/dashboard/BadgeProgressSection';
import PointsHistory from '../components/dashboard/PointsHistory';
import EventRecommendations from '../components/dashboard/EventRecommendations';
import BadgeEarnedCelebration from '../components/BadgeEarnedCelebration';
import BadgeLevelUpCelebration from '../components/BadgeLevelUpCelebration';
import StreakCelebration from '../components/StreakCelebration';
import ViewAllButton from '../components/ui/ViewAllButton';
import MilestoneApproachIndicator from '../components/MilestoneApproachIndicator';
import ProfileCustomizationDialog from '../components/profile/ProfileCustomizationDialog';
import { useToast } from '../contexts/ToastContext';

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
  
  // States for badge celebration
  const [showCelebration, setShowCelebration] = useState(false);
  const [celebrationBadge, setCelebrationBadge] = useState<Badge | null>(null);
  
  // States for badge level-up celebration
  const [showLevelUpCelebration, setShowLevelUpCelebration] = useState(false);
  const [levelUpBadge, setLevelUpBadge] = useState<Badge | null>(null);
  const [previousLevel, setPreviousLevel] = useState(0);
  
  // States for streak celebration
  const [showStreakCelebration, setShowStreakCelebration] = useState(false);
  const [streakCount, setStreakCount] = useState(0);
  
  // States for profile customization
  const [showCustomizationDialog, setShowCustomizationDialog] = useState(false);
  
  // States for approaching milestones
  const [approachingMilestones] = useState<Array<{
    type: 'points' | 'streak' | 'rank' | 'badge';
    currentValue: number;
    targetValue: number;
    label: string;
    description: string;
  }>>([]);
  
  // Toast context for notifications
  const { showToast } = useToast();
  
  // Fetch user profile
  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        setLoading(true);
        setError('');
        
        // Use safeApiCall for better error handling
        const userData = await safeApiCall(
          api.get('/users/me'),
          null
        );
        
        if (!userData) {
          setError('Failed to load profile data');
          return null;
        }
        
        setProfile(userData);
        
        // Fetch stats immediately after profile is loaded
        if (userData.id) {
          try {
            const statsData = await safeApiCall(
              api.get(`/users/${userData.id}/stats`),
              null
            );
            
            if (statsData) {
              setStats(statsData);
            }
          } catch (error) {
            console.error('Error fetching user stats:', error);
          }
        }
        
        return userData; // Return user data for use in other functions
      } finally {
        setLoading(false);
      }
      
      return null; // Return null if there was an error
    };
    
    const fetchDashboardData = async (userData: any) => {
      if (!userData || !userData.id) {
        console.error('User data not available for dashboard data fetching');
        return;
      }
      
      const userId = userData.id;
      
      // Fetch user badges using safeApiCall
      const badgesResponse = await safeApiCall(
        api.get('/badges/users/me/badges'),
        { badges: [] }
      );
      
      // Handle different response formats
      const badgesData = Array.isArray(badgesResponse) 
        ? badgesResponse 
        : badgesResponse?.badges || [];
      
      setBadges(badgesData);
      
      // Check for newly earned badges
      const newBadge = localStorage.getItem('newBadge');
      if (newBadge) {
        try {
          const badgeData = JSON.parse(newBadge);
          setCelebrationBadge(badgeData);
          setShowCelebration(true);
          localStorage.removeItem('newBadge');
        } catch (error) {
          console.error('Error parsing new badge data:', error);
          localStorage.removeItem('newBadge');
        }
      }
      
      // Check for badge level ups
      const levelUpData = localStorage.getItem('badgeLevelUp');
      if (levelUpData) {
        try {
          const { badge, previousLevel } = JSON.parse(levelUpData);
          setLevelUpBadge(badge);
          setPreviousLevel(previousLevel);
          setShowLevelUpCelebration(true);
          localStorage.removeItem('badgeLevelUp');
        } catch (error) {
          console.error('Error parsing badge level up data:', error);
          localStorage.removeItem('badgeLevelUp');
        }
      }
      
      // Fetch upcoming events using safeApiCall with proper parameters
      try {
          // Get upcoming events from the recommended endpoint
        // This follows the Pine Time API structure as documented
        const upcomingEventsResponse = await safeApiCall(
          api.get('/events/recommended', {
            params: {
              limit: 3
            }
          }),
          { events: [] }
        );
        
        // Handle different response formats
        const upcomingEventsData = Array.isArray(upcomingEventsResponse) 
          ? upcomingEventsResponse 
          : upcomingEventsResponse?.events || [];
        
        setUpcomingEvents(upcomingEventsData.slice(0, 3)); // Show only 3 upcoming events
      } catch (error) {
        console.error('Error fetching upcoming events:', error);
        setUpcomingEvents([]); // Set empty array on error
      }
      
      // Fetch recommended events using safeApiCall
      const recommendedEventsResponse = await safeApiCall(
        api.get('/events/recommended'),
        { events: [] }
      );
      
      // Handle different response formats
      const recommendedEventsData = Array.isArray(recommendedEventsResponse) 
        ? recommendedEventsResponse 
        : recommendedEventsResponse?.events || [];
      
      setRecommendedEvents(recommendedEventsData.slice(0, 4)); // Show only 4 recommended events
      
      // Fetch recent activities using safeApiCall with proper parameters
      try {
        
        // Following Pine Time's API structure and error handling guidelines
        const activitiesResponse = await safeApiCall(
          api.get(`/users/${userData.id}/activities`, {
            params: {
              limit: 5
            }
          }),
          { activities: [] }
        );
        
        // Handle different response formats
        const activitiesData = Array.isArray(activitiesResponse) 
          ? activitiesResponse 
          : activitiesResponse?.activities || [];
        
        setRecentActivities(activitiesData.slice(0, 5)); // Show only 5 recent activities
      } catch (error) {
        console.error('Error fetching user activities:', error);
        setRecentActivities([]); // Set empty array on error
      }
    };
    
    const checkStreakCelebration = () => {
      const streakData = localStorage.getItem('streakCelebration');
      if (streakData) {
        try {
          const { count } = JSON.parse(streakData);
          setStreakCount(count);
          setShowStreakCelebration(true);
          localStorage.removeItem('streakCelebration');
        } catch (error) {
          console.error('Error parsing streak celebration data:', error);
          localStorage.removeItem('streakCelebration');
        }
      }
    };
    
    // Execute all data fetching functions in sequence
    // This ensures proper data dependencies are respected
    const loadData = async () => {
      const userData = await fetchProfileData(); // Load profile first and get user data
      if (userData) {
        await fetchDashboardData(userData); // Pass user data directly to dashboard function
      }
      checkStreakCelebration();
    };
    
    loadData();
  }, []);
  
  // Render loading state with skeleton screens
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Profile Header Skeleton */}
          <Paper sx={{ p: 3, mb: 4, borderRadius: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ 
                width: 80, 
                height: 80, 
                borderRadius: '50%', 
                bgcolor: 'rgba(0, 0, 0, 0.11)' 
              }} />
              <Box sx={{ flex: 1 }}>
                <Box sx={{ height: 24, width: '40%', bgcolor: 'rgba(0, 0, 0, 0.11)', mb: 1, borderRadius: 1 }} />
                <Box sx={{ height: 16, width: '60%', bgcolor: 'rgba(0, 0, 0, 0.11)', borderRadius: 1 }} />
              </Box>
            </Box>
          </Paper>
          
          {/* Stats Cards Skeleton */}
          <Box sx={{ mb: 4 }}>
            <Box sx={{ height: 24, width: '20%', bgcolor: 'rgba(0, 0, 0, 0.11)', mb: 2, borderRadius: 1 }} />
            <Grid container spacing={2}>
              {[1, 2, 3, 4].map((item) => (
                <Grid key={item} sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
                  <Paper sx={{ p: 2, height: 120, borderRadius: 2 }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      <Box sx={{ height: 20, width: '50%', bgcolor: 'rgba(0, 0, 0, 0.11)', borderRadius: 1 }} />
                      <Box sx={{ height: 30, width: '30%', bgcolor: 'rgba(0, 0, 0, 0.11)', borderRadius: 1 }} />
                      <Box sx={{ height: 16, width: '70%', bgcolor: 'rgba(0, 0, 0, 0.11)', borderRadius: 1 }} />
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>
          
          {/* Main Content Skeleton */}
          <Grid container spacing={3}>
            <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 8' } }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {/* Points History Skeleton */}
                <Paper sx={{ p: 2, height: 200, borderRadius: 2 }}>
                  <Box sx={{ height: 24, width: '30%', bgcolor: 'rgba(0, 0, 0, 0.11)', mb: 2, borderRadius: 1 }} />
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {[1, 2, 3].map((item) => (
                      <Box key={item} sx={{ height: 40, bgcolor: 'rgba(0, 0, 0, 0.11)', borderRadius: 1 }} />
                    ))}
                  </Box>
                </Paper>
                
                {/* Events Skeleton */}
                <Paper sx={{ p: 2, height: 200, borderRadius: 2 }}>
                  <Box sx={{ height: 24, width: '30%', bgcolor: 'rgba(0, 0, 0, 0.11)', mb: 2, borderRadius: 1 }} />
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {[1, 2, 3].map((item) => (
                      <Box key={item} sx={{ height: 40, bgcolor: 'rgba(0, 0, 0, 0.11)', borderRadius: 1 }} />
                    ))}
                  </Box>
                </Paper>
              </Box>
            </Grid>
            
            <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {/* Badges Skeleton */}
                <Paper sx={{ p: 2, height: 200, borderRadius: 2 }}>
                  <Box sx={{ height: 24, width: '40%', bgcolor: 'rgba(0, 0, 0, 0.11)', mb: 2, borderRadius: 1 }} />
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {[1, 2].map((item) => (
                      <Box key={item} sx={{ height: 40, bgcolor: 'rgba(0, 0, 0, 0.11)', borderRadius: 1 }} />
                    ))}
                  </Box>
                </Paper>
                
                {/* Activities Skeleton */}
                <Paper sx={{ p: 2, height: 200, borderRadius: 2 }}>
                  <Box sx={{ height: 24, width: '40%', bgcolor: 'rgba(0, 0, 0, 0.11)', mb: 2, borderRadius: 1 }} />
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {[1, 2, 3].map((item) => (
                      <Box key={item} sx={{ height: 30, bgcolor: 'rgba(0, 0, 0, 0.11)', borderRadius: 1 }} />
                    ))}
                  </Box>
                </Paper>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </Container>
    );
  }
  
  // Render error state with retry option
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          action={
            <Button color="inherit" size="small" onClick={() => window.location.reload()}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            Unable to load profile data
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            We're having trouble connecting to the server. This could be due to network issues or server maintenance.
          </Typography>
          <Button 
            variant="contained" 
            onClick={() => window.location.reload()}
            startIcon={<RefreshIcon />}
          >
            Refresh Page
          </Button>
        </Paper>
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
      {/* Profile Header - Completely Restructured Layout */}
      <Paper 
        elevation={2} 
        sx={{ 
          p: { xs: 2, md: 3 }, 
          mb: 4, 
          borderRadius: 2,
          background: `linear-gradient(135deg, ${theme.palette.primary.main}15 0%, ${theme.palette.primary.main}05 100%)`,
          overflow: 'visible', // Changed to visible to prevent clipping
          position: 'relative'
        }}
      >
        {/* Main content container with proper z-index */}
        <Box sx={{ position: 'relative', zIndex: 5 }}>
          {/* Top row: Avatar and User Info */}
          <Box sx={{ 
            display: 'flex', 
            flexWrap: 'wrap', 
            gap: { xs: 2, md: 3 },
            mb: { xs: 2, md: 3 }
          }}>
            {/* Avatar Section */}
            <Box sx={{ width: { xs: '100%', sm: 'auto' }, display: 'flex', justifyContent: { xs: 'center', sm: 'flex-start' } }}>
              <Box sx={{ position: 'relative' }}>
                <Avatar 
                  src={profile.avatar_url} 
                  alt={profile.full_name || profile.username}
                  sx={{ 
                    width: 100, 
                    height: 100,
                    border: `4px solid ${theme.palette.primary.main}`,
                    boxShadow: theme.shadows[3],
                    transition: 'transform 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.05)'
                    }
                  }}
                >
                  {(profile.full_name || profile.username || '').substring(0, 1).toUpperCase()}
                </Avatar>
                <Tooltip title="Edit profile">
                  <IconButton 
                    size="small" 
                    sx={{ 
                      position: 'absolute', 
                      bottom: 0, 
                      right: 0, 
                      backgroundColor: theme.palette.primary.main,
                      color: '#fff',
                      '&:hover': {
                        backgroundColor: theme.palette.primary.dark
                      }
                    }}
                    onClick={() => setShowCustomizationDialog(true)}
                  >
                    <EditIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
            
            {/* User Info Section */}
            <Box sx={{ 
              flex: '1', 
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center'
            }}>
              <Typography variant="h4" fontWeight="bold" sx={{ mb: 0.5 }}>
                {profile.full_name || profile.username}
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
                {profile.email}
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 0.5 }}>
                {profile.user_type && (
                  <Chip 
                    label={profile.user_type.charAt(0).toUpperCase() + profile.user_type.slice(1)} 
                    color="primary" 
                    size="small" 
                    sx={{ fontWeight: 500 }}
                  />
                )}
                {stats?.streak_count && stats.streak_count > 0 && (
                  <Chip 
                    icon={<LocalFireDepartmentIcon />}
                    label={`${stats.streak_count} week streak`} 
                    color="warning" 
                    size="small" 
                    sx={{ 
                      fontWeight: 600,
                      background: stats.streak_count >= 2 ? 
                        `linear-gradient(90deg, ${theme.palette.warning.main}, ${theme.palette.warning.light})` : 
                        undefined,
                      boxShadow: stats.streak_count >= 2 ? 1 : 0,
                      '&:hover': {
                        background: stats.streak_count >= 2 ? 
                          `linear-gradient(90deg, ${theme.palette.warning.main}, ${theme.palette.warning.light})` : 
                          undefined,
                      }
                    }}
                    onClick={() => {
                      if (stats.streak_count >= 2) {
                        setStreakCount(stats.streak_count);
                        setShowStreakCelebration(true);
                      }
                    }}
                  />
                )}
              </Box>
            </Box>
          </Box>
          
          {/* Bottom row: Stats Section - Completely Redesigned */}
          <Box sx={{ 
            display: 'flex',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 2
          }}>
            <Paper 
              elevation={1} 
              sx={{ 
                p: 2, 
                borderRadius: 2,
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(5px)',
                display: 'flex',
                flexWrap: 'wrap',
                justifyContent: 'space-around',
                width: '100%',
                gap: { xs: 2, md: 4 }
              }}
            >
              {/* Points */}
              <Box sx={{ 
                textAlign: 'center',
                minWidth: '80px',
                px: 1
              }}>
                <Typography variant="h5" fontWeight="bold" color="primary" sx={{ mb: 0 }}>
                  {stats?.total_points || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontWeight: 500 }}>
                  POINTS
                </Typography>
              </Box>
              
              {/* Badges */}
              <Box sx={{ 
                textAlign: 'center',
                minWidth: '80px',
                px: 1
              }}>
                <Typography variant="h5" fontWeight="bold" color="secondary" sx={{ mb: 0 }}>
                  {stats?.total_badges || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontWeight: 500 }}>
                  BADGES
                </Typography>
              </Box>
              
              {/* Rank */}
              <Box sx={{ 
                textAlign: 'center',
                minWidth: '80px',
                px: 1
              }}>
                <Typography variant="h5" fontWeight="bold" sx={{ 
                  mb: 0,
                  background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}>
                  {stats?.rank || '-'}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontWeight: 500 }}>
                  RANK
                </Typography>
              </Box>
            </Paper>
          </Box>
        </Box>
        
        {/* Background pattern with lower z-index */}
        <Box sx={{ 
          position: 'absolute', 
          top: 0, 
          right: 0, 
          width: '30%', 
          height: '100%', 
          opacity: 0.05,
          background: `radial-gradient(circle, ${theme.palette.primary.main} 10%, transparent 10.5%) 0 0/20px 20px`,
          zIndex: 1
        }} />
      </Paper>
      
      {/* Stats Cards - Responsive Grid System with Improved Layout */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, pl: 1 }}>
          Your Statistics
        </Typography>
        <Grid container spacing={2}>
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
            <StatsCard 
              title="Total Points" 
              value={stats?.total_points || 0} 
              icon={<StarIcon />}
              color="primary"
              trend={stats?.total_points_change ? {
                value: stats.total_points_change,
                label: 'vs last month'
              } : undefined}
            />
          </Grid>
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
            <StatsCard 
              title="Total Badges" 
              value={stats?.total_badges || 0} 
              icon={<EmojiEventsIcon />}
              color="secondary"
            />
          </Grid>
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
            <StatsCard 
              title="Events Attended" 
              value={stats?.events_attended || 0} 
              icon={<EventIcon />}
              color="info"
            />
          </Grid>
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
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
          </Grid>
        </Grid>
      </Box>
      
      {/* Main Dashboard Content */}
      <Grid container spacing={3}>
        {/* Left Column */}
        <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 8' } }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Points History */}
            <Box>
              <PointsHistory />
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                <ViewAllButton 
                  onClick={() => showToast('Full points history view coming soon!', 'info')} 
                  label="View All Points" 
                  size="small" 
                />
              </Box>
            </Box>
            
            {/* Upcoming Events */}
            <Box>
              <UpcomingEvents events={upcomingEvents} />
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                <ViewAllButton 
                  onClick={() => showToast('Full events calendar coming soon!', 'info')} 
                  label="View All Events" 
                  color="info"
                  size="small" 
                />
              </Box>
            </Box>
          </Box>
        </Grid>
        
        {/* Right Column */}
        <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Badge Progress */}
            <Box>
              <BadgeProgressSection badges={badges} />
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                <ViewAllButton 
                  onClick={() => showToast('Complete badge collection coming soon!', 'info')} 
                  label="View All Badges" 
                  color="secondary"
                  size="small" 
                />
              </Box>
            </Box>
            
            {/* Recent Activities */}
            <Box>
              <RecentActivities activities={recentActivities} />
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                <ViewAllButton 
                  onClick={() => showToast('Activity history coming soon!', 'info')} 
                  label="View All Activities" 
                  color="warning"
                  size="small" 
                />
              </Box>
            </Box>
          </Box>
        </Grid>
      </Grid>
      
      {/* Approaching Milestones Section */}
      {approachingMilestones.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" fontWeight="bold" sx={{ mb: 2 }}>
            Approaching Milestones
          </Typography>
          <Grid container spacing={2}>
            {approachingMilestones.map((milestone, index) => (
              <Grid key={`milestone-${index}`} sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' } }}>
                <MilestoneApproachIndicator
                  type={milestone.type}
                  currentValue={milestone.currentValue}
                  targetValue={milestone.targetValue}
                  label={milestone.label}
                  description={milestone.description}
                />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
      
      {/* Recommendations Section */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" fontWeight="bold" sx={{ mb: 2 }}>
          Personalized Recommendations
        </Typography>
        <EventRecommendations events={recommendedEvents} fullWidth />
      </Box>
      
      {/* Badge Earned Celebration Dialog */}
      <BadgeEarnedCelebration 
        badge={celebrationBadge} 
        open={showCelebration} 
        onClose={() => setShowCelebration(false)} 
      />
      
      {/* Badge Level Up Celebration Dialog */}
      <BadgeLevelUpCelebration
        badge={levelUpBadge}
        previousLevel={previousLevel}
        open={showLevelUpCelebration}
        onClose={() => setShowLevelUpCelebration(false)}
      />
      
      {/* Streak Celebration Dialog */}
      <StreakCelebration
        streakCount={streakCount}
        open={showStreakCelebration}
        onClose={() => setShowStreakCelebration(false)}
      />
      
      {/* Profile Customization Dialog */}
      <ProfileCustomizationDialog
        open={showCustomizationDialog}
        onClose={() => setShowCustomizationDialog(false)}
        currentUser={profile}
        onSave={(updates) => {
          // Update profile with customization changes
          setProfile((prev: any) => ({ ...prev, ...updates }));
          showToast('Profile customization saved successfully!', 'success');
        }}
      />
    </Container>
  );
};

export default ProfilePage;
