import React, { createContext, useContext, useState } from 'react';

// Define the context type for better type safety
interface LoadingContextType {
  loading: boolean;
  setLoading: (loading: boolean) => void;
  loadingMessage: string | null;
  setLoadingMessage: (message: string | null) => void;
}

// Create context with default values
const LoadingContext = createContext<LoadingContextType>({
  loading: false,
  setLoading: () => {},
  loadingMessage: null,
  setLoadingMessage: () => {},
});

// Custom hook for using the loading context
export const useLoading = () => useContext(LoadingContext);

// Loading provider component
export const LoadingProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingMessage, setLoadingMessage] = useState<string | null>(null);

  // Context value
  const contextValue: LoadingContextType = {
    loading,
    setLoading,
    loadingMessage,
    setLoadingMessage,
  };

  return (
    <LoadingContext.Provider value={contextValue}>
      {children}
    </LoadingContext.Provider>
  );
};

export default LoadingContext;
