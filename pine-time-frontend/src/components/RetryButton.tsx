import React from 'react';
import { Button, CircularProgress } from '@mui/material';

interface RetryButtonProps {
  onClick: () => void;
  loading?: boolean;
  children?: React.ReactNode;
}

const RetryButton: React.FC<RetryButtonProps> = ({ onClick, loading = false, children }) => (
  <Button onClick={onClick} variant="outlined" color="primary" disabled={loading} startIcon={loading ? <CircularProgress size={18} /> : null}>
    {children || 'Retry'}
  </Button>
);

export default RetryButton;
