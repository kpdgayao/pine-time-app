import { useState } from 'react';
import api from '../api/client';
import { extractErrorMessage } from '../utils/extractErrorMessage';

interface RegistrationState {
  loading: number | null;
  error: string | null;
  success: string | null;
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

  const unregister = async (eventId: number) => {
    setState({ ...state, loading: eventId, error: null, success: null });
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

  const cancelPending = async (eventId: number) => {
    setState({ ...state, loading: eventId, error: null, success: null });
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
