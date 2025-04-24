import React, { useState } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Card, 
  CardContent, 
  CardMedia, 
  Button, 
  Chip,
  Stack,
  useTheme,
  alpha,
  Collapse,
  IconButton,
  Tooltip,
  Divider,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Fade
} from '@mui/material';
import RecommendIcon from '@mui/icons-material/Recommend';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FilterListIcon from '@mui/icons-material/FilterList';
import SortIcon from '@mui/icons-material/Sort';
import CategoryIcon from '@mui/icons-material/Category';
import StarIcon from '@mui/icons-material/Star';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { Event } from '../../types/events';
import { useNavigate } from 'react-router-dom';

interface EventRecommendationsProps {
  events: Event[];
  loading?: boolean;
  fullWidth?: boolean;
}

const EventRecommendations: React.FC<EventRecommendationsProps> = ({ 
  events,
  loading = false,
  fullWidth = false
}) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(null);
  const [sortAnchorEl, setSortAnchorEl] = useState<null | HTMLElement>(null);
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [activeSort, setActiveSort] = useState<string>('recommended');
  
  // Pine Time green theme color
  const pineTimeGreen = '#2E7D32';
  
  // Handle expand/collapse for recommendation reason
  const handleExpandClick = (eventId: number) => {
    setExpandedId(expandedId === eventId ? null : eventId);
  };
  
  // Handle filter menu
  const handleFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setFilterAnchorEl(event.currentTarget);
  };
  
  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };
  
  const handleFilterSelect = (filter: string) => {
    setActiveFilter(filter);
    handleFilterClose();
  };
  
  // Handle sort menu
  const handleSortClick = (event: React.MouseEvent<HTMLElement>) => {
    setSortAnchorEl(event.currentTarget);
  };
  
  const handleSortClose = () => {
    setSortAnchorEl(null);
  };
  
  const handleSortSelect = (sort: string) => {
    setActiveSort(sort);
    handleSortClose();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short',
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  // Generate recommendation reason based on event and user history
  const getRecommendationReason = (event: Event) => {
    // In a real implementation, this would use the actual recommendation reason from the API
    // For now, we'll generate some sample reasons based on the event properties
    
    const reasons = [
      { 
        type: 'category',
        text: `Based on your interest in ${event.category || 'this category'} events`,
        icon: <CategoryIcon fontSize="small" sx={{ color: theme.palette.info.main }} />
      },
      { 
        type: 'popular',
        text: 'Popular among users with similar interests',
        icon: <StarIcon fontSize="small" sx={{ color: theme.palette.warning.main }} />
      },
      { 
        type: 'time',
        text: 'Fits your usual attendance schedule',
        icon: <AccessTimeIcon fontSize="small" sx={{ color: theme.palette.success.main }} />
      },
      { 
        type: 'streak',
        text: 'Will help maintain your attendance streak',
        icon: <LocalFireDepartmentIcon fontSize="small" sx={{ color: theme.palette.error.main }} />
      }
    ];
    
    // Select 1-2 random reasons
    const numReasons = Math.floor(Math.random() * 2) + 1;
    const shuffled = [...reasons].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, numReasons);
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: { xs: 2, md: 3 }, 
        borderRadius: 2,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: `linear-gradient(135deg, ${alpha(theme.palette.secondary.main, 0.05)} 0%, ${alpha(theme.palette.secondary.main, 0.02)} 100%)`,
        borderTop: `4px solid ${theme.palette.secondary.main}`,
        position: 'relative',
        overflow: 'visible',
        width: fullWidth ? '100%' : 'auto',
        boxShadow: `0 6px 20px ${alpha(theme.palette.secondary.main, 0.15)}`
      }}
    >
      {/* Decorative elements */}
      <Box 
        sx={{ 
          position: 'absolute', 
          top: -15, 
          right: 20, 
          width: 30, 
          height: 30, 
          borderRadius: '50%',
          backgroundColor: theme.palette.secondary.main,
          boxShadow: `0 0 10px ${theme.palette.secondary.main}`,
          opacity: 0.7,
          zIndex: 1
        }} 
      />
      <Box 
        sx={{ 
          position: 'absolute', 
          top: 10, 
          right: 40, 
          width: 15, 
          height: 15, 
          borderRadius: '50%',
          backgroundColor: theme.palette.secondary.light,
          opacity: 0.5,
          zIndex: 1
        }} 
      />
      
      {/* Header with title and filter/sort options */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 2,
        flexWrap: 'wrap',
        gap: 1
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <RecommendIcon sx={{ 
            color: theme.palette.secondary.main, 
            mr: 1,
            fontSize: 28,
            filter: `drop-shadow(0 2px 3px ${alpha(theme.palette.secondary.main, 0.3)})`
          }} />
          <Typography 
            variant="h5" 
            fontWeight="bold" 
            sx={{ 
              background: `linear-gradient(90deg, ${theme.palette.secondary.main}, ${theme.palette.secondary.dark})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textShadow: `0 2px 4px ${alpha(theme.palette.secondary.main, 0.2)}`
            }}
          >
            Recommended For You
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Filter events">
            <Button
              size="small"
              startIcon={<FilterListIcon />}
              onClick={handleFilterClick}
              color="secondary"
              variant="outlined"
              sx={{ 
                borderRadius: 4,
                textTransform: 'none',
                px: 1.5
              }}
            >
              {activeFilter === 'all' ? 'All' : activeFilter}
            </Button>
          </Tooltip>
          
          <Tooltip title="Sort events">
            <Button
              size="small"
              startIcon={<SortIcon />}
              onClick={handleSortClick}
              color="secondary"
              variant="outlined"
              sx={{ 
                borderRadius: 4,
                textTransform: 'none',
                px: 1.5
              }}
            >
              {activeSort === 'recommended' ? 'Best Match' : activeSort}
            </Button>
          </Tooltip>
          
          {/* Filter Menu */}
          <Menu
            anchorEl={filterAnchorEl}
            open={Boolean(filterAnchorEl)}
            onClose={handleFilterClose}
            TransitionComponent={Fade}
          >
            <MenuItem onClick={() => handleFilterSelect('all')} selected={activeFilter === 'all'}>
              <ListItemText>All</ListItemText>
            </MenuItem>
            <MenuItem onClick={() => handleFilterSelect('Trivia')} selected={activeFilter === 'Trivia'}>
              <ListItemIcon>
                <CategoryIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Trivia</ListItemText>
            </MenuItem>
            <MenuItem onClick={() => handleFilterSelect('Game Night')} selected={activeFilter === 'Game Night'}>
              <ListItemIcon>
                <CategoryIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Game Night</ListItemText>
            </MenuItem>
            <MenuItem onClick={() => handleFilterSelect('Mystery')} selected={activeFilter === 'Mystery'}>
              <ListItemIcon>
                <CategoryIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Mystery</ListItemText>
            </MenuItem>
          </Menu>
          
          {/* Sort Menu */}
          <Menu
            anchorEl={sortAnchorEl}
            open={Boolean(sortAnchorEl)}
            onClose={handleSortClose}
            TransitionComponent={Fade}
          >
            <MenuItem onClick={() => handleSortSelect('recommended')} selected={activeSort === 'recommended'}>
              <ListItemIcon>
                <RecommendIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Best Match</ListItemText>
            </MenuItem>
            <MenuItem onClick={() => handleSortSelect('date')} selected={activeSort === 'date'}>
              <ListItemIcon>
                <CalendarTodayIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Date</ListItemText>
            </MenuItem>
            <MenuItem onClick={() => handleSortSelect('points')} selected={activeSort === 'points'}>
              <ListItemIcon>
                <StarIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Points</ListItemText>
            </MenuItem>
          </Menu>
        </Box>
      </Box>
      
      <Typography 
        variant="body1" 
        color="text.secondary" 
        sx={{ 
          mb: 3,
          fontStyle: 'italic',
          display: 'flex',
          alignItems: 'center',
          gap: 0.5
        }}
      >
        <InfoOutlinedIcon fontSize="small" />
        Personalized recommendations based on your activity and preferences
      </Typography>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <Typography color="text.secondary">Finding recommendations...</Typography>
        </Box>
      ) : events.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <Typography color="text.secondary">No recommendations available</Typography>
        </Box>
      ) : (
        <Stack spacing={2.5} sx={{ overflow: 'auto' }}>
          {events.map((event, index) => {
            // Get recommendation reasons for this event
            const reasons = getRecommendationReason(event);
            
            return (
              <Card 
                key={`recommendation-${event.id}-${index}`} 
                sx={{ 
                  display: 'flex', 
                  flexDirection: { xs: 'column', sm: 'row' },
                  borderRadius: 2,
                  overflow: 'hidden',
                  transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
                  boxShadow: expandedId === event.id ? 
                    `0 10px 20px ${alpha(theme.palette.secondary.main, 0.2)}` : 
                    `0 3px 10px ${alpha(theme.palette.secondary.main, 0.1)}`,
                  transform: expandedId === event.id ? 'scale(1.02)' : 'scale(1)',
                  '&:hover': {
                    transform: 'translateY(-3px)',
                    boxShadow: `0 8px 15px ${alpha(theme.palette.secondary.main, 0.15)}`,
                  },
                  position: 'relative',
                  zIndex: expandedId === event.id ? 2 : 1
                }}
              >
                <CardMedia
                  component="img"
                  sx={{ 
                    width: { xs: '100%', sm: 150 }, 
                    height: { xs: 140, sm: '100%' }, 
                    objectFit: 'cover'
                  }}
                  image={event.image_url || '/default-event.jpg'}
                  alt={event.title}
                />
                <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                  <CardContent sx={{ flex: '1 0 auto', py: 2, px: { xs: 2, md: 3 } }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography 
                        component="div" 
                        variant="h6" 
                        fontWeight="bold"
                        sx={{ 
                          color: theme.palette.text.primary,
                          transition: 'color 0.2s ease',
                          '&:hover': {
                            color: theme.palette.secondary.main,
                            cursor: 'pointer'
                          }
                        }}
                        onClick={() => navigate(`/events/${event.id}`)}
                      >
                        {event.title}
                      </Typography>
                      <Chip 
                        label={`${event.points_reward} pts`} 
                        size="small" 
                        color="secondary"
                        sx={{ 
                          ml: 1,
                          fontWeight: 'bold',
                          boxShadow: `0 2px 4px ${alpha(theme.palette.secondary.main, 0.2)}`,
                          background: `linear-gradient(90deg, ${theme.palette.secondary.main}, ${theme.palette.secondary.dark})`,
                        }}
                      />
                    </Box>
                    
                    {/* Event details */}
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: { xs: 0.5, md: 2 } }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', color: 'text.secondary', mr: 2 }}>
                        <CalendarTodayIcon fontSize="small" sx={{ mr: 0.5 }} />
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(event.start_time)}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', color: 'text.secondary' }}>
                        <LocationOnIcon fontSize="small" sx={{ mr: 0.5 }} />
                        <Typography variant="body2" color="text.secondary">
                          {event.location}
                        </Typography>
                      </Box>
                    </Box>
                    
                    {/* Event description preview */}
                    <Typography 
                      variant="body2" 
                      color="text.secondary" 
                      sx={{ 
                        mt: 1.5, 
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        lineHeight: 1.4
                      }}
                    >
                      {event.description}
                    </Typography>
                    
                    {/* Recommendation reason chip */}
                    <Box sx={{ display: 'flex', mt: 2, mb: 1, flexWrap: 'wrap', gap: 1 }}>
                      {reasons.map((reason, idx) => (
                        <Chip
                          key={`reason-${event.id}-${idx}`}
                          icon={reason.icon}
                          label={reason.text}
                          size="small"
                          variant="outlined"
                          color="secondary"
                          sx={{ 
                            borderRadius: 4,
                            backgroundColor: alpha(theme.palette.secondary.main, 0.05),
                            '& .MuiChip-label': {
                              px: 1
                            }
                          }}
                        />
                      ))}
                      
                      <IconButton
                        onClick={() => handleExpandClick(event.id)}
                        aria-expanded={expandedId === event.id}
                        aria-label="show more"
                        size="small"
                        sx={{
                          ml: 'auto',
                          transform: expandedId === event.id ? 'rotate(180deg)' : 'rotate(0deg)',
                          transition: 'transform 0.3s',
                          color: theme.palette.secondary.main
                        }}
                      >
                        <ExpandMoreIcon />
                      </IconButton>
                    </Box>
                    
                    {/* Expanded recommendation details */}
                    <Collapse in={expandedId === event.id} timeout="auto" unmountOnExit>
                      <Box sx={{ mt: 1, mb: 2 }}>
                        <Divider sx={{ mb: 2 }} />
                        <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                          Why we think you'll like this event:
                        </Typography>
                        <Box component="ul" sx={{ pl: 2, mt: 1, mb: 2 }}>
                          <Typography component="li" variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            This event matches your preferred categories and interests
                          </Typography>
                          <Typography component="li" variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            You've attended similar events in the past with high ratings
                          </Typography>
                          <Typography component="li" variant="body2" color="text.secondary">
                            Users with similar preferences have enjoyed this event type
                          </Typography>
                        </Box>
                      </Box>
                    </Collapse>
                    
                    {/* Action buttons */}
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1, gap: 1 }}>
                      <Button 
                        size="small" 
                        variant="outlined" 
                        color="secondary"
                        onClick={() => navigate(`/events/${event.id}`)}
                        sx={{ 
                          borderRadius: 6,
                          px: 2
                        }}
                      >
                        Details
                      </Button>
                      <Button 
                        size="small" 
                        variant="contained" 
                        color="secondary"
                        onClick={() => navigate(`/events/${event.id}`)}
                        sx={{ 
                          borderRadius: 6,
                          px: 2,
                          boxShadow: `0 2px 8px ${alpha(theme.palette.secondary.main, 0.3)}`,
                          background: `linear-gradient(90deg, ${theme.palette.secondary.main}, ${theme.palette.secondary.dark})`,
                          '&:hover': {
                            boxShadow: `0 4px 12px ${alpha(theme.palette.secondary.main, 0.4)}`,
                          }
                        }}
                      >
                        Register
                      </Button>
                    </Box>
                  </CardContent>
                </Box>
              </Card>
            );
          })}
        </Stack>
      )}
    </Paper>
  );
};

export default EventRecommendations;
