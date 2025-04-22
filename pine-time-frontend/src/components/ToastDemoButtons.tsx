import React from 'react';
import { Stack } from '@mui/material';
import PineTimeButton from './PineTimeButton';
import { useToast } from '../contexts/ToastContext';

const ToastDemoButtons: React.FC = () => {
  const { showToast } = useToast();
  return (
    <Stack direction="row" spacing={2}>
      <PineTimeButton onClick={() => showToast('Success message!', 'success')} variantType="primary">Success</PineTimeButton>
      <PineTimeButton onClick={() => showToast('Error message!', 'error')} variantType="secondary">Error</PineTimeButton>
      <PineTimeButton onClick={() => showToast('Info message!', 'info')} variantType="text">Info</PineTimeButton>
      <PineTimeButton onClick={() => showToast('Warning message!', 'warning')} variantType="secondary">Warning</PineTimeButton>
    </Stack>
  );
};

export default ToastDemoButtons;
