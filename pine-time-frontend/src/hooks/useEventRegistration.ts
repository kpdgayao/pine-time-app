import { useState } from 'react';
import api from '../api/client';
import { extractErrorMessage } from '../utils/extractErrorMessage';
import { Event } from '../types/events';

interface RegistrationState {
  loading: number | null;
  error: string | null;
  success: string | null;
}

// Function to check if an event is within 24 hours of its start time
const isEventWithin24Hours = (event: Event) => {
  const now = new Date();
  const startTime = new Date(event.start_time);
  const timeDiff = startTime.getTime() - now.getTime();
  const hoursDiff = timeDiff / (1000 * 60 * 60);
  
  const isWithin24Hours = hoursDiff <= 24;
  const message = isWithin24Hours 
    ? `Cannot cancel registration for "${event.title}" as it's less than 24 hours before the event starts.` 
    : '';
    
  return { isWithin24Hours, message };
}

export const useEventRegistration = () => {
  const [state, setState] = useState<RegistrationState>({
    loading: null,
    error: null,
    success: null,
  });

  const register = async (eventId: number) => {
    setState({ loading: eventId, error: null, success: null });
    try {
      await api.post(`/events/${eventId}/register`);
      setState(prev => ({ ...prev, loading: null, success: 'Registration submitted! Awaiting admin approval.' }));
      return true;
    } catch (err: any) {
      const message = extractErrorMessage(err);
      setState(prev => ({ ...prev, loading: null, error: message }));
      return false;
    }
  };

  const unregister = async (eventId: number, event?: Event) => {
    setState({ ...state, loading: eventId, error: null, success: null });
    
    // Check if event is provided and within 24 hours of start time
    if (event) {
      const { isWithin24Hours, message } = isEventWithin24Hours(event);
      if (isWithin24Hours) {
        setState(prev => ({ ...prev, loading: null, error: message }));
        return false;
      }
    }
    
    try {
      await api.delete(`/registrations/events/${eventId}/register`);
      setState(prev => ({ ...prev, loading: null, success: 'Unregistered successfully.' }));
      return true;
    } catch (err: any) {
      const message = extractErrorMessage(err);
      setState(prev => ({ ...prev, loading: null, error: message }));
      return false;
    }
  };

  const cancelPending = async (eventId: number, event?: Event) => {
    setState({ ...state, loading: eventId, error: null, success: null });
    
    // Check if event is provided and within 24 hours of start time
    if (event) {
      const { isWithin24Hours, message } = isEventWithin24Hours(event);
      if (isWithin24Hours) {
        setState(prev => ({ ...prev, loading: null, error: message }));
        return false;
      }
    }
    
    try {
      await api.delete(`/registrations/events/${eventId}/register`);
      setState(prev => ({ ...prev, loading: null, success: 'Registration request canceled.' }));
      return true;
    } catch (err: any) {
      const message = extractErrorMessage(err);
      setState(prev => ({ ...prev, loading: null, error: message }));
      return false;
    }
  };

  const clearMessages = () => setState(prev => ({ ...prev, error: null, success: null }));

  return {
    state,
    register,
    unregister,
    cancelPending,
    clearMessages,
  };
};
