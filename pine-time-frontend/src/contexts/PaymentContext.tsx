import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { PaymentRecord, PaymentSubmission, usePayments } from '../hooks/usePayments';

interface PaymentContextType {
  paymentRecords: PaymentRecord[];
  isRegistrationPaid: (eventId: number, registrationId: number) => boolean;
  getPaymentDetails: (eventId: number, registrationId: number) => PaymentRecord | null;
  submitPayment: (paymentData: PaymentSubmission) => Promise<boolean>;
  refreshPaymentRecords: () => Promise<void>;
  loading: boolean;
  error: string | null;
}

const PaymentContext = createContext<PaymentContextType | undefined>(undefined);

/**
 * Provider component for payment-related functionality
 * Makes payment state and methods available throughout the application
 */
export const PaymentProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const { user } = useAuth();
  const {
    paymentRecords,
    loading,
    error,
    fetchPaymentRecords,
    submitPayment,
    isRegistrationPaid,
    getPaymentDetails
  } = usePayments();
  
  // Load payment records when user changes
  useEffect(() => {
    if (user?.id) {
      refreshPaymentRecords();
    }
  }, [user?.id]);
  
  /**
   * Refresh payment records from the server
   */
  const refreshPaymentRecords = async () => {
    if (!user?.id) return;
    await fetchPaymentRecords(user.id);
  };
  
  // Poll for payment status updates every 30 seconds when user is logged in
  useEffect(() => {
    if (!user?.id) return;
    
    const pollInterval = setInterval(() => {
      refreshPaymentRecords();
    }, 30000); // 30 seconds
    
    return () => clearInterval(pollInterval);
  }, [user?.id]);
  
  return (
    <PaymentContext.Provider value={{
      paymentRecords,
      isRegistrationPaid,
      getPaymentDetails,
      submitPayment,
      refreshPaymentRecords,
      loading,
      error
    }}>
      {children}
    </PaymentContext.Provider>
  );
};

/**
 * Hook to use the payment context
 * @returns Payment context with state and methods
 */
export const usePayment = () => {
  const context = useContext(PaymentContext);
  if (context === undefined) {
    throw new Error('usePayment must be used within a PaymentProvider');
  }
  return context;
};
