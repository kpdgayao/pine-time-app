import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid,
  Card,
  CardContent,
  CardActions,
  CardMedia,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import { Edit, Add, StarRate } from '@mui/icons-material';
import AdminLayout from '../../components/layout/AdminLayout';
import { BadgeService } from '../../api/services';
import { useLoading } from '../../contexts/LoadingContext';
import type { Badge } from '../../types/api';

/**
 * Badges management page component
 * Allows admins to view, create, edit, and manage badges
 */
const BadgesPage: React.FC = () => {
  // State for badges data
  const [badges, setBadges] = useState<Badge[]>([]);
  
  // State for badge edit modal
  const [selectedBadge, setSelectedBadge] = useState<Badge | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [badgeFormData, setBadgeFormData] = useState<Partial<Badge>>({});
  
  // Error handling state
  const [error, setError] = useState<string | null>(null);
  
  // Loading context for managing loading states
  const { setLoading, setLoadingMessage } = useLoading();

  // Badge categories
  const badgeCategories = ['events', 'social', 'achievements', 'special'];

  /**
   * Fetch badges data from API
   */
  const fetchBadges = async () => {
    try {
      setLoading(true);
      setLoadingMessage('Loading badges...');
      setError(null);
      
      const response = await BadgeService.getBadges();
      
      if (response && Array.isArray(response)) {
        setBadges(response);
      } else {
        setError('Failed to fetch badges data');
        setBadges([]);
      }
    } catch (err) {
      setError('An error occurred while fetching badges data');
      console.error('Error fetching badges:', err);
      setBadges([]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Open edit modal for a badge
   */
  const handleEditBadge = (badge: Badge) => {
    setSelectedBadge(badge);
    setBadgeFormData({
      name: badge.name,
      description: badge.description,
      category: badge.category,
      level: badge.level,
      requirements: badge.requirements,
      points_reward: badge.points_reward,
      icon_url: badge.icon_url
    });
    setIsEditModalOpen(true);
  };

  
  /**
   * Handle form changes for all field types
   */
  const handleFormChange = (event: any) => {
    const name = event.target.name;
    const value = event.target.value;
    
    setBadgeFormData({
      ...badgeFormData,
      [name]: value
    });
  };

  /**
   * Submit badge edit form
   */
  const handleSubmitBadgeEdit = async () => {
    // This would connect to your backend API
    // For now, we'll just update the local state for demo purposes
    try {
      setLoading(true);
      setLoadingMessage(selectedBadge ? 'Updating badge...' : 'Creating badge...');
      
      // In a real implementation, you would call your API here
      // const result = await BadgeService.updateBadge(selectedBadge.id, badgeFormData);
      
      // For demo purposes, just update the UI
      if (selectedBadge) {
        const updatedBadges = badges.map(badge => 
          badge.id === selectedBadge.id 
            ? { ...badge, ...badgeFormData as Badge } 
            : badge
        );
        setBadges(updatedBadges);
      } else {
        // Creating a new badge (in real app, you'd get the ID from the API)
        const { id, ...formDataWithoutId } = badgeFormData as Badge;
        const newBadge: Badge = {
          id: `temp-${Date.now()}`,
          ...formDataWithoutId
        };
        setBadges([...badges, newBadge]);
      }
      
      setIsEditModalOpen(false);
      setSelectedBadge(null);
    } catch (err) {
      setError(`An error occurred while ${selectedBadge ? 'updating' : 'creating'} badge`);
      console.error(`Error ${selectedBadge ? 'updating' : 'creating'} badge:`, err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Render stars for badge level
   */
  const renderLevelStars = (level: number) => {
    return Array(level).fill(0).map((_, index) => (
      <StarRate key={index} fontSize="small" color="primary" />
    ));
  };

  // Fetch badges on component mount
  useEffect(() => {
    fetchBadges();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /**
   * Group badges by category
   */
  const badgesByCategory = badges.reduce((acc, badge) => {
    const category = badge.category || 'other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(badge);
    return acc;
  }, {} as Record<string, Badge[]>);

  return (
    <AdminLayout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Badges Management
          </Typography>
          <Button 
            variant="contained" 
            startIcon={<Add />}
            onClick={() => {
              setSelectedBadge(null);
              setBadgeFormData({
                level: 1,
                points_reward: 100,
                category: 'events'
              });
              setIsEditModalOpen(true);
            }}
          >
            Create Badge
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {badges.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
            <CircularProgress />
          </Box>
        ) : (
          Object.entries(badgesByCategory).map(([category, categoryBadges]) => (
            <Box key={category} sx={{ mb: 4 }}>
              <Typography variant="h5" sx={{ mb: 2, textTransform: 'capitalize' }}>
                {category} Badges
              </Typography>
              
              <Grid container spacing={3}>
                {categoryBadges.map((badge) => (
                  <Grid key={badge.id} sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 4', lg: 'span 3' } }}>
                    <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                      {badge.icon_url ? (
                        <CardMedia
                          component="img"
                          height="140"
                          image={badge.icon_url}
                          alt={badge.name}
                          sx={{ objectFit: 'contain', p: 2, backgroundColor: '#f5f5f5' }}
                        />
                      ) : (
                        <Box
                          sx={{
                            height: 140,
                            backgroundColor: '#f5f5f5',
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center'
                          }}
                        >
                          <Typography color="textSecondary">No Image</Typography>
                        </Box>
                      )}
                      
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="h6" component="div">
                            {badge.name}
                          </Typography>
                          <Chip 
                            label={`Level ${badge.level}`}
                            size="small"
                            color="primary"
                          />
                        </Box>
                        
                        <Box sx={{ mb: 1 }}>
                          {renderLevelStars(badge.level)}
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {badge.description}
                        </Typography>
                        
                        <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                          Requirements:
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {badge.requirements}
                        </Typography>
                        
                        <Chip 
                          label={`${badge.points_reward} Points`}
                          size="small"
                          color="secondary"
                          sx={{ mt: 1 }}
                        />
                      </CardContent>
                      
                      <CardActions>
                        <Button 
                          size="small" 
                          startIcon={<Edit />}
                          onClick={() => handleEditBadge(badge)}
                        >
                          Edit
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          ))
        )}

        {/* Badge Edit Dialog */}
        <Dialog open={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>
            {selectedBadge ? 'Edit Badge' : 'Create New Badge'}
          </DialogTitle>
          <DialogContent dividers>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
              <TextField
                label="Badge Name"
                name="name"
                value={badgeFormData.name || ''}
                onChange={handleFormChange}
                fullWidth
                variant="outlined"
                required
              />
              
              <TextField
                label="Description"
                name="description"
                value={badgeFormData.description || ''}
                onChange={handleFormChange}
                fullWidth
                variant="outlined"
                required
                multiline
                rows={2}
              />
              
              <FormControl fullWidth required>
                <InputLabel id="category-label">Category</InputLabel>
                <Select
                  labelId="category-label"
                  name="category"
                  value={badgeFormData.category || ''}
                  onChange={handleFormChange}
                  label="Category"
                >
                  {badgeCategories.map((category) => (
                    <MenuItem key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <TextField
                label="Level (1-5)"
                name="level"
                type="number"
                value={badgeFormData.level || ''}
                onChange={handleFormChange}
                fullWidth
                variant="outlined"
                required
                inputProps={{ min: 1, max: 5 }}
              />
              
              <TextField
                label="Requirements"
                name="requirements"
                value={badgeFormData.requirements || ''}
                onChange={handleFormChange}
                fullWidth
                variant="outlined"
                required
                multiline
                rows={3}
              />
              
              <TextField
                label="Points Reward"
                name="points_reward"
                type="number"
                value={badgeFormData.points_reward || ''}
                onChange={handleFormChange}
                fullWidth
                variant="outlined"
                required
                inputProps={{ min: 0 }}
              />
              
              <TextField
                label="Icon URL"
                name="icon_url"
                value={badgeFormData.icon_url || ''}
                onChange={handleFormChange}
                fullWidth
                variant="outlined"
                placeholder="https://example.com/badge-icon.png"
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditModalOpen(false)}>Cancel</Button>
            <Button 
              onClick={handleSubmitBadgeEdit} 
              variant="contained" 
              color="primary"
            >
              {selectedBadge ? 'Update Badge' : 'Create Badge'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </AdminLayout>
  );
};

export default BadgesPage;
