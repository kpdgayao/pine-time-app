import React, { useState } from 'react';
import { useProfileData } from '../hooks/useProfileData';
import { 
  Box, 
  Container, 
  Typography, 
  Paper, 
  Chip,
  Alert,
  useTheme,
  IconButton,
  Tooltip,
  Grid,
  Button
} from '@mui/material';
import LazyAvatar from '../components/LazyAvatar';

import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import StarIcon from '@mui/icons-material/Star';
import EventIcon from '@mui/icons-material/Event';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';
import EditIcon from '@mui/icons-material/Edit';
import RefreshIcon from '@mui/icons-material/Refresh';


// Import types as needed
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
import { getImageUrl } from '../utils/image';

// Safe image URL function with built-in fallbacks
const getSafeImageUrl = (url: string | null | undefined, type: 'avatar' | 'event' = 'event'): string => {
  // First try using the utility function
  const processedUrl = getImageUrl(url, type);
  
  // Define appropriate fallbacks based on type
  const fallbacks = {
    avatar: '/avatar-placeholder.png',
    event: '/event-placeholder.png'
  };
  
  // Return the processed URL or appropriate fallback
  return processedUrl || fallbacks[type];
};

const ProfilePage: React.FC = () => {
  const theme = useTheme();
  // Local state only for streak and customization dialogs (not yet in hook)
  const [showStreakCelebration, setShowStreakCelebration] = useState(false);
  const [streakCount, setStreakCount] = useState(0);
  const [showCustomizationDialog, setShowCustomizationDialog] = useState(false);
  const [approachingMilestones] = useState<Array<{
    type: 'points' | 'streak' | 'rank' | 'badge';
    currentValue: number;
    targetValue: number;
    label: string;
    description: string;
  }>>([]);
  const { showToast } = useToast();

  // Use the new hook for all profile/dashboard/celebration data
  const {
    profile,
    stats,
    badges,
    upcomingEvents,
    recommendedEvents,
    recentActivities,
    loading,
    error,
    showCelebration,
    setShowCelebration,
    celebrationBadge,
    showLevelUpCelebration,
    setShowLevelUpCelebration,
    levelUpBadge,
    previousLevel,
    setProfile,
  } = useProfileData();

  
  
  
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
                <LazyAvatar
                  src={getSafeImageUrl(profile.avatar_url, 'avatar')}
                  alt={profile.full_name || profile.username}
                  sx={{
                    width: 100,
                    height: 100,
                    border: `4px solid ${theme.palette.primary.main}`,
                    boxShadow: theme.shadows[3],
                    transition: 'transform 0.3s ease',
                    bgcolor: theme.palette.primary.main,
                    color: theme.palette.primary.contrastText,
                    '&:hover': {
                      transform: 'scale(1.05)'
                    }
                  }}
                >
                  {(profile.full_name || profile.username || '').substring(0, 1).toUpperCase()}
                </LazyAvatar>
{/*
// Alternate approach using LazyImage for avatar rendering:
<Box sx={{ width: 100, height: 100, borderRadius: '50%', overflow: 'hidden', border: `4px solid ${theme.palette.primary.main}`, boxShadow: theme.shadows[3], transition: 'transform 0.3s ease', '&:hover': { transform: 'scale(1.05)' } }}>
  <LazyImage
    src={profile.avatar_url}
    alt={profile.full_name || profile.username}
    fallbackSrc="/avatars/default.png"
    placeholderSrc="/avatars/default.png"
    width={100}
    height={100}
    borderRadius="50%"
    style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }}
  />
</Box>
*/}

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
          setProfile((prev: any) => ({ ...prev, ...updates }));
          showToast('Profile customization saved successfully!', 'success');
        }}
      />
    </Container>
  );
};

export default ProfilePage;
