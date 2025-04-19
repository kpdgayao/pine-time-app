import React, { useEffect, useState } from 'react';
import { Typography } from '@mui/material';
import { api } from '../api';

const BadgesPage: React.FC = () => {
  const [badges, setBadges] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/badges/users/me/badges')
      .then(res => setBadges(res.data.badges || []))
      .catch(err => {
        let message = 'Failed to load badges.';
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

  if (loading) return <div>Loading badges...</div>;
  if (error) return <div>{error}</div>;
  if (!badges.length) return <div>No badges found.</div>;

  return (
    <div>
      <Typography variant="h5">Your Badges</Typography>
      <ul>
        {badges.map((badge, idx) => (
          <li key={idx}>
            {badge.badge_type_obj?.name || 'Unknown Badge'} - {badge.badge_type_obj?.description || ''}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default BadgesPage;
