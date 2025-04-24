import { useState, useCallback } from 'react';
import api, { retryApiCall } from '../utils/api';
import { extractErrorMessage } from '../utils/extractErrorMessage';

export interface PaymentRecord {
  id: number;
  registration_id: number;
  user_id: number;
  event_id: number;
  amount_paid: number;
  payment_channel: string;
  payment_date: string;
}

export interface PaymentSubmission {
  registration_id: number;
  user_id: number;
  event_id: number;
  amount_paid: number;
  payment_channel: string;
  payment_date?: string;
}

/**
 * Hook for managing payment-related functionality
 * Handles fetching, submitting, and tracking payment status
 */
export function usePayments() {
  const [paymentRecords, setPaymentRecords] = useState<PaymentRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  /**
   * Fetch payment records for a specific user
   * @param userId - The ID of the user to fetch payments for
   */
  const fetchPaymentRecords = async (userId?: number) => {
    if (!userId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await retryApiCall(
        () => api.get(`/payments/users/${userId}/payments`),
        { items: [] },
        2,
        1000
      );
      
      // Handle both paginated and non-paginated responses
      const records = Array.isArray(response.items) 
        ? response.items 
        : Array.isArray(response) 
          ? response 
          : [];
      
      // Transform API response to our internal format
      const formattedRecords: PaymentRecord[] = records.map((record: any) => ({
        id: record.id,
        registration_id: record.registration_id,
        user_id: record.user_id,
        event_id: record.event_id,
        amount_paid: record.amount_paid,
        payment_channel: record.payment_channel,
        payment_date: record.payment_date
      }));
      
      setPaymentRecords(formattedRecords);
    } catch (err) {
      setError(extractErrorMessage(err));
      console.error('Error fetching payment records:', err);
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * Submit a new payment
   * @param paymentData - Payment submission data
   * @returns Promise resolving to success status
   */
  const submitPayment = async (paymentData: PaymentSubmission): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/payments/payments/register', paymentData);
      
      // Add to local state for immediate UI update
      const newPayment: PaymentRecord = {
        id: response.data?.id || Date.now(), // Use response ID if available, fallback to timestamp
        registration_id: paymentData.registration_id,
        user_id: paymentData.user_id,
        event_id: paymentData.event_id,
        amount_paid: paymentData.amount_paid,
        payment_channel: paymentData.payment_channel,
        payment_date: new Date().toISOString()
      };
      
      setPaymentRecords(prev => [...prev, newPayment]);
      return true;
    } catch (err) {
      setError(extractErrorMessage(err));
      console.error('Payment submission error:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * Check if a registration has been paid
   * @param eventId - The event ID
   * @param registrationId - The registration ID
   * @returns Boolean indicating if the registration is paid
   */
  const isRegistrationPaid = useCallback((eventId: number, registrationId: number) => {
    return paymentRecords.some((record: PaymentRecord) => 
      record.event_id === eventId && 
      record.registration_id === registrationId
    );
  }, [paymentRecords]);
  
  /**
   * Get payment details for a specific registration
   * @param eventId - The event ID
   * @param registrationId - The registration ID
   * @returns Payment record if found, null otherwise
   */
  const getPaymentDetails = (eventId: number, registrationId: number): PaymentRecord | null => {
    if (!eventId || !registrationId) return null;
    
    const payment = paymentRecords.find(
      record => record.event_id === eventId && 
                record.registration_id === registrationId
    );
    
    return payment || null;
  };
  
  return {
    paymentRecords,
    loading,
    error,
    fetchPaymentRecords,
    submitPayment,
    isRegistrationPaid,
    getPaymentDetails
  };
}
