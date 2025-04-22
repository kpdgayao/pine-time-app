import React from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  Divider,
  useTheme 
} from '@mui/material';
import EventIcon from '@mui/icons-material/Event';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import RemoveCircleIcon from '@mui/icons-material/RemoveCircle';
import { RecentActivity } from '../../types/badges';

interface RecentActivitiesProps {
  activities: RecentActivity[];
  loading?: boolean;
}

const RecentActivities: React.FC<RecentActivitiesProps> = ({ 
  activities,
  loading = false
}) => {
  const theme = useTheme();

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'event_registration':
        return <EventIcon color="primary" />;
      case 'badge_earned':
        return <EmojiEventsIcon sx={{ color: theme.palette.secondary.main }} />;
      case 'points_earned':
        return <AddCircleIcon sx={{ color: theme.palette.success.main }} />;
      case 'points_redeemed':
        return <RemoveCircleIcon sx={{ color: theme.palette.error.main }} />;
      default:
        return <EventIcon color="primary" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) {
      return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    }
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
      <Typography variant="h6" fontWeight="bold" color="primary" sx={{ mb: 2 }}>
        Recent Activities
      </Typography>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <Typography color="text.secondary">Loading activities...</Typography>
        </Box>
      ) : activities.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <Typography color="text.secondary">No recent activities</Typography>
        </Box>
      ) : (
        <List sx={{ width: '100%', flex: 1, overflow: 'auto' }}>
          {activities.map((activity, index) => (
            <React.Fragment key={activity.id}>
              <ListItem alignItems="flex-start" sx={{ px: 1 }}>
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {getActivityIcon(activity.activity_type)}
                </ListItemIcon>
                <ListItemText
                  primary={activity.description}
                  secondary={formatDate(activity.timestamp)}
                  primaryTypographyProps={{ 
                    variant: 'body1',
                    fontWeight: 'medium'
                  }}
                  secondaryTypographyProps={{ 
                    variant: 'body2',
                    color: 'text.secondary'
                  }}
                />
                {activity.points && (
                  <Box 
                    sx={{ 
                      ml: 2, 
                      color: activity.activity_type === 'points_earned' 
                        ? 'success.main' 
                        : 'error.main',
                      fontWeight: 'bold'
                    }}
                  >
                    {activity.activity_type === 'points_earned' ? '+' : '-'}{activity.points} pts
                  </Box>
                )}
              </ListItem>
              {index < activities.length - 1 && (
                <Divider variant="inset" component="li" />
              )}
            </React.Fragment>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default RecentActivities;
