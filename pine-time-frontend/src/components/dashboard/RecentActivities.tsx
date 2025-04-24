import React, { useMemo } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  Divider,
  useTheme,
  Chip
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

  // Group similar activities that occur on the same day
  const groupedActivities = useMemo(() => {
    if (!activities || activities.length === 0) return [];
    
    // Sort activities by timestamp (newest first)
    const sortedActivities = [...activities].sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
    
    const grouped: {
      key: string;
      activities: typeof activities;
      count: number;
      date: string;
      displayActivity: typeof activities[0];
    }[] = [];
    
    // Helper function to get date string for grouping (YYYY-MM-DD)
    const getDateString = (timestamp: string) => {
      const date = new Date(timestamp);
      return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
    };
    
    // Helper function to create a key for similar activities
    const createGroupKey = (activity: typeof activities[0]) => {
      // For event registrations, group by event_id and activity_type
      if (activity.activity_type === 'event_registration' && activity.event_id) {
        return `${activity.activity_type}_${activity.event_id}_${getDateString(activity.timestamp)}`;
      }
      
      // For badge earned, group by badge_id and activity_type
      if (activity.activity_type === 'badge_earned' && activity.badge_id) {
        return `${activity.activity_type}_${activity.badge_id}_${getDateString(activity.timestamp)}`;
      }
      
      // For points, group by activity_type and points amount on the same day
      if ((activity.activity_type === 'points_earned' || activity.activity_type === 'points_redeemed') && 
          activity.points !== undefined) {
        return `${activity.activity_type}_${activity.points}_${getDateString(activity.timestamp)}`;
      }
      
      // Default case - use the activity id as the key (no grouping)
      return `${activity.id}`;
    };
    
    // Group the activities
    sortedActivities.forEach(activity => {
      const key = createGroupKey(activity);
      const existingGroup = grouped.find(g => g.key === key);
      
      if (existingGroup) {
        existingGroup.activities.push(activity);
        existingGroup.count += 1;
      } else {
        grouped.push({
          key,
          activities: [activity],
          count: 1,
          date: activity.timestamp,
          displayActivity: activity
        });
      }
    });
    
    return grouped;
  }, [activities]);

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
          {groupedActivities.map((group, index) => (
            <React.Fragment key={group.key}>
              <ListItem alignItems="flex-start" sx={{ px: 1 }}>
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {getActivityIcon(group.displayActivity.activity_type)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body1" fontWeight="medium">
                        {group.displayActivity.description}
                      </Typography>
                      {group.count > 1 && (
                        <Chip 
                          size="small" 
                          label={`${group.count}x`} 
                          sx={{ ml: 1, height: 20, fontSize: '0.7rem' }}
                        />
                      )}
                    </Box>
                  }
                  secondary={formatDate(group.displayActivity.timestamp)}
                  secondaryTypographyProps={{ 
                    variant: 'body2',
                    color: 'text.secondary'
                  }}
                />
                {group.displayActivity.points && (
                  <Box 
                    sx={{ 
                      ml: 2, 
                      color: group.displayActivity.activity_type === 'points_earned' 
                        ? 'success.main' 
                        : 'error.main',
                      fontWeight: 'bold',
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    <Chip
                      size="small"
                      color={group.displayActivity.activity_type === 'points_earned' ? 'success' : 'error'}
                      label={`${group.displayActivity.activity_type === 'points_earned' ? '+' : '-'}${group.displayActivity.points} pts${group.count > 1 ? ` × ${group.count}` : ''}`}
                      sx={{ fontWeight: 'bold' }}
                    />
                  </Box>
                )}
              </ListItem>
              {index < groupedActivities.length - 1 && (
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
