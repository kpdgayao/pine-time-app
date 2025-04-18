import React, { useEffect, useState } from 'react';
import api from '../api/client';

const LeaderboardPage: React.FC = () => {
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/points/leaderboard')
      .then(res => setLeaderboard(res.data))
      .catch(err => {
        let message = 'Failed to load leaderboard.';
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

  if (loading) return <div>Loading leaderboard...</div>;
  if (error) return <div>{error}</div>;
  if (!leaderboard.length) return <div>No leaderboard data found.</div>;

  return (
    <div>
      <h2>Leaderboard</h2>
      <ol>
        {leaderboard.map((entry, idx) => (
          <li key={idx}>{entry.username} - {entry.current_balance} pts</li>
        ))}
      </ol>
    </div>
  );
};

export default LeaderboardPage;
