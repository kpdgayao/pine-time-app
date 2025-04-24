import React, { useState, useEffect } from "react";
import {
  Box,
  CssBaseline,
  Paper,
  Tabs,
  Tab,
} from '@mui/material';

import api from "../api/client";
import { extractErrorMessage } from '../utils/extractErrorMessage';
import AdminUsersSection from "../components/AdminUsersSection";
import AdminEventsSection from "../components/AdminEventsSection";
import PointsBadgesLeaderboard from "../components/PointsBadgesLeaderboard";

import AdminOverviewSection from "../components/AdminOverviewSection";
import AdminPointsTransactionsTable from "../components/AdminPointsTransactionsTable";
import AdminBadgesSection from "../components/AdminBadgesSection";
import AdminPendingRegistrationsSection from "../components/AdminPendingRegistrationsSection";

const UsersSection = () => <AdminUsersSection />;
const EventsSection = () => <AdminEventsSection />;
const PointsSection = () => (
  <>
    <PointsBadgesLeaderboard />
    <AdminPointsTransactionsTable />
  </>
);
const BadgesSection = () => <AdminBadgesSection />;

// --- CLEANED UP SINGLE COMPONENT IMPLEMENTATION ---
const AdminDashboardPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState<string>("overview");
  const [events, setEvents] = useState<any[]>([]);
  const [eventStats, setEventStats] = useState<Record<number, { registration_count: number; revenue: number }>>({});
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchEvents = async () => {
      setLoading(true);
      try {
        const res = await api.get('/events/');
        const eventsData = res.data;
        
        // Handle both array and paginated object formats
        const eventsArray = Array.isArray(eventsData) 
          ? eventsData 
          : (eventsData && eventsData.items ? eventsData.items : []);
          
        setEvents(eventsArray);
        // Fetch stats for each event
        const stats: Record<number, { registration_count: number; revenue: number }> = {};
        let statsErrors = 0;
        await Promise.all(
          (Array.isArray(eventsData) ? eventsData : []).map(async (eventData: any) => {
            try {
              const statsRes = await api.get(`/events/${eventData.id}/stats`);
              const statsData = statsRes.data;
              stats[eventData.id] = {
                registration_count: statsData.registration_count ?? 0,
                revenue: statsData.revenue ?? 0,
              };
            } catch (err: any) {
              statsErrors += 1;
              const status = err?.response?.status;
              const data = err?.response?.data;
              const msg = extractErrorMessage(err) || "Unknown error";
              console.error(`[Event Stats] Failed for event ${eventData.id}:`, {
                status,
                data,
                msg,
                error: err,
              });
              stats[eventData.id] = { registration_count: 0, revenue: 0 };
            }
          })
        );
        setEventStats(stats);
        if (statsErrors > 0) {
          // Optionally, you could set a state for error or warning here
          // For demonstration, we log a warning
          console.warn(`Some event stats could not be loaded (${statsErrors} errors).`);
        }
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  // Analytics calculations
  // Ensure events is always treated as an array
  const eventsArray: any[] = Array.isArray(events) ? events : [];
  const totalEvents: number = eventsArray.length;
  const activeEvents: number = eventsArray.filter((e: any) => e.is_active).length;
  const totalParticipants: number = eventsArray.reduce((sum: number, e: any) => sum + (e.max_participants || 0), 0);
  const totalRevenue: number = eventsArray.reduce((sum: number, e: any) => sum + (eventStats[e.id]?.revenue || 0), 0);

  const sections = [
    { key: "overview", label: "Overview", component: () => <AdminOverviewSection
      totalEvents={totalEvents}
      activeEvents={activeEvents}
      totalParticipants={totalParticipants}
      totalRevenue={totalRevenue}
      eventStats={eventStats}
      eventsArray={eventsArray}
      loading={loading}
    /> },
    { key: "users", label: "Users", component: UsersSection },
    { key: "events", label: "Events", component: EventsSection },
    { key: "pending", label: "Pending Approvals", component: AdminPendingRegistrationsSection },
    { key: "points", label: "Points", component: PointsSection },
    { key: "badges", label: "Badges", component: BadgesSection },
  ];

  // Section tab handler
  const handleTabChange = (_: React.SyntheticEvent, newValue: string) => {
    setActiveSection(newValue);
  };

  const sectionIndex = sections.findIndex((s) => s.key === activeSection);
  const SectionComponent = sections[sectionIndex]?.component || (() => null);

  return (
    <Box sx={{
      minHeight: '100vh',
      bgcolor: 'background.default',
      width: '100vw',
      maxWidth: 'none',
      overflowX: 'auto',
      p: 0,
      m: 0,
    }}>
      <CssBaseline />
      <Paper
        elevation={2}
        sx={{
          width: '100vw',
          maxWidth: 'none',
          p: 2,
          boxSizing: 'border-box',
          m: 0,
          borderRadius: 0,
        }}
      >
        <Tabs
          value={activeSection}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="scrollable"
          scrollButtons="auto"
          sx={{ mb: 2 }}
        >
          {sections.map((section) => (
            <Tab
              key={section.key}
              label={section.label}
              value={section.key}
              sx={{ fontWeight: 600 }}
            />
          ))}
        </Tabs>
        <Box sx={{ mt: 2, width: '100%', overflowX: 'auto' }}>
          {activeSection === "overview" ? (
            <AdminOverviewSection
              totalEvents={totalEvents}
              activeEvents={activeEvents}
              totalParticipants={totalParticipants}
              totalRevenue={totalRevenue}
              eventStats={eventStats}
              eventsArray={eventsArray}
              loading={loading}
            />
          ) : (
            <SectionComponent />
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default AdminDashboardPage;
