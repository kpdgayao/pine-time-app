import React, { useEffect, useState } from 'react';
import { Typography, Dialog, DialogTitle, DialogContent, DialogActions, Button } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';

const EventDetailsPage: React.FC = () => {
  const { showToast } = useToast();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [showAuthPrompt, setShowAuthPrompt] = useState(!user);
  const { eventId } = useParams<{ eventId: string }>();
  const [event, setEvent] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const [registering, setRegistering] = useState(false);
  const [alreadyRegistered, setAlreadyRegistered] = useState(false);

  useEffect(() => {
    if (!user) return;
    api.get(`/events/${eventId}`)
      .then(res => setEvent(res.data))
      .catch(err => {
        const data = err.response?.data;
        let errorMsg = 'An error occurred';
        if (typeof data === 'string') {
          errorMsg = data;
        } else if (Array.isArray(data)) {
          errorMsg = data.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        } else if (typeof data === 'object' && data !== null) {
          errorMsg = data.detail || data.msg || JSON.stringify(data);
        }
        errorMsg = errorMsg; // assign to local variable, not state
      })
      .finally(() => setLoading(false));
  }, [eventId, user]);

  const handleRegister = async () => {
    if (!user) {
      setShowAuthPrompt(true);
      return;
    }
    setRegistering(true);
    try {
      await api.post(`/registrations/events/${eventId}/register`);
      showToast('✅ Registration successful! 🌲', 'success');
      setAlreadyRegistered(true);
    } catch (err: any) {
      let message = 'Registration failed.';
      const data = err.response?.data;
      if (typeof data === 'string') {
        message = data;
      } else if (Array.isArray(data)) {
        message = data.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
      } else if (typeof data === 'object' && data !== null) {
        message = data.detail || data.msg || JSON.stringify(data);
      }
      let emoji = '❌';
      if (message.toLowerCase().includes('already registered')) {
        emoji = '⚠️';
        setAlreadyRegistered(true);
      }
      if (message.toLowerCase().includes('full')) emoji = '⚠️';
      if (message.toLowerCase().includes('past')) emoji = '⏰';
      showToast(`${emoji} ${message}`, 'error');
    } finally {
      setRegistering(false);
    }
  };

  if (!user) {
    return (
      <Dialog open={showAuthPrompt} onClose={() => navigate('/')} maxWidth="xs" fullWidth>
        <DialogTitle>Login or Register Required</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Please log in or register to view event details and register for events.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button href="/login" variant="contained" color="primary">Login</Button>
          <Button href="/register" variant="outlined" color="primary">Register</Button>
          <Button onClick={() => navigate('/')}>Cancel</Button>
        </DialogActions>
      </Dialog>
    );
  }

  if (loading) return <div>Loading...</div>;

  // Disable registration if event is in the past
  const isPastEvent = event && new Date(event.end_time) < new Date();

  return (
    <div>
      <Typography variant="h5">{event.title}</Typography>
      <p>Type: {event.event_type}</p>
      <p>Description: {event.description}</p>
      <p>Location: {event.location}</p>
      <p>Start: {event.start_time}</p>
      <p>End: {event.end_time}</p>
      <button
        onClick={handleRegister}
        disabled={registering || alreadyRegistered || isPastEvent}
        style={{ marginTop: '1rem' }}
      >
        {alreadyRegistered ? 'Already Registered' : isPastEvent ? 'Event Ended' : registering ? 'Registering...' : 'Register for Event'}
      </button>
    </div>
  );
};

export default EventDetailsPage;
