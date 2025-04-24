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
  Chip
} from '@mui/material';

import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';
import api from '../api/client';
import { Badge as BadgeType } from '../types/badges';
import BadgeProgressBar from '../components/BadgeProgressBar';
import { safeApiCall } from '../utils/api';
import BadgeEarnedCelebration from '../components/BadgeEarnedCelebration';

// Define badge categories for filtering
const BADGE_CATEGORIES = [
  { id: 'all', label: 'All Badges' },
  { id: 'events', label: 'Events' },
  { id: 'social', label: 'Social' },
  { id: 'achievements', label: 'Achievements' }
];

const BadgesPage: React.FC = () => {
  const theme = useTheme();
  const [badges, setBadges] = useState<BadgeType[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('all');
  const [stats, setStats] = useState<{total: number, unlocked: number}>({total: 0, unlocked: 0});
  const [showCelebration, setShowCelebration] = useState(false);
  const [celebrationBadge, setCelebrationBadge] = useState<BadgeType | null>(null);
  
  // Pine Time green theme color
  const pineTimeGreen = '#2E7D32';

  useEffect(() => {
    const fetchBadges = async () => {
      try {
        setLoading(true);
        setError('');
        
        // Use the safe API call helper for better error handling
        const badgesData = await safeApiCall(
          api.get('/badges/users/me/badges'),
          { badges: [] }
        );
        
        // Handle both array and object response formats
        let badgesList: BadgeType[] = [];
        
        if (Array.isArray(badgesData)) {
          badgesList = badgesData;
        } else if (badgesData.badges && Array.isArray(badgesData.badges)) {
          badgesList = badgesData.badges;
        }
        
        // Process badges to ensure they have all required properties
        const processedBadges = badgesList.map(badge => ({
          ...badge,
          name: badge.name || (badge as any).badge_type_obj?.name || 'Unknown Badge',
          description: badge.description || (badge as any).badge_type_obj?.description || '',
          category: badge.category || (badge as any).badge_type_obj?.category || 'Achievements',
          level: badge.level || 1,
          progress: badge.progress || 0,
          next_level_threshold: badge.next_level_threshold || 100
        }));
        
        setBadges(processedBadges);
        
        // Calculate stats
        setStats({
          total: processedBadges.length,
          unlocked: processedBadges.filter(b => b.progress > 0).length
        });
        
        // Check for newly earned badges (in a real app, this would come from a notification or context)
        const urlParams = new URLSearchParams(window.location.search);
        const newBadgeId = urlParams.get('new_badge');
        
        if (newBadgeId) {
          const newBadge = processedBadges.find(b => b.id.toString() === newBadgeId);
          if (newBadge) {
            setCelebrationBadge(newBadge);
            setShowCelebration(true);
            
            // Clean up URL parameter after showing celebration
            const newUrl = window.location.pathname;
            window.history.replaceState({}, document.title, newUrl);
          }
        }
      } catch (err: any) {
        console.error('Error fetching badges:', err);
        setError('Failed to load badges. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchBadges();
  }, []);

  // Filter badges by category
  const filteredBadges = badges.filter(badge => 
    activeCategory === 'all' || badge.category?.toLowerCase() === activeCategory
  );

  // Handle category change
  const handleCategoryChange = (_event: React.SyntheticEvent, newValue: string) => {
    setActiveCategory(newValue);
  };

  // Render loading skeletons
  const renderSkeletons = () => {
    return Array(4).fill(0).map((_, index) => (
      <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }} key={`skeleton-${index}`}>
        <Paper 
          elevation={2} 
          sx={{ 
            p: 2.5, 
            borderRadius: 2, 
            mb: 2,
            height: '180px',
            width: '100%'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Skeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
            <Box sx={{ width: '100%' }}>
              <Skeleton variant="text" width="60%" />
              <Skeleton variant="text" width="40%" />
            </Box>
          </Box>
          <Skeleton variant="text" />
          <Skeleton variant="text" width="80%" />
          <Skeleton variant="rectangular" height={10} sx={{ mt: 2, borderRadius: 5 }} />
        </Paper>
      </Grid>
    ));
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Badge celebration overlay */}
      {showCelebration && celebrationBadge && (
        <BadgeEarnedCelebration 
          badge={celebrationBadge}
          onClose={() => setShowCelebration(false)}
          open={showCelebration}
        />
      )}
      
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
          <EmojiEventsIcon sx={{ mr: 1, fontSize: 32 }} />
          Your Badges
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" sx={{ mt: 1 }}>
          Track your achievements and progress in Pine Time
        </Typography>
      </Box>
      
      {/* Stats overview */}
      <Paper 
        elevation={3} 
        sx={{ 
          p: 3, 
          mb: 4, 
          borderRadius: 2,
          background: `linear-gradient(135deg, ${alpha(pineTimeGreen, 0.05)} 0%, ${alpha(pineTimeGreen, 0.1)} 100%)`
        }}
      >
        <Grid container spacing={3}>
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6' } }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box 
                sx={{ 
                  width: 60, 
                  height: 60, 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  backgroundColor: alpha(pineTimeGreen, 0.15),
                  color: pineTimeGreen,
                  mr: 2
                }}
              >
                <EmojiEventsIcon sx={{ fontSize: 30 }} />
              </Box>
              <Box>
                <Typography variant="h5" fontWeight="bold">
                  {loading ? <Skeleton width={60} /> : stats.unlocked}/{stats.total}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Badges Unlocked
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 6' } }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box 
                sx={{ 
                  width: 60, 
                  height: 60, 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  backgroundColor: alpha('#FF9800', 0.15),
                  color: '#FF9800',
                  mr: 2
                }}
              >
                <LocalFireDepartmentIcon sx={{ fontSize: 30 }} />
              </Box>
              <Box>
                <Typography variant="h5" fontWeight="bold">
                  {loading ? (
                    <Skeleton width={60} />
                  ) : (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      2
                      <Chip 
                        label="week streak" 
                        size="small" 
                        sx={{ 
                          ml: 1, 
                          backgroundColor: alpha('#FF9800', 0.1),
                          color: '#FF9800',
                          fontWeight: 'bold'
                        }} 
                      />
                    </Box>
                  )}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Current Streak
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Category tabs */}
      <Paper sx={{ mb: 4, borderRadius: 2 }}>
        <Tabs 
          value={activeCategory} 
          onChange={handleCategoryChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ 
            borderBottom: 1, 
            borderColor: 'divider',
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 'medium',
              fontSize: '0.95rem',
              minWidth: 100,
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
          {BADGE_CATEGORIES.map(category => (
            <Tab 
              key={category.id} 
              label={category.label} 
              value={category.id} 
            />
          ))}
        </Tabs>
      </Paper>
      
      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      {/* No badges message */}
      {!loading && !error && filteredBadges.length === 0 && (
        <Paper 
          elevation={2} 
          sx={{ 
            p: 4, 
            borderRadius: 2, 
            mb: 4,
            textAlign: 'center',
            backgroundColor: alpha(theme.palette.background.paper, 0.6)
          }}
        >
          <EmojiEventsIcon sx={{ fontSize: 60, color: alpha(pineTimeGreen, 0.3), mb: 2 }} />
          <Typography variant="h6">
            No {activeCategory !== 'all' ? BADGE_CATEGORIES.find(c => c.id === activeCategory)?.label : ''} Badges Found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Participate in events and activities to earn badges!
          </Typography>
        </Paper>
      )}
      
      {/* Badges grid */}
      <Grid container spacing={3}>
        {loading ? (
          renderSkeletons()
        ) : (
          filteredBadges.map((badge) => (
            <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }} key={badge.id}>
              <BadgeProgressBar badge={badge} />
            </Grid>
          ))
        )}
      </Grid>
    </Container>
  );
};

export default BadgesPage;
