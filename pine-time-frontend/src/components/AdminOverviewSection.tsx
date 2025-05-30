import React from 'react';
import EventStatsChart from './EventStatsChart';
import { Typography, Box } from '@mui/material';

interface AnalyticsProps {
  totalEvents: number;
  activeEvents: number;
  totalParticipants: number;
  totalRevenue: number;
  eventStats: Record<number, { registration_count: number; revenue: number }>;
  eventsArray: any[];
  loading: boolean;
}

const AdminOverviewSection: React.FC<AnalyticsProps> = ({
  totalEvents,
  activeEvents,
  totalParticipants,
  totalRevenue,
  eventStats,
  eventsArray,
  loading,
}) => {
  return (
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
        Admin Dashboard Analytics
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 4, mb: 4 }}>
        <Box>
          <Typography variant="subtitle1">Total Events: {totalEvents}</Typography>
          <Typography variant="subtitle1">Active Events: {activeEvents}</Typography>
          <Typography variant="subtitle1">Max Total Participants: {totalParticipants}</Typography>
          <Typography variant="subtitle1">Total Revenue: {totalRevenue}</Typography>
        </Box>
        <Box>
          {/* Only render the chart when loading is false */}
          {loading ? (
            <div style={{ width: 320, display: 'flex', alignItems: 'center', justifyContent: 'center', height: 220 }}>
              <span>Loading analytics...</span>
            </div>
          ) : (
            <EventStatsChart
              events={eventsArray.map((e: any) => ({
                ...e,
                registration_count: eventStats[e.id]?.registration_count ?? 0,
                revenue: eventStats[e.id]?.revenue ?? 0,
              }))}
            />
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default AdminOverviewSection;
