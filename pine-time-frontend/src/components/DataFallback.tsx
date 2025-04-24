import React from 'react';
import { Box, Typography, Button } from '@mui/material';

interface DataFallbackProps {
  message?: string;
  onRetry?: () => void;
}

const DataFallback: React.FC<DataFallbackProps> = ({ message = 'Failed to load data.', onRetry }) => (
  <Box sx={{ textAlign: 'center', py: 6 }}>
    <Typography variant="h6" color="error" gutterBottom>
      {message}
    </Typography>
    {onRetry && (
      <Button onClick={onRetry} variant="outlined" color="primary">
        Retry
      </Button>
    )}
  </Box>
);

export default DataFallback;
