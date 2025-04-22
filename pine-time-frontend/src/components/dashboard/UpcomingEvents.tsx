import React from 'react';
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
  useTheme 
} from '@mui/material';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import { Event } from '../../types/events';
import { useNavigate } from 'react-router-dom';

interface UpcomingEventsProps {
  events: Event[];
  loading?: boolean;
}

const UpcomingEvents: React.FC<UpcomingEventsProps> = ({ 
  events,
  loading = false
}) => {
  const theme = useTheme();
  const navigate = useNavigate();

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

  return (
    <Paper 
      elevation={1} 
      sx={{ 
        p: 2, 
        borderRadius: 2,
        height: '100%',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" fontWeight="bold" color="primary">
          Upcoming Events
        </Typography>
        <Button 
          size="small" 
          color="primary" 
          onClick={() => navigate('/events')}
        >
          View All
        </Button>
      </Box>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <Typography color="text.secondary">Loading events...</Typography>
        </Box>
      ) : events.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <Typography color="text.secondary">No upcoming events</Typography>
        </Box>
      ) : (
        <Stack spacing={2} sx={{ overflow: 'auto' }}>
          {events.map((event) => (
            <Card 
              key={event.id} 
              sx={{ 
                display: 'flex', 
                borderRadius: 2,
                overflow: 'hidden',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: theme.shadows[3],
                }
              }}
            >
              <CardMedia
                component="img"
                sx={{ width: 100, height: '100%', objectFit: 'cover' }}
                image={event.image_url || '/default-event.jpg'}
                alt={event.title}
              />
              <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                <CardContent sx={{ flex: '1 0 auto', py: 1.5 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Typography component="div" variant="subtitle1" fontWeight="bold">
                      {event.title}
                    </Typography>
                    <Chip 
                      label={`${event.points_reward} pts`} 
                      size="small" 
                      color="secondary"
                      sx={{ ml: 1 }}
                    />
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, color: 'text.secondary' }}>
                    <CalendarTodayIcon fontSize="small" sx={{ mr: 0.5 }} />
                    <Typography variant="body2" color="text.secondary">
                      {formatDate(event.start_time)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5, color: 'text.secondary' }}>
                    <LocationOnIcon fontSize="small" sx={{ mr: 0.5 }} />
                    <Typography variant="body2" color="text.secondary">
                      {event.location}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                    <Button 
                      size="small" 
                      variant="outlined" 
                      onClick={() => navigate(`/events/${event.id}`)}
                    >
                      Details
                    </Button>
                  </Box>
                </CardContent>
              </Box>
            </Card>
          ))}
        </Stack>
      )}
    </Paper>
  );
};

export default UpcomingEvents;
