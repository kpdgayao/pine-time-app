import React, { useState } from "react";
import {
  Box,
  CssBaseline,
  Paper,
  Tabs,
  Tab,
  Container,
} from '@mui/material';


import AdminUsersSection from "../components/AdminUsersSection";
import AdminEventsSection from "../components/AdminEventsSection";
import PointsBadgesLeaderboard from "../components/PointsBadgesLeaderboard";
import { useAuth } from '../contexts/AuthContext';

// Simple placeholder components for each admin section
const OverviewSection = () => <div>Overview (Key Stats, Analytics)</div>;
const UsersSection = () => <AdminUsersSection />;
const EventsSection = () => <AdminEventsSection />;
import AdminPointsTransactionsTable from "../components/AdminPointsTransactionsTable";

const PointsSection = () => (
  <>
    <PointsBadgesLeaderboard />
    <AdminPointsTransactionsTable />
  </>
);
import AdminBadgesSection from "../components/AdminBadgesSection";
const BadgesSection = () => <AdminBadgesSection />;

const sections = [
  { key: "overview", label: "Overview", component: OverviewSection },
  { key: "users", label: "Users", component: UsersSection },
  { key: "events", label: "Events", component: EventsSection },
  { key: "points", label: "Points", component: PointsSection },
  { key: "badges", label: "Badges", component: BadgesSection },
];

const AdminDashboardPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState("overview");

  // Section tab handler
  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    setActiveSection(newValue);
  };

  const sectionIndex = sections.findIndex((s) => s.key === activeSection);
  const SectionComponent = sections[sectionIndex]?.component || (() => null);

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <CssBaseline />

      <Paper elevation={2} sx={{ width: '100%', p: 2, boxSizing: 'border-box', m: 0, borderRadius: 0 }}>
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
        <Box sx={{ mt: 2 }}>
          <SectionComponent />
        </Box>
      </Paper>
    </Box>
  );
};

export default AdminDashboardPage;
