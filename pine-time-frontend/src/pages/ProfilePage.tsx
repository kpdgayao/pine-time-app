import React, { useEffect, useState } from 'react';
import { api } from '../api';

const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<any>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/users/me')
      .then(res => setProfile(res.data))
      .catch(err => {
        let message = 'Failed to load profile.';
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

  if (loading) return <div>Loading profile...</div>;
  if (error) return <div>{error}</div>;
  if (!profile) return <div>No profile found.</div>;

  return (
    <div>
      <h2>Profile</h2>
      <p>Username: {profile.username}</p>
      <p>Email: {profile.email}</p>
      {/* Add badges, points, and registration history here */}
    </div>
  );
};

export default ProfilePage;
