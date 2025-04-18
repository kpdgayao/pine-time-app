import React, { useEffect, useState } from 'react';
import api from '../api/client';

const PointsPage: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/points/stats')
      .then(res => setStats(res.data))
      .catch(err => {
        let message = 'Failed to load points stats.';
        const data = err.response?.data;
        if (typeof data === 'string') {
          message = data;
        } else if (Array.isArray(data)) {
          message = data.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        } else if (typeof data === 'object' && data !== null) {
          message = data.detail || data.msg || JSON.stringify(data);
        }
        setError(message);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading points...</div>;
  if (error) return <div>{error}</div>;
  if (!stats) return <div>No points data found.</div>;

  return (
    <div>
      <h2>Your Points</h2>
      <p>Current Balance: {stats.current_balance}</p>
      <p>Total Earned: {stats.total_earned}</p>
      <p>Total Redeemed: {stats.total_redeemed}</p>
      <p>Rank: {stats.user_rank}</p>
      {/* Add more breakdowns as needed */}
    </div>
  );
};

export default PointsPage;
