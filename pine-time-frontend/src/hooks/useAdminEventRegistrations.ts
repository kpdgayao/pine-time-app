import { useCallback, useEffect, useState } from "react";
import api from '../api/client'; // Ensure this is your shared axios instance with token

export interface Registration {
  id: number;
  user_id: number;
  event_id: number;
  registration_date: string;
  status: string;
  payment_status: string;
  user?: any; // Optionally define a User type
  event?: any; // Optionally define an Event type
}

export interface AdminEventRegistrationsResponse {
  items: Registration[];
  total: number;
  approved: number;
  attendance_rate: number;
  revenue: number;
  page: number;
  size: number;
}

export function useAdminEventRegistrations(eventId: number | undefined, page = 1, size = 20) {
  const [data, setData] = useState<AdminEventRegistrationsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRegistrations = useCallback(async () => {
    if (!eventId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/registrations/events/${eventId}/registrations`, {
        params: { page, size },
        timeout: 10000,
      });
      if (typeof response.data === "object" && response.data.items) {
        setData(response.data);
      } else {
        setError("Unexpected API response format.");
      }
    } catch (err: any) {
      if (err.response && err.response.status === 401) {
        setError("Session expired. Please log in again.");
      } else if (err.response && err.response.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Failed to fetch registrations.");
      }
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [eventId, page, size]);

  useEffect(() => {
    fetchRegistrations();
  }, [fetchRegistrations]);

  return { ...data, loading, error, refetch: fetchRegistrations };
}
