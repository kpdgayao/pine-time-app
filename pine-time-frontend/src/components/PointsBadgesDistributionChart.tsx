import React from "react";
import { Bar, Pie } from "react-chartjs-2";
import { Chart, ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from "chart.js";

Chart.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

interface DistributionProps {
  leaderboard: Array<{ points: number; badges: number }>;
}

const PointsBadgesDistributionChart: React.FC<DistributionProps> = ({ leaderboard }) => {
  // Points distribution (histogram)
  const pointsBuckets = [0, 50, 100, 200, 500, 1000, 2000];
  const pointsCounts = pointsBuckets.map((min, i, arr) =>
    leaderboard.filter(u => u.points >= min && u.points < (arr[i + 1] || Infinity)).length
  );
  // Badges distribution (pie)
  const badgeCounts: Record<number, number> = {};
  leaderboard.forEach(u => { badgeCounts[u.badges] = (badgeCounts[u.badges] || 0) + 1; });
  const badgeLabels = Object.keys(badgeCounts).map(Number).sort((a, b) => a - b);
  const badgeData = badgeLabels.map(l => badgeCounts[l]);

  const pointsData = {
    labels: pointsBuckets.map((min, i, arr) =>
      i === arr.length - 1 ? `${min}+` : `${min}-${arr[i + 1] - 1}`
    ),
    datasets: [
      {
        label: "Users",
        data: pointsCounts,
        backgroundColor: "#1976d2",
      },
    ],
  };
  const badgesPieData = {
    labels: badgeLabels.map(l => `${l} badge${l !== 1 ? "s" : ""}`),
    datasets: [
      {
        data: badgeData,
        backgroundColor: ["#43a047", "#ffa726", "#ab47bc", "#29b6f6", "#ef5350", "#8d6e63", "#789262"],
      },
    ],
  };

  return (
    <div style={{ display: "flex", gap: 32, flexWrap: "wrap", marginTop: 24 }}>
      <div style={{ width: 340 }}>
        <h4>Points Distribution</h4>
        <Bar data={pointsData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
      </div>
      <div style={{ width: 260 }}>
        <h4>Badges Distribution</h4>
        <Pie data={badgesPieData} options={{ responsive: true }} />
      </div>
    </div>
  );
};

export default PointsBadgesDistributionChart;
