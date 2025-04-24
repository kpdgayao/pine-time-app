import { useEffect, useState } from 'react';
import api from '../api/client';

export interface PaymentDetails {
  payment_id: number;
  registration_id: number;
  user_id: number;
  event_id: number;
  amount_paid: number;
  payment_channel: string;
  payment_reference?: string;
  payment_date: string;
}

/**
 * Fetches payment details for a list of registration IDs.
 * Returns a map: { [registration_id]: PaymentDetails | null }
 */
export function usePaymentsForRegistrations(registrationIds: number[]) {
  const [payments, setPayments] = useState<{ [registrationId: number]: PaymentDetails | null }>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function fetchPayments() {
      setLoading(true);
      const results: { [registrationId: number]: PaymentDetails | null } = {};
      await Promise.all(
        registrationIds.map(async (regId) => {
          try {
            // Using the correct endpoint path according to documentation
            const res = await api.get(`/payments/payments/by_registration/${regId}`);
            results[regId] = res.data;
          } catch (err: any) {
            if (err.response && err.response.status === 404) {
              results[regId] = null;
            } else {
              results[regId] = null; // Optionally handle other errors differently
            }
          }
        })
      );
      if (!cancelled) {
        setPayments(results);
        setLoading(false);
      }
    }

    if (registrationIds.length > 0) {
      fetchPayments();
    } else {
      setPayments({});
    }
    return () => {
      cancelled = true;
    };
  }, [registrationIds.join(',')]); // join to avoid array reference issues

  return { payments, loading };
}
