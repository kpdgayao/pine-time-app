import React from 'react';
import { 
  Button, Dialog, DialogActions, DialogContent, 
  DialogTitle, Typography, CircularProgress 
} from '@mui/material';

type ConfirmActionType = 'register' | 'unregister' | 'cancel';

interface ConfirmActionDialogProps {
  open: boolean;
  onClose: () => void;
  type: ConfirmActionType | null;
  eventTitle: string;
  loading: number | null; // Changed from boolean to match registration hook's loading state
  onConfirm: () => void;
}

const ConfirmActionDialog: React.FC<ConfirmActionDialogProps> = ({
  open,
  onClose,
  type,
  eventTitle,
  loading,
  onConfirm
}) => {
  const getTitle = () => {
    switch (type) {
      case 'register': return 'Confirm Registration';
      case 'unregister': return 'Confirm Unregistration';
      case 'cancel': return 'Confirm Cancellation';
      default: return 'Confirm Action';
    }
  };

  const getMessage = () => {
    switch (type) {
      case 'register':
        return `Are you sure you want to register for "${eventTitle}"?`;
      case 'unregister':
        return `Are you sure you want to unregister from "${eventTitle}"? This action cannot be undone.`;
      case 'cancel':
        return `Are you sure you want to cancel your pending registration for "${eventTitle}"? This action cannot be undone.`;
      default:
        return 'Are you sure you want to proceed?';
    }
  };

  const getConfirmButtonText = () => {
    switch (type) {
      case 'register': return 'Register';
      case 'unregister': return 'Unregister';
      case 'cancel': return 'Cancel Registration';
      default: return 'Confirm';
    }
  };

  const getConfirmButtonColor = (): 'primary' | 'error' => {
    switch (type) {
      case 'register': return 'primary';
      case 'unregister': 
      case 'cancel': 
        return 'error';
      default: return 'primary';
    }
  };

  if (!type) return null;

  return (
    <Dialog 
      open={open} 
      onClose={loading !== null ? undefined : onClose}
      disableEscapeKeyDown={loading !== null}
      aria-labelledby="confirm-action-dialog-title"
    >
      <DialogTitle id="confirm-action-dialog-title">{getTitle()}</DialogTitle>
      <DialogContent>
        <Typography>{getMessage()}</Typography>
      </DialogContent>
      <DialogActions>
        <Button 
          onClick={onClose} 
          disabled={loading !== null}
          aria-label="Cancel action"
        >
          Cancel
        </Button>
        <Button 
          onClick={onConfirm} 
          color={getConfirmButtonColor()}
          variant="contained" 
          disabled={loading !== null}
          startIcon={loading !== null ? <CircularProgress size={20} /> : null}
          aria-label={getConfirmButtonText()}
        >
          {loading !== null ? 'Processing...' : getConfirmButtonText()}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmActionDialog;
