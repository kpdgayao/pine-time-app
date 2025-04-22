import React from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Button
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import BadgeProgressBar from '../BadgeProgressBar';
import { Badge } from '../../types/badges';

interface BadgeProgressSectionProps {
  badges: Badge[];
  loading?: boolean;
}

const BadgeProgressSection: React.FC<BadgeProgressSectionProps> = ({ 
  badges,
  loading = false
}) => {
  const navigate = useNavigate();

  // Sort badges by progress percentage (highest first)
  const sortedBadges = [...badges].sort((a, b) => {
    const aPercentage = a.next_level_threshold ? (a.progress || 0) / a.next_level_threshold : 1;
    const bPercentage = b.next_level_threshold ? (b.progress || 0) / b.next_level_threshold : 1;
    return bPercentage - aPercentage;
  });

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
          Badge Progress
        </Typography>
        <Button 
          size="small" 
          color="primary" 
          onClick={() => navigate('/badges')}
        >
          View All
        </Button>
      </Box>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <Typography color="text.secondary">Loading badges...</Typography>
        </Box>
      ) : badges.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <Typography color="text.secondary">No badges yet</Typography>
        </Box>
      ) : (
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {sortedBadges.slice(0, 4).map((badge) => (
              <Box key={badge.id}>
                <BadgeProgressBar badge={badge} />
              </Box>
            ))}
          </Box>
          
          {badges.length > 4 && (
            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Button 
                variant="text" 
                color="primary"
                onClick={() => navigate('/badges')}
              >
                See {badges.length - 4} more badges
              </Button>
            </Box>
          )}
        </Box>
      )}
    </Paper>
  );
};

export default BadgeProgressSection;
