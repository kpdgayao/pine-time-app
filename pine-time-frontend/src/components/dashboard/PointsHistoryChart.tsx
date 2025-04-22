import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  ToggleButtonGroup, 
  ToggleButton,
  useTheme 
} from '@mui/material';

// Note: In a real implementation, you would import a charting library like Chart.js or Recharts
// For this example, we'll create a simplified visualization

interface PointsData {
  date: string;
  points: number;
}

interface PointsHistoryChartProps {
  data: PointsData[];
  loading?: boolean;
}

const PointsHistoryChart: React.FC<PointsHistoryChartProps> = ({ 
  data,
  loading = false
}) => {
  const theme = useTheme();
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'year'>('month');
  const [chartData, setChartData] = useState<PointsData[]>([]);
  
  // Filter data based on selected time range
  useEffect(() => {
    if (!data || data.length === 0) {
      setChartData([]);
      return;
    }
    
    const now = new Date();
    let filterDate = new Date();
    
    switch (timeRange) {
      case 'week':
        filterDate.setDate(now.getDate() - 7);
        break;
      case 'month':
        filterDate.setMonth(now.getMonth() - 1);
        break;
      case 'year':
        filterDate.setFullYear(now.getFullYear() - 1);
        break;
    }
    
    const filtered = data.filter(item => new Date(item.date) >= filterDate);
    setChartData(filtered);
  }, [data, timeRange]);
  
  // Calculate total points in the selected period
  const totalPoints = chartData.reduce((sum, item) => sum + item.points, 0);
  
  // Find max points for scaling the chart
  const maxPoints = Math.max(...chartData.map(item => item.points), 1);
  
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
          Points History
        </Typography>
        <ToggleButtonGroup
          size="small"
          value={timeRange}
          exclusive
          onChange={(_, newValue) => {
            if (newValue) setTimeRange(newValue);
          }}
          aria-label="time range"
        >
          <ToggleButton value="week" aria-label="week">
            Week
          </ToggleButton>
          <ToggleButton value="month" aria-label="month">
            Month
          </ToggleButton>
          <ToggleButton value="year" aria-label="year">
            Year
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Total points in this period:
        </Typography>
        <Typography variant="body1" fontWeight="bold" color="primary">
          {totalPoints} points
        </Typography>
      </Box>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4, flex: 1 }}>
          <Typography color="text.secondary">Loading chart data...</Typography>
        </Box>
      ) : chartData.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4, flex: 1 }}>
          <Typography color="text.secondary">No data available for this period</Typography>
        </Box>
      ) : (
        <Box sx={{ height: 200, mt: 2, position: 'relative', flex: 1 }}>
          {/* X-axis labels */}
          <Box sx={{ 
            position: 'absolute', 
            bottom: 0, 
            left: 0, 
            right: 0, 
            height: 20,
            display: 'flex',
            justifyContent: 'space-between'
          }}>
            {chartData.slice(0, 10).map((item, index) => (
              <Typography 
                key={index} 
                variant="caption" 
                sx={{ 
                  transform: 'rotate(-45deg)',
                  transformOrigin: 'top left',
                  width: 20,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}
              >
                {new Date(item.date).toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric' 
                })}
              </Typography>
            ))}
          </Box>
          
          {/* Y-axis */}
          <Box sx={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            bottom: 20, 
            width: 30,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            alignItems: 'flex-end',
            pr: 0.5
          }}>
            <Typography variant="caption">{maxPoints}</Typography>
            <Typography variant="caption">{Math.floor(maxPoints / 2)}</Typography>
            <Typography variant="caption">0</Typography>
          </Box>
          
          {/* Chart area */}
          <Box sx={{ 
            position: 'absolute', 
            top: 0, 
            left: 30, 
            right: 0, 
            bottom: 20,
            display: 'flex',
            alignItems: 'flex-end',
            gap: '2px'
          }}>
            {chartData.slice(0, 10).map((item, index) => (
              <Box 
                key={index}
                sx={{
                  flex: 1,
                  height: `${(item.points / maxPoints) * 100}%`,
                  backgroundColor: theme.palette.primary.main,
                  borderTopLeftRadius: 4,
                  borderTopRightRadius: 4,
                  transition: 'height 0.5s ease-in-out',
                  position: 'relative',
                  '&:hover': {
                    backgroundColor: theme.palette.primary.dark,
                    '& .tooltip': {
                      display: 'block'
                    }
                  }
                }}
              >
                <Box 
                  className="tooltip"
                  sx={{
                    display: 'none',
                    position: 'absolute',
                    top: -28,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    color: 'white',
                    padding: '2px 6px',
                    borderRadius: 1,
                    fontSize: '0.75rem',
                    whiteSpace: 'nowrap',
                    zIndex: 1
                  }}
                >
                  {item.points} points
                </Box>
              </Box>
            ))}
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default PointsHistoryChart;
