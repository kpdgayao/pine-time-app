import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { LinearProgress, Box, Typography, Fade } from '@mui/material';

interface LoadingContextType {
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
  startLoading: (message?: string) => void;
  stopLoading: () => void;
  loadingMessage: string | null;
  setLoadingMessage: (message: string | null) => void;
  progress: number | null;
  setProgress: (progress: number | null) => void;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

interface LoadingProviderProps {
  children: ReactNode;
}

export const LoadingProvider: React.FC<LoadingProviderProps> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState<string | null>(null);
  const [progress, setProgress] = useState<number | null>(null);

  const setLoading = useCallback((loading: boolean) => {
    setIsLoading(loading);
    if (!loading) {
      // Reset message and progress when stopping loading
      setLoadingMessage(null);
      setProgress(null);
    }
  }, []);

  const startLoading = useCallback((message?: string) => {
    setIsLoading(true);
    if (message) {
      setLoadingMessage(message);
    }
  }, []);

  const stopLoading = useCallback(() => {
    setIsLoading(false);
    setLoadingMessage(null);
    setProgress(null);
  }, []);

  return (
    <LoadingContext.Provider
      value={{
        isLoading,
        setLoading,
        startLoading,
        stopLoading,
        loadingMessage,
        setLoadingMessage,
        progress,
        setProgress,
      }}
    >
      {isLoading && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            zIndex: 9999,
            width: '100%',
          }}
        >
          <LinearProgress
            variant={progress !== null ? 'determinate' : 'indeterminate'}
            value={progress !== null ? progress : undefined}
            color="primary"
            sx={{
              height: 4,
              '& .MuiLinearProgress-bar': {
                backgroundColor: '#2E7D32',
              },
            }}
          />
          {loadingMessage && (
            <Fade in={!!loadingMessage}>
              <Box
                sx={{
                  position: 'fixed',
                  top: 4,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  backgroundColor: 'rgba(46, 125, 50, 0.9)',
                  color: 'white',
                  padding: '4px 12px',
                  borderRadius: '0 0 8px 8px',
                  zIndex: 9999,
                  maxWidth: '80%',
                  textAlign: 'center',
                }}
              >
                <Typography variant="caption" fontWeight="medium">
                  {loadingMessage}
                </Typography>
              </Box>
            </Fade>
          )}
        </Box>
      )}
      {children}
    </LoadingContext.Provider>
  );
};

export const useLoading = (): LoadingContextType => {
  const context = useContext(LoadingContext);
  if (context === undefined) {
    throw new Error('useLoading must be used within a LoadingProvider');
  }
  return context;
};
