import React, { useEffect, useState } from 'react';
import { Typography } from '@mui/material';
import { useParams } from 'react-router-dom';
import { api } from '../api';

const EventDetailsPage: React.FC = () => {
  const { eventId } = useParams<{ eventId: string }>();
  const [event, setEvent] = useState<any>(null);
  let errorMsg = '';
  const [loading, setLoading] = useState(true);
  
  const [registering, setRegistering] = useState(false);
  const [registerMsg, setRegisterMsg] = useState('');
  const [alreadyRegistered, setAlreadyRegistered] = useState(false);

  useEffect(() => {
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
  }, [eventId]);

  const handleRegister = async () => {
    setRegistering(true);
    setRegisterMsg('');
    try {
      await api.post(`/registrations/events/${eventId}/register`);
      setRegisterMsg('Registration successful!');
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
      setRegisterMsg(message);
      if (message.toLowerCase().includes('already registered')) {
        setAlreadyRegistered(true);
      }
    } finally {
      setRegistering(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  // Disable registration if event is in the past
  const isPastEvent = event && new Date(event.end_time) < new Date();

  return (
    <div>
      {errorMsg && <div style={{color:'red'}}>{errorMsg}</div>}
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
      {registerMsg && <div style={{ marginTop: '0.5rem', color: registerMsg.includes('success') ? 'green' : 'red' }}>{registerMsg}</div>}
    </div>
  );
};

export default EventDetailsPage;
