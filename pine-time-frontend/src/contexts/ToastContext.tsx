import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { Snackbar, Alert, Slide, SnackbarOrigin } from '@mui/material';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
  duration?: number;
}

interface ToastContextProps {
  showToast: (message: string, type: ToastType, duration?: number) => void;
}

const ToastContext = createContext<ToastContextProps | undefined>(undefined);

let toastId = 0;

export const ToastProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [anchorOrigin] = useState<SnackbarOrigin>({ vertical: 'top', horizontal: 'center' });

  const showToast = useCallback((message: string, type: ToastType, duration = 4000) => {
    setToasts((prev) => [...prev, { id: ++toastId, message, type, duration }]);
  }, []);

  const handleClose = (id: number) => (_event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') return;
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {toasts.map((toast) => (
        <Snackbar
          key={toast.id}
          open
          autoHideDuration={toast.duration}
          onClose={handleClose(toast.id)}
          anchorOrigin={anchorOrigin}
          TransitionComponent={Slide}
        >
          <Alert
            elevation={6}
            variant="filled"
            onClose={handleClose(toast.id)}
            severity={toast.type}
            sx={{ minWidth: 280, fontWeight: 600, alignItems: 'center' }}
          >
            {toast.message}
          </Alert>
        </Snackbar>
      ))}
    </ToastContext.Provider>
  );
};

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within a ToastProvider');
  return ctx;
}
