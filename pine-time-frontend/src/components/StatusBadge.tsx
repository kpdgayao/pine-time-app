import React from 'react';
import { Chip } from '@mui/material';

interface StatusBadgeProps {
  status: 'Active' | 'Full' | 'Past';
}

const statusColors = {
  Active: 'success',
  Full: 'error',
  Past: 'default',
};

const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => (
  <Chip
    label={status}
    color={statusColors[status] as any}
    size="small"
    variant={status === 'Past' ? 'outlined' : 'filled'}
    sx={{ fontWeight: 600, minWidth: 70, justifyContent: 'center' }}
  />
);

export default StatusBadge;
