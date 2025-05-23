import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Paper, 
  Typography, 
  Card, 
  CardContent, 
  Alert,
  Skeleton,
  Divider
} from '@mui/material';
import {
  PeopleAlt as UsersIcon,
  Event as EventsIcon,
  AppRegistration as RegistrationsIcon,
  EmojiEvents as BadgesIcon,
  StarRate as PointsIcon
} from '@mui/icons-material';
import AdminLayout from '../../components/layout/AdminLayout';
import api from '../../api/client';
import { safeApiCall, extractItems } from '../../utils/api';
import { DEFAULT_TIMEOUT } from '../../config';

/**
 * Types for dashboard data
 */
interface DashboardMetricsResponse {
  users_count: number;
  previous_users_count: number;
  active_events_count: number;
  previous_active_events_count: number;
  registrations_count: number;
  previous_registrations_count: number;
  badges_awarded_count: number;
  previous_badges_awarded_count: number;
  total_points: number;
  previous_total_points: number;
}

interface DashboardMetric {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  previousValue?: number;
}

interface RecentActivity {
  id: string;
  type: string;
  user: string;
  action: string;
  timestamp: string;
  details?: string;
}

/**
 * DashboardPage component displays key metrics and recent activities
 * for the Pine Time admin dashboard.
 */
const DashboardPage: React.FC = () => {
  // State for dashboard data
  const [metrics, setMetrics] = useState<DashboardMetric[]>([]);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch dashboard data on mount
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch metrics data with timeout and error handling
        const metricsResponse = await safeApiCall<DashboardMetricsResponse>(
          Promise.race([
            api.get<DashboardMetricsResponse>('/admin/dashboard/metrics'),
            new Promise((_, reject) => 
              setTimeout(() => reject(new Error('Request timed out')), DEFAULT_TIMEOUT)
            )
          ]),
          // Default fallback metrics for development/demo
          {
            users_count: 125,
            previous_users_count: 110,
            active_events_count: 8,
            previous_active_events_count: 5,
            registrations_count: 89,
            previous_registrations_count: 75,
            badges_awarded_count: 42,
            previous_badges_awarded_count: 35,
            total_points: 12450,
            previous_total_points: 10200
          }
        );

        // Check if API response is valid
        if (!metricsResponse) {
          throw new Error('Failed to fetch dashboard metrics');
        }

        // Format metrics data with consistent icons and colors
        const formattedMetrics: DashboardMetric[] = [
          {
            label: 'Total Users',
            value: metricsResponse.users_count || 0,
            icon: <UsersIcon />,
            color: '#2E7D32', // Pine Time green
            previousValue: metricsResponse.previous_users_count
          },
          {
            label: 'Active Events',
            value: metricsResponse.active_events_count || 0,
            icon: <EventsIcon />,
            color: '#F57C00', // Orange
            previousValue: metricsResponse.previous_active_events_count
          },
          {
            label: 'Total Registrations',
            value: metricsResponse.registrations_count || 0,
            icon: <RegistrationsIcon />,
            color: '#1976D2', // Blue
            previousValue: metricsResponse.previous_registrations_count
          },
          {
            label: 'Badges Awarded',
            value: metricsResponse.badges_awarded_count || 0,
            icon: <BadgesIcon />,
            color: '#7B1FA2', // Purple
            previousValue: metricsResponse.previous_badges_awarded_count
          },
          {
            label: 'Total Points',
            value: metricsResponse.total_points || 0,
            icon: <PointsIcon />,
            color: '#C2185B', // Pink
            previousValue: metricsResponse.previous_total_points
          }
        ];

        // Fetch recent activities with same error handling pattern
        const activitiesResponse = await safeApiCall(
          Promise.race([
            api.get('/admin/dashboard/activities'),
            new Promise((_, reject) => 
              setTimeout(() => reject(new Error('Request timed out')), DEFAULT_TIMEOUT)
            )
          ]),
          null
        );

        // Format and update state with fetched data
        setMetrics(formattedMetrics);
        
        // Handle both paginated and non-paginated API responses
        if (activitiesResponse) {
          const activities = extractItems<RecentActivity>(activitiesResponse, []);
          setRecentActivities(activities);
        } else {
          setRecentActivities([]);
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err instanceof Error ? err.message : 'An error occurred while fetching dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  /**
   * Renders a metric card with value, label, and icon
   */
  const renderMetricCard = (metric: DashboardMetric) => {
    const percentChange = metric.previousValue 
      ? Math.round(((metric.value - metric.previousValue) / metric.previousValue) * 100) 
      : null;
    
    const isIncrease = percentChange !== null ? percentChange > 0 : null;
    
    return (
      <Card elevation={2} sx={{ height: '100%' }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box
              sx={{
                bgcolor: `${metric.color}20`, // 20% opacity of the color
                color: metric.color,
                p: 1,
                borderRadius: 1,
                mr: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              {metric.icon}
            </Box>
            <Typography variant="h6" component="div" color="text.secondary">
              {metric.label}
            </Typography>
          </Box>
          
          <Typography variant="h4" component="div" fontWeight="bold">
            {metric.value.toLocaleString()}
          </Typography>
          
          {percentChange !== null && (
            <Typography 
              variant="body2" 
              color={isIncrease ? 'success.main' : 'error.main'}
              sx={{ mt: 1, display: 'flex', alignItems: 'center' }}
            >
              {isIncrease ? '+' : ''}{percentChange}% from previous period
            </Typography>
          )}
        </CardContent>
      </Card>
    );
  };

  /**
   * Formats a timestamp string into a human-readable date and time
   */
  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return timestamp;
    }
  };

  return (
    <AdminLayout>
      <Box sx={{ p: 2 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
          Dashboard
        </Typography>
        
        <Typography variant="body1" paragraph sx={{ mb: 4 }}>
          Welcome to the Pine Time Admin Dashboard. Here's an overview of the platform's current status.
        </Typography>
        
        {/* Error message if API call fails */}
        {error && (
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        )}
        
        {/* Metrics overview */}
        <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
          Key Metrics
        </Typography>
        
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {loading ? (
            // Skeleton loaders while data is loading
            Array.from(new Array(5)).map((_, index) => (
              <Grid key={index} sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 4', lg: 'span 2.4' } }}>
                <Skeleton variant="rectangular" height={160} sx={{ borderRadius: 2 }} />
              </Grid>
            ))
          ) : (
            // Actual metrics cards
            metrics.map((metric, index) => (
              <Grid key={index} sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 4', lg: 'span 2.4' } }}>
                {renderMetricCard(metric)}
              </Grid>
            ))
          )}
        </Grid>
        
        {/* Recent Activities */}
        <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
          Recent Activities
        </Typography>
        
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          {loading ? (
            // Skeleton loaders while data is loading
            Array.from(new Array(5)).map((_, index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Skeleton variant="text" height={30} width="60%" />
                <Skeleton variant="text" height={20} width="40%" />
                <Skeleton variant="text" height={20} width="80%" />
                {index < 4 && <Divider sx={{ my: 2 }} />}
              </Box>
            ))
          ) : recentActivities.length > 0 ? (
            // Actual activities
            recentActivities.map((activity, index) => (
              <Box key={activity.id} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Typography variant="h6" component="div">
                    {activity.type}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {formatTimestamp(activity.timestamp)}
                  </Typography>
                </Box>
                <Typography variant="body1">
                  <strong>{activity.user}</strong> {activity.action}
                </Typography>
                {activity.details && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {activity.details}
                  </Typography>
                )}
                {index < recentActivities.length - 1 && (
                  <Box sx={{ height: 1, bgcolor: 'grey.200', my: 2 }} />
                )}
              </Box>
            ))
          ) : (
            // No activities fallback
            <Typography variant="body1" color="text.secondary" textAlign="center" py={3}>
              No recent activities to display
            </Typography>
          )}
        </Paper>
      </Box>
    </AdminLayout>
  );
};

export default DashboardPage;
