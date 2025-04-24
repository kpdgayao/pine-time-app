import React from 'react';
import {
  Typography, Box, Dialog, DialogTitle, DialogContent,
  DialogActions, Button, Stack, IconButton
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { CircularProgress } from '@mui/material';
import dayjs from 'dayjs';
import { Event, Registration } from '../types/events';

type EventDetailsDialogProps = {
  open: boolean;
  onClose: () => void;
  event: Event | null;
  registrations: Registration[];
  onRegister: (eventId: number) => Promise<boolean>;
  setLastRegisteredEventId: (id: number) => void;
};

const EventDetailsDialog: React.FC<EventDetailsDialogProps> = ({
  open,
  onClose,
  event,
  registrations,
  onRegister,
  setLastRegisteredEventId
}) => {
  if (!event) return null;

  // Track loading state for this dialog's registration button
  const [isRegistering, setIsRegistering] = React.useState(false);

  const handleRegister = async () => {
    setIsRegistering(true);
    try {
      const success = await onRegister(event.id);
      if (success) {
        setLastRegisteredEventId(event.id);
        // Only close the dialog after successful registration
        onClose();
      }
    } catch (error) {
      console.error('Registration error:', error);
      // Error is handled by the registration hook
    } finally {
      setIsRegistering(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      aria-labelledby="event-details-dialog-title"
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', pr: 5 }}>
        <Box sx={{ flexGrow: 1 }}>{event.title}</Box>
        <IconButton aria-label="close" onClick={onClose} sx={{ ml: 1 }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        {event.image_url && (
          <Box sx={{ mb: 2, width: '100%', maxHeight: 350, overflow: 'hidden', borderRadius: 2 }}>
            <img
              src={event.image_url}
              alt={`Image for ${event.title}`}
              style={{ width: '100%', objectFit: 'cover', borderRadius: 8, maxHeight: 350 }}
              onError={e => { (e.currentTarget as HTMLImageElement).src = '/event-placeholder.png'; }}
            />
          </Box>
        )}
        <Typography variant="body1" sx={{ mb: 2 }}>
          {event.description || 'No description available.'}
        </Typography>
        <Stack spacing={1} direction="column">
          <Typography variant="body2">
            <strong>Date:</strong> {dayjs(event.start_time).format('MMM D, YYYY h:mm A')} - {dayjs(event.end_time).format('MMM D, YYYY h:mm A')}
          </Typography>
          <Typography variant="body2"><strong>Location:</strong> {event.location}</Typography>
          <Typography variant="body2"><strong>Capacity:</strong> {event.max_participants}</Typography>
          <Typography variant="body2"><strong>Price:</strong> {event.price === 0 ? 'Free' : `₱${event.price}`}</Typography>
          <Typography variant="body2"><strong>Points:</strong> {event.points_reward}</Typography>
        </Stack>
      </DialogContent>
      <DialogActions>
        {(() => {
          const now = dayjs();
          const eventEnded = dayjs(event.end_time).isBefore(now);
          const reg = registrations.find(r => r.event_id === event.id);
          const full = (event.registration_count ?? 0) >= event.max_participants;
          
          if (eventEnded) {
            return <Typography sx={{ mr: 2 }} color="text.secondary">Registration Closed</Typography>;
          }
          if (reg?.status === 'approved') {
            return <Typography sx={{ mr: 2 }} color="success.main">Already Registered</Typography>;
          }
          if (full) {
            return <Typography sx={{ mr: 2 }} color="text.secondary">Event Full</Typography>;
          }
          return (
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleRegister}
              disabled={isRegistering}
              startIcon={isRegistering ? <CircularProgress size={20} /> : null}
            >
              {isRegistering ? 'Registering...' : 'Register'}
            </Button>
          );
        })()}
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default EventDetailsDialog;
