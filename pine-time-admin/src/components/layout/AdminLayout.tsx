import React from 'react';
import {
  AppBar,
  Box,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Event as EventIcon,
  BarChart as AnalyticsIcon,
  EmojiEvents as BadgesIcon,
  Stars as PointsIcon,
  Logout as LogoutIcon,
  AccountCircle
} from '@mui/icons-material';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ADMIN_ROUTES } from '../../config';
import { useAuth } from '../../contexts/AuthContext';

const drawerWidth = 240;

interface AdminLayoutProps {
  children: React.ReactNode;
}

/**
 * AdminLayout component provides a consistent layout for the admin dashboard
 * with navigation drawer, app bar, and content area.
 * 
 * @param {React.ReactNode} children - Content to display in the main area
 */
export const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  // Handle drawer toggle
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // Handle user menu open
  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  // Handle user menu close
  const handleClose = () => {
    setAnchorEl(null);
  };

  // Handle logout
  const handleLogout = () => {
    handleClose();
    logout();
  };

  // Handle profile navigation
  const handleProfile = () => {
    handleClose();
    navigate('/profile');
  };

  // Navigation items
  const navItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, route: ADMIN_ROUTES.DASHBOARD },
    { text: 'Users', icon: <PeopleIcon />, route: ADMIN_ROUTES.USERS },
    { text: 'Events', icon: <EventIcon />, route: ADMIN_ROUTES.EVENTS },
    { text: 'Analytics', icon: <AnalyticsIcon />, route: ADMIN_ROUTES.ANALYTICS },
    { text: 'Badges', icon: <BadgesIcon />, route: ADMIN_ROUTES.BADGES },
    { text: 'Points', icon: <PointsIcon />, route: ADMIN_ROUTES.POINTS },
  ];

  // Drawer content
  const drawer = (
    <div>
      <Toolbar sx={{ bgcolor: 'primary.main' }}>
        <Typography variant="h6" noWrap component="div" sx={{ color: 'white' }}>
          Pine Time Admin
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton 
              component={Link} 
              to={item.route}
              selected={location.pathname === item.route}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'rgba(46, 125, 50, 0.1)',
                  borderLeft: '4px solid #2E7D32',
                  '&:hover': {
                    backgroundColor: 'rgba(46, 125, 50, 0.2)',
                  }
                }
              }}
            >
              <ListItemIcon sx={{ color: location.pathname === item.route ? 'primary.main' : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          bgcolor: 'primary.main'
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {navItems.find(item => item.route === location.pathname)?.text || 'Admin Dashboard'}
          </Typography>
          
          {/* User menu */}
          <div>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              {user?.full_name ? (
                <Avatar sx={{ bgcolor: 'secondary.main' }}>
                  {user.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                </Avatar>
              ) : (
                <AccountCircle />
              )}
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleProfile}>Profile</MenuItem>
              <MenuItem onClick={handleLogout}>
                <ListItemIcon>
                  <LogoutIcon fontSize="small" />
                </ListItemIcon>
                Logout
              </MenuItem>
            </Menu>
          </div>
        </Toolbar>
      </AppBar>
      
      {/* Drawer for mobile */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
        aria-label="navigation"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        
        {/* Permanent drawer for desktop */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      {/* Main content */}
      <Box
        component="main"
        sx={{ 
          flexGrow: 1, 
          p: 3, 
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          bgcolor: 'background.default'
        }}
      >
        <Toolbar /> {/* Space for fixed app bar */}
        {children}
      </Box>
    </Box>
  );
};

export default AdminLayout;
