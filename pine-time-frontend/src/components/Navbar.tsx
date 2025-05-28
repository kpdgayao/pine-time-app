import React, { useState, useEffect } from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Drawer from '@mui/material/Drawer';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Chip from '@mui/material/Chip';
import Badge from '@mui/material/Badge';
import LinearProgress from '@mui/material/LinearProgress';
// Import the admin access utility - we only need hasAdminAccess now
import { hasAdminAccess } from '../utils/adminAccess';

import MenuIcon from '@mui/icons-material/Menu';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import StarIcon from '@mui/icons-material/Star';
import LeaderboardIcon from '@mui/icons-material/Leaderboard';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';
import Divider from '@mui/material/Divider';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';
import api, { apiLongTimeout, retryApiCall } from '../utils/api';

const navLinks = [
  { label: 'Events', to: '/' },
  { label: 'Profile', to: '/profile' },
];

const rewardsLinks = [
  { label: 'Badges', to: '/badges', icon: <EmojiEventsIcon fontSize="small" /> },
  { label: 'Points', to: '/points', icon: <StarIcon fontSize="small" /> },
  { label: 'Leaderboard', to: '/leaderboard', icon: <LeaderboardIcon fontSize="small" /> },
];

const adminLink = { label: 'Admin Dashboard', to: '/admin' };
const loginLinks = [
  { label: 'Login', to: '/login' },
  { label: 'Register', to: '/register' },
];

const Navbar = (): React.ReactNode => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [rewardsAnchorEl, setRewardsAnchorEl] = useState<null | HTMLElement>(null);
  const [userPoints, setUserPoints] = useState<number>(0);
  const [unreadBadges, setUnreadBadges] = useState<number>(0);
  const [nextBadgeProgress, setNextBadgeProgress] = useState<number>(0);
  const [streakCount, setStreakCount] = useState<number>(0);

  const handleDrawerToggle = () => setDrawerOpen((prev) => !prev);
  const closeDrawer = () => setDrawerOpen(false);
  
  const handleRewardsMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setRewardsAnchorEl(event.currentTarget);
  };
  
  const handleRewardsMenuClose = () => {
    setRewardsAnchorEl(null);
  };

  // Fetch user points and badges data
  useEffect(() => {
    if (!user) return;
    
    const fetchUserData = async () => {
      try {
        // Fetch user points with retry mechanism
        const pointsData = await retryApiCall(
          () => apiLongTimeout.get(`/users/${user.sub}/points`),
          null, // fallback value
          2,    // max retries
          1000  // retry delay in ms
        );
        
        if (pointsData) {
          // Handle different response formats
          if (typeof pointsData.points === 'number') {
            setUserPoints(pointsData.points);
          } else if (typeof pointsData.total_points === 'number') {
            setUserPoints(pointsData.total_points);
          } else if (typeof pointsData === 'number') {
            setUserPoints(pointsData);
          }
        }
        
        try {
          // Fetch user badges with progress using retry mechanism
          let badgeData: any[] = [];
          const badgesData = await retryApiCall(
            () => apiLongTimeout.get(`/users/${user.sub}/badges`, {
              params: { include_progress: true }
            }),
            { items: [], badges: [] }, // fallback value
            2,    // max retries
            1000  // retry delay in ms
          );
          
          // Handle different response formats
          if (Array.isArray(badgesData)) {
            badgeData = badgesData;
          } else if (badgesData && Array.isArray(badgesData.items)) {
            badgeData = badgesData.items;
          } else if (badgesData && Array.isArray(badgesData.badges)) {
            badgeData = badgesData.badges;
          }
            
          // Check for unread/new badges
          const newBadges = badgeData.filter((badge: any) => 
            badge && badge.is_new === true
          );
          setUnreadBadges(newBadges.length);
          
          // Get next badge progress
          const inProgressBadges = badgeData.filter((badge: any) => 
            badge && badge.next_level_threshold && 
            typeof badge.progress === 'number' && 
            badge.progress < badge.next_level_threshold
          );
            
          if (inProgressBadges.length > 0) {
            // Sort by progress percentage (highest first)
            inProgressBadges.sort((a: any, b: any) => {
              const aPercentage = a.progress / a.next_level_threshold;
              const bPercentage = b.progress / b.next_level_threshold;
              return bPercentage - aPercentage;
            });
            
            const nextBadge = inProgressBadges[0];
            setNextBadgeProgress(Math.min(100, (nextBadge.progress / nextBadge.next_level_threshold) * 100));
          } else {
            // Default progress if no in-progress badges
            setNextBadgeProgress(0);
          }
        } catch (badgesError) {
          console.error('Error fetching user badges:', badgesError);
          // Don't fail the entire function, continue with other requests
        }
        
        try {
          // Fetch user stats for streak
          const statsResponse = await api.get(`/users/${user.sub}/stats`);
          if (statsResponse.data) {
            // Handle different response formats
            if (typeof statsResponse.data.streak_count === 'number') {
              setStreakCount(statsResponse.data.streak_count);
            } else if (typeof statsResponse.data.streak === 'number') {
              setStreakCount(statsResponse.data.streak);
            } else if (statsResponse.data.stats && typeof statsResponse.data.stats.streak_count === 'number') {
              setStreakCount(statsResponse.data.stats.streak_count);
            }
          }
        } catch (statsError) {
          console.error('Error fetching user stats:', statsError);
          // Use a default streak count of 0 if the API call fails
          setStreakCount(0);
        }
      } catch (error) {
        console.error('Error in fetchUserData:', error);
        // Set default values in case of overall failure
        setUserPoints(0);
        setUnreadBadges(0);
        setNextBadgeProgress(0);
        setStreakCount(0);
      }
    };
    
    fetchUserData();
  }, [user]);

  const isActive = (to: string) => location.pathname === to;

  const renderNavLinks = (isDrawer = false) => {
    const isRewardsActive = rewardsLinks.some(link => isActive(link.to));
    
    return (
      <>
        {/* Regular nav links */}
        {navLinks.map((link) => (
          <Button
            key={link.to}
            component={RouterLink}
            to={link.to}
            color={isActive(link.to) ? 'secondary' : 'inherit'}
            sx={{
              fontWeight: isActive(link.to) ? 700 : 500,
              bgcolor: isActive(link.to) && !isDrawer ? theme.palette.action.selected : 'transparent',
              borderRadius: 2,
              mx: isDrawer ? 0 : 0.5,
              my: isDrawer ? 0.5 : 0,
              transition: 'background 0.2s',
              minWidth: 100,
              color: isDrawer
                ? theme.palette.text.primary
                : (isActive(link.to)
                  ? theme.palette.secondary.contrastText
                  : theme.palette.primary.contrastText),
            }}
            onClick={isDrawer ? closeDrawer : undefined}
          >
            {link.label}
          </Button>
        ))}
        
        {/* Rewards dropdown or section */}
        {user && (
          isDrawer ? (
            // Drawer version - expanded list
            <>
              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, px: 2, color: 'text.secondary' }}>
                Rewards
              </Typography>
              {rewardsLinks.map((link) => (
                <Button
                  key={link.to}
                  component={RouterLink}
                  to={link.to}
                  color={isActive(link.to) ? 'secondary' : 'inherit'}
                  sx={{
                    fontWeight: isActive(link.to) ? 700 : 500,
                    borderRadius: 2,
                    my: 0.5,
                    justifyContent: 'flex-start',
                    pl: 3,
                    color: theme.palette.text.primary,
                  }}
                  onClick={closeDrawer}
                  startIcon={link.icon}
                >
                  {link.label}
                </Button>
              ))}
              {streakCount > 0 && (
                <Box sx={{ px: 3, py: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LocalFireDepartmentIcon color="warning" fontSize="small" />
                  <Typography variant="body2" color="text.secondary">
                    {streakCount} week streak
                  </Typography>
                </Box>
              )}
            </>
          ) : (
            // Regular navbar version - dropdown
            <Box sx={{ position: 'relative' }}>
              <Button 
                color={isRewardsActive ? 'secondary' : 'inherit'}
                endIcon={<KeyboardArrowDownIcon />}
                onClick={handleRewardsMenuOpen}
                sx={{
                  fontWeight: isRewardsActive ? 700 : 500,
                  bgcolor: isRewardsActive ? theme.palette.action.selected : 'transparent',
                  borderRadius: 2,
                  mx: 0.5,
                  transition: 'background 0.2s',
                  minWidth: 100,
                  color: isRewardsActive
                    ? theme.palette.secondary.contrastText
                    : theme.palette.primary.contrastText,
                }}
              >
                Rewards
                {unreadBadges > 0 && (
                  <Badge badgeContent={unreadBadges} color="secondary" sx={{ ml: 1 }} />
                )}
              </Button>
              <Menu
                anchorEl={rewardsAnchorEl}
                open={Boolean(rewardsAnchorEl)}
                onClose={handleRewardsMenuClose}
                PaperProps={{
                  elevation: 3,
                  sx: { mt: 1, width: 220, borderRadius: 2 }
                }}
              >
                {rewardsLinks.map((link) => (
                  <MenuItem 
                    key={link.to} 
                    component={RouterLink} 
                    to={link.to} 
                    onClick={handleRewardsMenuClose}
                    selected={isActive(link.to)}
                  >
                    <ListItemIcon>
                      {link.icon}
                    </ListItemIcon>
                    <ListItemText primary={link.label} />
                  </MenuItem>
                ))}
                <Divider />
                <Box sx={{ px: 2, py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                    Next badge progress:
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={nextBadgeProgress} 
                    sx={{ height: 8, borderRadius: 4 }} 
                  />
                </Box>
                {streakCount > 0 && (
                  <Box sx={{ px: 2, py: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LocalFireDepartmentIcon color="warning" fontSize="small" />
                    <Typography variant="body2" color="text.secondary">
                      {streakCount} week streak
                    </Typography>
                  </Box>
                )}
              </Menu>
            </Box>
          )
        )}
        
        {/* Admin link */}
        {user && hasAdminAccess(user) && (
          <Button
            key="admin-dashboard"
            color={isActive(adminLink.to) ? 'secondary' : 'inherit'}
            sx={{
              fontWeight: isActive(adminLink.to) ? 700 : 500,
              bgcolor: isActive(adminLink.to) && !isDrawer ? theme.palette.action.selected : 'transparent',
              borderRadius: 2,
              mx: isDrawer ? 0 : 0.5,
              my: isDrawer ? 0.5 : 0,
              transition: 'background 0.2s',
              minWidth: 120,
              color: isDrawer 
                ? theme.palette.text.primary 
                : (isActive(adminLink.to)
                  ? theme.palette.secondary.contrastText
                  : theme.palette.primary.contrastText),
            }}
            onClick={(e) => {
              e.preventDefault();
              if (isDrawer) closeDrawer();
              
              // SIMPLIFIED DIRECT APPROACH
              // Instead of complex token transfers, we'll use a direct dashboard access
              const isDev = import.meta.env.DEV;
              
              // First, verify we have a token to avoid unnecessary redirects
              const token = localStorage.getItem('access_token');
              if (!token) {
                // No token found, need to login first
                const loginUrl = isDev 
                  ? 'http://localhost:5173/login?admin=true' 
                  : '/login?admin=true';
                  
                window.location.href = loginUrl;
                return;
              }
              
              // Direct navigation to admin dashboard in the same tab using HashRouter format
              const adminUrl = isDev 
                ? 'http://localhost:5174/#/' 
                : '/admin/#/';
                
              console.log('Direct navigation to admin dashboard with hash routing:', adminUrl);
              // Navigate in the same tab with the hash format for proper routing
              window.location.href = adminUrl;
              
              // We don't need a fallback since this is already the simplest approach
            }}
          >
            {adminLink.label}
          </Button>
        )}
        
        {/* Login/Logout */}
        {user ? (
          <Button
            color="inherit"
            onClick={() => { closeDrawer(); logout(); }}
            sx={{
              ml: isDrawer ? 0 : 2,
              fontWeight: 600,
              color: isDrawer ? theme.palette.primary.main : theme.palette.primary.contrastText,
            }}
          >
            Logout
          </Button>
        ) : (
          loginLinks.map((link) => (
            <Button
              key={link.to}
              component={RouterLink}
              to={link.to}
              color={isActive(link.to) ? 'secondary' : 'inherit'}
              sx={{
                fontWeight: isActive(link.to) ? 700 : 500,
                bgcolor: isActive(link.to) && !isDrawer ? theme.palette.action.selected : 'transparent',
                borderRadius: 2,
                mx: isDrawer ? 0 : 0.5,
                my: isDrawer ? 0.5 : 0,
                transition: 'background 0.2s',
                minWidth: 100,
                color: isDrawer 
                  ? theme.palette.text.primary 
                  : (isActive(link.to)
                    ? theme.palette.secondary.contrastText
                    : theme.palette.primary.contrastText),
              }}
              onClick={isDrawer ? closeDrawer : undefined}
            >
              {link.label}
            </Button>
          ))
        )}
      </>
    );
  };

  return (
    <AppBar position="static" color="primary" elevation={1}>
      <Toolbar sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ flexGrow: 1, letterSpacing: 1, fontWeight: 800 }}>
          Pine Time App
        </Typography>
        
        {/* Points display - visible on all screen sizes */}
        {user && userPoints > 0 && (
          <Chip
            icon={<StarIcon />}
            label={`${userPoints} pts`}
            color="secondary"
            sx={{ 
              mr: 2, 
              fontWeight: 'bold',
              display: { xs: 'flex', sm: 'flex' },
              '& .MuiChip-icon': { color: 'inherit' }
            }}
          />
        )}
        
        {isMobile ? (
          <>
            <IconButton
              color="inherit"
              aria-label="open navigation menu"
              edge="end"
              onClick={handleDrawerToggle}
              sx={{ ml: 1, transition: 'transform 0.2s' }}
            >
              <MenuIcon />
            </IconButton>
            <Drawer
              anchor="right"
              open={drawerOpen}
              onClose={closeDrawer}
              transitionDuration={300}
              PaperProps={{ sx: { width: 240, pt: 2 } }}
              ModalProps={{ keepMounted: true }}
            >
              <Box sx={{ px: 2, py: 1, minHeight: '100%', display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 700, color: 'primary.main' }}>Menu</Typography>
                <Divider sx={{ mb: 1 }} />
                {renderNavLinks(true)}
              </Box>
            </Drawer>
          </>
        ) : (
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>{renderNavLinks(false)}</Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
