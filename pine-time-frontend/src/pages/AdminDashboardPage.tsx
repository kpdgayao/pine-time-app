import React, { useState } from "react";

// Simple placeholder components for each admin section
const OverviewSection = () => <div>Overview (Key Stats, Analytics)</div>;
import AdminUsersSection from "../components/AdminUsersSection";
const UsersSection = () => <AdminUsersSection />;
import AdminEventsSection from "../components/AdminEventsSection";
const EventsSection = () => <AdminEventsSection />;
const PointsSection = () => <div>Points Management (Award, Redeem, Leaderboard)</div>;
const BadgesSection = () => <div>Badges Management (View, Assign)</div>;

const sections = [
  { key: "overview", label: "Overview", component: <OverviewSection /> },
  { key: "users", label: "Users", component: <UsersSection /> },
  { key: "events", label: "Events", component: <EventsSection /> },
  { key: "points", label: "Points", component: <PointsSection /> },
  { key: "badges", label: "Badges", component: <BadgesSection /> },
];

const AdminDashboardPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState("overview");

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Sidebar Navigation */}
      <nav
        style={{
          width: 220,
          background: "#2E7D32",
          color: "white",
          display: "flex",
          flexDirection: "column",
          padding: "2rem 0.5rem",
        }}
      >
        <h2 style={{ margin: "0 0 2rem 0", textAlign: "center" }}>Admin</h2>
        {sections.map((s) => (
          <button
            key={s.key}
            onClick={() => setActiveSection(s.key)}
            style={{
              background: activeSection === s.key ? "#1B5E20" : "transparent",
              color: "white",
              border: "none",
              padding: "1rem",
              textAlign: "left",
              cursor: "pointer",
              fontWeight: activeSection === s.key ? "bold" : "normal",
              borderRadius: 6,
              marginBottom: 8,
            }}
          >
            {s.label}
          </button>
        ))}
      </nav>
      {/* Main Content */}
      <main style={{ flex: 1, padding: "2rem", background: "#f9f9f9" }}>
        {sections.find((s) => s.key === activeSection)?.component}
      </main>
    </div>
  );
};

export default AdminDashboardPage;
