import React from "react";
import { Bar, Pie } from "react-chartjs-2";
import { Chart, ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from "chart.js";

Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

interface Event {
  id: number;
  title: string;
  is_active: boolean;
  max_participants: number;
  registration_count: number;
  revenue: number;
}

interface Props {
  events: Event[];
}

const EventStatsChart: React.FC<Props> = ({ events }) => {
  // Bar chart: Registration counts per event
  const barData = {
    labels: events.map((e) => e.title),
    datasets: [
      {
        label: "Registrations",
        data: events.map((e) => e.registration_count),
        backgroundColor: "#43a047",
      },
    ],
  };
  // Pie chart: Active vs Inactive events
  const pieData = {
    labels: ["Active", "Inactive"],
    datasets: [
      {
        data: [events.filter((e) => e.is_active).length, events.filter((e) => !e.is_active).length],
        backgroundColor: ["#66bb6a", "#bdbdbd"],
      },
    ],
  };
  // Bar chart: Revenue per event
  const revenueData = {
    labels: events.map((e) => e.title),
    datasets: [
      {
        label: "Revenue",
        data: events.map((e) => e.revenue),
        backgroundColor: "#ffa726",
      },
    ],
  };

  return (
    <div style={{ display: "flex", gap: 32, flexWrap: "wrap" }}>
      <div style={{ width: 320 }}>
        <h4>Registrations per Event</h4>
        <Bar data={barData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
      </div>
      <div style={{ width: 220 }}>
        <h4>Active Events</h4>
        <Pie data={pieData} options={{ responsive: true }} />
      </div>
      <div style={{ width: 320 }}>
        <h4>Revenue per Event</h4>
        <Bar data={revenueData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
      </div>
    </div>
  );
};

export default EventStatsChart;
