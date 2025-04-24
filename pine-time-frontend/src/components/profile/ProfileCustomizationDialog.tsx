import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Avatar,
  CircularProgress,
  Tabs,
  Tab,
  useTheme,
  alpha,
  Snackbar,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';

import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ColorLensIcon from '@mui/icons-material/ColorLens';
import ImageIcon from '@mui/icons-material/Image';
import PersonIcon from '@mui/icons-material/Person';
import CloseIcon from '@mui/icons-material/Close';
import api from '../../api/client';

// Define the interface for avatar options
interface AvatarOption {
  id: string;
  url: string;
  name: string;
  unlocked: boolean;
  requirementText?: string;
}

// Define the interface for banner options
interface BannerOption {
  id: string;
  url: string;
  name: string;
  unlocked: boolean;
  requirementText?: string;
}

// Define the interface for theme options
interface ThemeOption {
  id: string;
  name: string;
  primaryColor: string;
  secondaryColor: string;
  unlocked: boolean;
  requirementText?: string;
}

interface ProfileCustomizationDialogProps {
  open: boolean;
  onClose: () => void;
  currentUser: any;
  onSave: (updates: any) => void;
}

const ProfileCustomizationDialog: React.FC<ProfileCustomizationDialogProps> = ({
  open,
  onClose,
  currentUser,
  onSave
}) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Pine Time green theme color
  const pineTimeGreen = '#2E7D32';
  
  // State for selected customizations
  const [selectedAvatar, setSelectedAvatar] = useState<string>('');
  const [selectedBanner, setSelectedBanner] = useState<string>('');
  const [selectedTheme, setSelectedTheme] = useState<string>('');
  
  // State for available options
  const [avatarOptions, setAvatarOptions] = useState<AvatarOption[]>([]);
  const [bannerOptions, setBannerOptions] = useState<BannerOption[]>([]);
  const [themeOptions, setThemeOptions] = useState<ThemeOption[]>([]);
  
  // Fetch customization options when dialog opens
  useEffect(() => {
    if (open) {
      fetchCustomizationOptions();
      
      // Set initial selections based on current user
      setSelectedAvatar(currentUser?.avatar_id || '');
      setSelectedBanner(currentUser?.banner_id || '');
      setSelectedTheme(currentUser?.theme_id || '');
    }
  }, [open, currentUser]);
  
  // Function to fetch customization options from API
  const fetchCustomizationOptions = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Fetch avatar options
      const avatarResponse = await api.get('/users/customization/avatars');
      if (Array.isArray(avatarResponse.data)) {
        setAvatarOptions(avatarResponse.data);
      } else if (avatarResponse.data && Array.isArray(avatarResponse.data.items)) {
        setAvatarOptions(avatarResponse.data.items);
      } else {
        // Fallback demo data if API fails
        setAvatarOptions([
          { id: 'avatar1', url: '/avatars/avatar1.png', name: 'Default', unlocked: true },
          { id: 'avatar2', url: '/avatars/avatar2.png', name: 'Explorer', unlocked: true },
          { id: 'avatar3', url: '/avatars/avatar3.png', name: 'Adventurer', unlocked: true },
          { id: 'avatar4', url: '/avatars/avatar4.png', name: 'Achiever', unlocked: false, requirementText: 'Earn 5 badges' },
          { id: 'avatar5', url: '/avatars/avatar5.png', name: 'Champion', unlocked: false, requirementText: 'Reach rank 10' },
        ]);
      }
      
      // Fetch banner options
      const bannerResponse = await api.get('/users/customization/banners');
      if (Array.isArray(bannerResponse.data)) {
        setBannerOptions(bannerResponse.data);
      } else if (bannerResponse.data && Array.isArray(bannerResponse.data.items)) {
        setBannerOptions(bannerResponse.data.items);
      } else {
        // Fallback demo data if API fails
        setBannerOptions([
          { id: 'banner1', url: '/banners/banner1.jpg', name: 'Pine Time Default', unlocked: true },
          { id: 'banner2', url: '/banners/banner2.jpg', name: 'Baguio Mountains', unlocked: true },
          { id: 'banner3', url: '/banners/banner3.jpg', name: 'City Lights', unlocked: true },
          { id: 'banner4', url: '/banners/banner4.jpg', name: 'Night Sky', unlocked: false, requirementText: 'Attend 10 events' },
          { id: 'banner5', url: '/banners/banner5.jpg', name: 'VIP', unlocked: false, requirementText: 'Reach rank 20' },
        ]);
      }
      
      // Fetch theme options
      const themeResponse = await api.get('/users/customization/themes');
      if (Array.isArray(themeResponse.data)) {
        setThemeOptions(themeResponse.data);
      } else if (themeResponse.data && Array.isArray(themeResponse.data.items)) {
        setThemeOptions(themeResponse.data.items);
      } else {
        // Fallback demo data if API fails
        setThemeOptions([
          { id: 'theme1', name: 'Pine Time Classic', primaryColor: '#2E7D32', secondaryColor: '#1976D2', unlocked: true },
          { id: 'theme2', name: 'Forest', primaryColor: '#2E7D32', secondaryColor: '#388E3C', unlocked: true },
          { id: 'theme3', name: 'Ocean', primaryColor: '#2E7D32', secondaryColor: '#0277BD', unlocked: true },
          { id: 'theme4', name: 'Sunset', primaryColor: '#2E7D32', secondaryColor: '#E64A19', unlocked: false, requirementText: 'Earn 3 gold badges' },
          { id: 'theme5', name: 'Royal', primaryColor: '#2E7D32', secondaryColor: '#7B1FA2', unlocked: false, requirementText: 'Maintain 5-week streak' },
        ]);
      }
    } catch (err) {
      console.error('Error fetching customization options:', err);
      setError('Failed to load customization options. Please try again later.');
      
      // Set fallback demo data
      setAvatarOptions([
        { id: 'avatar1', url: '/avatars/avatar1.png', name: 'Default', unlocked: true },
        { id: 'avatar2', url: '/avatars/avatar2.png', name: 'Explorer', unlocked: true },
        { id: 'avatar3', url: '/avatars/avatar3.png', name: 'Adventurer', unlocked: true },
      ]);
      
      setBannerOptions([
        { id: 'banner1', url: '/banners/banner1.jpg', name: 'Pine Time Default', unlocked: true },
        { id: 'banner2', url: '/banners/banner2.jpg', name: 'Baguio Mountains', unlocked: true },
      ]);
      
      setThemeOptions([
        { id: 'theme1', name: 'Pine Time Classic', primaryColor: '#2E7D32', secondaryColor: '#1976D2', unlocked: true },
        { id: 'theme2', name: 'Forest', primaryColor: '#2E7D32', secondaryColor: '#388E3C', unlocked: true },
      ]);
    } finally {
      setLoading(false);
    }
  };
  
  // Handle tab change
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };
  
  // Handle save
  const handleSave = async () => {
    setSaving(true);
    setError('');
    
    try {
      const updates = {
        avatar_id: selectedAvatar,
        banner_id: selectedBanner,
        theme_id: selectedTheme
      };
      
      // Call API to save customization
      await api.put(`/users/${currentUser.id}/customization`, updates);
      
      // Call onSave callback with updates
      onSave(updates);
      
      setSuccess('Profile customization saved successfully!');
      
      // Close dialog after a short delay
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      console.error('Error saving customization:', error);
      setError('Failed to save customization. Please try again later.');
    } finally {
      setSaving(false);
    }
  };
  
  // Render avatar options
  const renderAvatarOptions = () => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={40} sx={{ color: pineTimeGreen }} />
        </Box>
      );
    }
    
    return (
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: 2, mt: 1 }}>
        {avatarOptions.map((avatar) => (
          <Box key={avatar.id} sx={{ gridColumn: { xs: 'span 3', sm: 'span 3' } }}>
            <Box
              sx={{
                position: 'relative',
                cursor: avatar.unlocked ? 'pointer' : 'default',
                opacity: avatar.unlocked ? 1 : 0.6,
                transition: 'all 0.2s ease',
                '&:hover': avatar.unlocked ? {
                  transform: 'translateY(-5px)',
                } : {},
              }}
              onClick={() => avatar.unlocked && setSelectedAvatar(avatar.id)}
            >
              <Avatar
                src={avatar.url}
                alt={avatar.name}
                sx={{
                  width: 80,
                  height: 80,
                  margin: '0 auto',
                  border: selectedAvatar === avatar.id ? `3px solid ${pineTimeGreen}` : '3px solid transparent',
                  boxShadow: selectedAvatar === avatar.id ? `0 0 10px ${pineTimeGreen}` : 'none',
                }}
              >
                <PersonIcon />
              </Avatar>
              
              {selectedAvatar === avatar.id && (
                <CheckCircleIcon
                  sx={{
                    position: 'absolute',
                    top: -5,
                    right: 'calc(50% - 45px)',
                    color: pineTimeGreen,
                    backgroundColor: theme.palette.background.paper,
                    borderRadius: '50%',
                    fontSize: 22,
                  }}
                />
              )}
              
              <Typography
                variant="caption"
                align="center"
                sx={{
                  display: 'block',
                  mt: 1,
                  fontWeight: selectedAvatar === avatar.id ? 'bold' : 'normal',
                }}
              >
                {avatar.name}
              </Typography>
              
              {!avatar.unlocked && avatar.requirementText && (
                <Typography
                  variant="caption"
                  align="center"
                  color="text.secondary"
                  sx={{ display: 'block', fontSize: '0.7rem', fontStyle: 'italic' }}
                >
                  {avatar.requirementText}
                </Typography>
              )}
            </Box>
          </Box>
        ))}
      </Box>
    );
  };
  
  // Render banner options
  const renderBannerOptions = () => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={40} sx={{ color: pineTimeGreen }} />
        </Box>
      );
    }
    
    return (
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: 2, mt: 1 }}>
        {bannerOptions.map((banner) => (
          <Box key={banner.id} sx={{ gridColumn: { xs: 'span 6', sm: 'span 4' } }}>
            <Box
              sx={{
                position: 'relative',
                cursor: banner.unlocked ? 'pointer' : 'default',
                opacity: banner.unlocked ? 1 : 0.6,
                transition: 'all 0.2s ease',
                '&:hover': banner.unlocked ? {
                  transform: 'translateY(-5px)',
                } : {},
              }}
              onClick={() => banner.unlocked && setSelectedBanner(banner.id)}
            >
              <Box
                sx={{
                  height: 80,
                  borderRadius: 2,
                  overflow: 'hidden',
                  backgroundImage: `url(${banner.url})`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                  border: selectedBanner === banner.id ? `3px solid ${pineTimeGreen}` : '3px solid transparent',
                  boxShadow: selectedBanner === banner.id ? `0 0 10px ${pineTimeGreen}` : 'none',
                }}
              />
              
              {selectedBanner === banner.id && (
                <CheckCircleIcon
                  sx={{
                    position: 'absolute',
                    top: -5,
                    right: 5,
                    color: pineTimeGreen,
                    backgroundColor: theme.palette.background.paper,
                    borderRadius: '50%',
                    fontSize: 22,
                  }}
                />
              )}
              
              <Typography
                variant="caption"
                align="center"
                sx={{
                  display: 'block',
                  mt: 1,
                  fontWeight: selectedBanner === banner.id ? 'bold' : 'normal',
                }}
              >
                {banner.name}
              </Typography>
              
              {!banner.unlocked && banner.requirementText && (
                <Typography
                  variant="caption"
                  align="center"
                  color="text.secondary"
                  sx={{ display: 'block', fontSize: '0.7rem', fontStyle: 'italic' }}
                >
                  {banner.requirementText}
                </Typography>
              )}
            </Box>
          </Box>
        ))}
      </Box>
    );
  };
  
  // Render theme options
  const renderThemeOptions = () => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={40} sx={{ color: pineTimeGreen }} />
        </Box>
      );
    }
    
    return (
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: 2, mt: 1 }}>
        {themeOptions.map((themeOption) => (
          <Box key={themeOption.id} sx={{ gridColumn: { xs: 'span 6', sm: 'span 4' } }}>
            <Box
              sx={{
                position: 'relative',
                cursor: themeOption.unlocked ? 'pointer' : 'default',
                opacity: themeOption.unlocked ? 1 : 0.6,
                transition: 'all 0.2s ease',
                '&:hover': themeOption.unlocked ? {
                  transform: 'translateY(-5px)',
                } : {},
              }}
              onClick={() => themeOption.unlocked && setSelectedTheme(themeOption.id)}
            >
              <Box
                sx={{
                  height: 80,
                  borderRadius: 2,
                  overflow: 'hidden',
                  background: `linear-gradient(135deg, ${themeOption.primaryColor} 0%, ${themeOption.secondaryColor} 100%)`,
                  border: selectedTheme === themeOption.id ? `3px solid ${pineTimeGreen}` : '3px solid transparent',
                  boxShadow: selectedTheme === themeOption.id ? `0 0 10px ${pineTimeGreen}` : 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography
                  variant="subtitle2"
                  sx={{
                    color: '#fff',
                    textShadow: '0 1px 3px rgba(0,0,0,0.3)',
                    fontWeight: 'bold',
                  }}
                >
                  {themeOption.name}
                </Typography>
              </Box>
              
              {selectedTheme === themeOption.id && (
                <CheckCircleIcon
                  sx={{
                    position: 'absolute',
                    top: -5,
                    right: 5,
                    color: pineTimeGreen,
                    backgroundColor: theme.palette.background.paper,
                    borderRadius: '50%',
                    fontSize: 22,
                  }}
                />
              )}
              
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  mt: 1,
                  gap: 1,
                }}
              >
                <Tooltip title="Primary Color">
                  <Box
                    sx={{
                      width: 20,
                      height: 20,
                      borderRadius: '50%',
                      backgroundColor: themeOption.primaryColor,
                      border: `1px solid ${alpha(theme.palette.text.primary, 0.2)}`,
                    }}
                  />
                </Tooltip>
                <Tooltip title="Secondary Color">
                  <Box
                    sx={{
                      width: 20,
                      height: 20,
                      borderRadius: '50%',
                      backgroundColor: themeOption.secondaryColor,
                      border: `1px solid ${alpha(theme.palette.text.primary, 0.2)}`,
                    }}
                  />
                </Tooltip>
              </Box>
              
              {!themeOption.unlocked && themeOption.requirementText && (
                <Typography
                  variant="caption"
                  align="center"
                  color="text.secondary"
                  sx={{ display: 'block', fontSize: '0.7rem', fontStyle: 'italic' }}
                >
                  {themeOption.requirementText}
                </Typography>
              )}
            </Box>
          </Box>
        ))}
      </Box>
    );
  };

  return (
    <>
      <Dialog
        open={open}
        onClose={onClose}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            overflow: 'hidden',
          }
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h5" fontWeight="bold">
              Customize Your Profile
            </Typography>
            <IconButton onClick={onClose} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <Box sx={{ px: 3 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
            textColor="primary"
            indicatorColor="primary"
            aria-label="customization tabs"
          >
            <Tab 
              icon={<PersonIcon />} 
              label="Avatar" 
              id="customization-tab-0"
              aria-controls="customization-tabpanel-0"
            />
            <Tab 
              icon={<ImageIcon />} 
              label="Banner" 
              id="customization-tab-1"
              aria-controls="customization-tabpanel-1"
            />
            <Tab 
              icon={<ColorLensIcon />} 
              label="Theme" 
              id="customization-tab-2"
              aria-controls="customization-tabpanel-2"
            />
          </Tabs>
        </Box>
        
        <DialogContent sx={{ pt: 2 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Box
            role="tabpanel"
            hidden={activeTab !== 0}
            id="customization-tabpanel-0"
            aria-labelledby="customization-tab-0"
          >
            {activeTab === 0 && (
              <>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Choose an avatar to represent you in Pine Time. Some avatars are unlocked by achieving specific milestones.
                </Typography>
                {renderAvatarOptions()}
              </>
            )}
          </Box>
          
          <Box
            role="tabpanel"
            hidden={activeTab !== 1}
            id="customization-tabpanel-1"
            aria-labelledby="customization-tab-1"
          >
            {activeTab === 1 && (
              <>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Select a banner image for your profile. Special banners can be unlocked through achievements.
                </Typography>
                {renderBannerOptions()}
              </>
            )}
          </Box>
          
          <Box
            role="tabpanel"
            hidden={activeTab !== 2}
            id="customization-tabpanel-2"
            aria-labelledby="customization-tab-2"
          >
            {activeTab === 2 && (
              <>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Choose a color theme for your Pine Time experience. All themes are based on the Pine Time green palette.
                </Typography>
                {renderThemeOptions()}
              </>
            )}
          </Box>
        </DialogContent>
        
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={onClose} variant="outlined" color="inherit">
            Cancel
          </Button>
          <Button 
            onClick={handleSave} 
            variant="contained" 
            color="primary"
            disabled={saving}
            startIcon={saving ? <CircularProgress size={20} /> : null}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>
      
      <Snackbar
        open={!!success}
        autoHideDuration={3000}
        onClose={() => setSuccess('')}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSuccess('')} severity="success" sx={{ width: '100%' }}>
          {success}
        </Alert>
      </Snackbar>
    </>
  );
};

export default ProfileCustomizationDialog;
