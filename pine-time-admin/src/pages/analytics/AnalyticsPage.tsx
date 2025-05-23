import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  CardHeader,
  Alert,
  CircularProgress,
  Tab,
  Tabs,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import AdminLayout from '../../components/layout/AdminLayout';
import { PointsService } from '../../api/services';
import { useLoading } from '../../contexts/LoadingContext';
import type { User } from '../../types/api';

/**
 * Custom tab panel component
 */
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

/**
 * Analytics page component
 * Provides visual data analysis and reporting for admin users
 */
const AnalyticsPage: React.FC = () => {
  // Tab state
  const [tabValue, setTabValue] = useState(0);
  
  // Time period filter
  const [timePeriod, setTimePeriod] = useState('month');
  
  // Data loading states
  const [usersData, setUsersData] = useState<any[]>([]);
  const [eventsData, setEventsData] = useState<any[]>([]);
  const [registrationsData, setRegistrationsData] = useState<any[]>([]);
  const [pointsData, setPointsData] = useState<any[]>([]);
  const [leaderboardData, setLeaderboardData] = useState<User[]>([]);
  
  // Error handling state
  const [error, setError] = useState<string | null>(null);
  
  // Loading context for managing loading states
  const { setLoading, setLoadingMessage } = useLoading();

  // Chart colors
  const COLORS = ['#2E7D32', '#1976d2', '#9c27b0', '#ed6c02', '#d32f2f', '#0288d1'];

  /**
   * Handle tab change
   */
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  /**
   * Handle time period change
   */
  const handleTimePeriodChange = (event: SelectChangeEvent) => {
    setTimePeriod(event.target.value);
  };

  /**
   * Fetch analytics data based on selected time period
   */
  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setLoadingMessage('Loading analytics data...');
      setError(null);
      
      // For demo purposes, this would be connected to your API endpoints
      // Here I'm using sample data based on the time period
      
      // Users Registration Data (sample data)
      const usersRegistrationData = [
        { name: 'Jan', count: 12 },
        { name: 'Feb', count: 15 },
        { name: 'Mar', count: 18 },
        { name: 'Apr', count: 22 },
        { name: 'May', count: 28 },
        { name: 'Jun', count: 25 },
        { name: 'Jul', count: 30 },
        { name: 'Aug', count: 32 },
        { name: 'Sep', count: 35 },
        { name: 'Oct', count: 38 },
        { name: 'Nov', count: 42 },
        { name: 'Dec', count: 45 }
      ];
      
      // Events Data (sample data)
      const eventsCreationData = [
        { name: 'Jan', count: 5 },
        { name: 'Feb', count: 7 },
        { name: 'Mar', count: 4 },
        { name: 'Apr', count: 8 },
        { name: 'May', count: 10 },
        { name: 'Jun', count: 6 },
        { name: 'Jul', count: 9 },
        { name: 'Aug', count: 11 },
        { name: 'Sep', count: 8 },
        { name: 'Oct', count: 12 },
        { name: 'Nov', count: 14 },
        { name: 'Dec', count: 15 }
      ];
      
      // Event Registrations Data (sample data)
      const eventRegistrationsData = [
        { name: 'Jan', count: 35 },
        { name: 'Feb', count: 42 },
        { name: 'Mar', count: 38 },
        { name: 'Apr', count: 45 },
        { name: 'May', count: 55 },
        { name: 'Jun', count: 48 },
        { name: 'Jul', count: 60 },
        { name: 'Aug', count: 65 },
        { name: 'Sep', count: 58 },
        { name: 'Oct', count: 70 },
        { name: 'Nov', count: 75 },
        { name: 'Dec', count: 85 }
      ];
      
      // Points Distribution Data (sample data)
      const pointsDistributionData = [
        { name: 'Event Attendance', value: 45 },
        { name: 'Badge Achievements', value: 25 },
        { name: 'Social Actions', value: 15 },
        { name: 'Admin Bonuses', value: 10 },
        { name: 'Referrals', value: 5 }
      ];
      
      // Filter data based on time period
      const getFilteredData = (data: any[]) => {
        switch (timePeriod) {
          case 'week':
            return data.slice(-7);
          case 'month':
            return data.slice(-30);
          case 'quarter':
            return data.slice(-90);
          case 'year':
            return data;
          default:
            return data;
        }
      };
      
      // Fetch leaderboard data
      const leaderboard = await PointsService.getLeaderboard(10);
      
      // Set the data
      setUsersData(getFilteredData(usersRegistrationData));
      setEventsData(getFilteredData(eventsCreationData));
      setRegistrationsData(getFilteredData(eventRegistrationsData));
      setPointsData(pointsDistributionData);
      setLeaderboardData(leaderboard);
      
    } catch (err) {
      setError('An error occurred while fetching analytics data');
      console.error('Error fetching analytics data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch analytics data when time period changes
  useEffect(() => {
    fetchAnalyticsData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timePeriod]);

  return (
    <AdminLayout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Analytics Dashboard
          </Typography>
          
          <FormControl variant="outlined" sx={{ minWidth: 150 }}>
            <InputLabel id="time-period-label">Time Period</InputLabel>
            <Select
              labelId="time-period-label"
              value={timePeriod}
              onChange={handleTimePeriodChange}
              label="Time Period"
              size="small"
            >
              <MenuItem value="week">Last Week</MenuItem>
              <MenuItem value="month">Last Month</MenuItem>
              <MenuItem value="quarter">Last Quarter</MenuItem>
              <MenuItem value="year">Last Year</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs 
              value={tabValue} 
              onChange={handleTabChange} 
              aria-label="analytics tabs"
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab label="Users" />
              <Tab label="Events" />
              <Tab label="Registrations" />
              <Tab label="Points" />
            </Tabs>
          </Box>
          
          {/* Users Analytics Tab */}
          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 8' } }}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>User Registrations Over Time</Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart
                      data={usersData}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="count" stroke="#2E7D32" name="New Users" activeDot={{ r: 8 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              
              <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>Top Users Leaderboard</Typography>
                  {leaderboardData.length > 0 ? (
                    <Box sx={{ overflowY: 'auto', maxHeight: 400 }}>
                      {leaderboardData.map((user, index) => (
                        <Box key={user.id} sx={{ mb: 2, pb: 2, borderBottom: index < leaderboardData.length - 1 ? '1px solid #eee' : 'none' }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography 
                                sx={{ 
                                  width: 24, 
                                  height: 24, 
                                  borderRadius: '50%', 
                                  bgcolor: index < 3 ? COLORS[index] : '#757575', 
                                  color: 'white',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  fontWeight: 'bold'
                                }}
                              >
                                {index + 1}
                              </Typography>
                              <Typography variant="body1">{user.username}</Typography>
                            </Box>
                            <Typography variant="body1" fontWeight="bold">{user.points} points</Typography>
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  ) : (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}>
                      <CircularProgress size={32} />
                    </Box>
                  )}
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>
          
          {/* Events Analytics Tab */}
          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>Events Created Over Time</Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart
                      data={eventsData}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="count" name="Events Created" fill="#1976d2" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              
              <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>Event Type Distribution</Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Workshop', value: 25 },
                          { name: 'Seminar', value: 15 },
                          { name: 'Meetup', value: 30 },
                          { name: 'Game Night', value: 20 },
                          { name: 'Trivia Night', value: 10 }
                        ]}
                        cx="50%"
                        cy="50%"
                        labelLine={true}
                        outerRadius={150}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      >
                        {[
                          { name: 'Workshop', value: 25 },
                          { name: 'Seminar', value: 15 },
                          { name: 'Meetup', value: 30 },
                          { name: 'Game Night', value: 20 },
                          { name: 'Trivia Night', value: 10 }
                        ].map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>
          
          {/* Registrations Analytics Tab */}
          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              <Grid sx={{ gridColumn: { xs: 'span 12' } }}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>Event Registrations Over Time</Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart
                      data={registrationsData}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="count" name="Registrations" fill="#9c27b0" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              
              <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>Registration Status Distribution</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Attended', value: 70 },
                          { name: 'No Show', value: 15 },
                          { name: 'Cancelled', value: 10 },
                          { name: 'Pending', value: 5 }
                        ]}
                        cx="50%"
                        cy="50%"
                        labelLine={true}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      >
                        {[
                          { name: 'Attended', value: 70 },
                          { name: 'No Show', value: 15 },
                          { name: 'Cancelled', value: 10 },
                          { name: 'Pending', value: 5 }
                        ].map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              
              <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>Payment Status Distribution</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Paid', value: 65 },
                          { name: 'Pending', value: 20 },
                          { name: 'Refunded', value: 10 },
                          { name: 'Not Required', value: 5 }
                        ]}
                        cx="50%"
                        cy="50%"
                        labelLine={true}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      >
                        {[
                          { name: 'Paid', value: 65 },
                          { name: 'Pending', value: 20 },
                          { name: 'Refunded', value: 10 },
                          { name: 'Not Required', value: 5 }
                        ].map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>
          
          {/* Points Analytics Tab */}
          <TabPanel value={tabValue} index={3}>
            <Grid container spacing={3}>
              <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 7' } }}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>Points Distribution by Source</Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <PieChart>
                      <Pie
                        data={pointsData}
                        cx="50%"
                        cy="50%"
                        labelLine={true}
                        outerRadius={150}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      >
                        {pointsData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              
              <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 5' } }}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>Points Metrics</Typography>
                  
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Card variant="outlined">
                      <CardHeader 
                        title="Total Points Awarded" 
                        titleTypographyProps={{ variant: 'subtitle1' }}
                        sx={{ pb: 0 }}
                      />
                      <CardContent>
                        <Typography variant="h3" color="primary">128,450</Typography>
                      </CardContent>
                    </Card>
                    
                    <Card variant="outlined">
                      <CardHeader 
                        title="Average Points per User" 
                        titleTypographyProps={{ variant: 'subtitle1' }}
                        sx={{ pb: 0 }}
                      />
                      <CardContent>
                        <Typography variant="h3" color="primary">2,853</Typography>
                      </CardContent>
                    </Card>
                    
                    <Card variant="outlined">
                      <CardHeader 
                        title="Points from Event Attendance" 
                        titleTypographyProps={{ variant: 'subtitle1' }}
                        sx={{ pb: 0 }}
                      />
                      <CardContent>
                        <Typography variant="h3" color="primary">57,802</Typography>
                      </CardContent>
                    </Card>
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>
        </Box>
      </Box>
    </AdminLayout>
  );
};

export default AnalyticsPage;
