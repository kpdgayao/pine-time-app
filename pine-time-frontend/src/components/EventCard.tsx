import React from 'react';
import { Card, Box, Typography, Chip, Button, Stack } from '@mui/material';
import { Event, Registration } from '../types/events';
import { FaCalendarAlt, FaClock, FaMapMarkerAlt, FaUsers } from 'react-icons/fa';

interface EventCardProps {
  event: Event;
  registration?: Registration;
  loading?: number | null;
  onRegister: (id: number) => void;
  onUnregister: (id: number) => void;
  onCancelPending: (id: number) => void;
  handleOpenDialog?: (event: Event) => void;
}

const EventCard: React.FC<EventCardProps> = React.memo(({
  event,
  registration,
  loading,
  onRegister,
  onUnregister,
  onCancelPending,
  handleOpenDialog,
}) => {
  const past = new Date(event.end_time) < new Date();
  const full = typeof event.registration_count === 'number' && event.registration_count >= event.max_participants;
  const isPending = registration?.status === 'pending';
  const isApproved = registration?.status === 'approved';
  const isRejected = registration?.status === 'rejected';
  const canRegister =
    (!registration || registration.status === 'cancelled' || registration.status === 'rejected')
    && !past && !full;

  // Debug log for button visibility
  // eslint-disable-next-line no-console
  console.log('[EventCard Debug]', {
    eventId: event.id,
    registration,
    past,
    full,
    canRegister,
    end_time: event.end_time,
    registration_count: event.registration_count,
    max_participants: event.max_participants,
  });

  return (
    <Card
      elevation={2}
      sx={{
        flex: '1 1 350px',
        minWidth: 320,
        maxWidth: 420,
        mb: 3,
        width: { xs: '100%', sm: 'auto' },
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        transition: 'box-shadow 0.2s',
        '&:hover': { boxShadow: 6 },
        minHeight: 100,
      }}
      tabIndex={0}
      aria-label={`Event card for ${event.title}`}
    >
      {/* Event image */}
      {event.image_url ? (
        <Box sx={{ width: '100%', aspectRatio: '16/9', mb: 2, overflow: 'hidden', borderTopLeftRadius: 8, borderTopRightRadius: 8 }}>
          <img
            src={event.image_url}
            alt={event.title ? `Image for ${event.title}` : 'Event image'}
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block', borderTopLeftRadius: 8, borderTopRightRadius: 8 }}
            onError={e => { (e.currentTarget as HTMLImageElement).src = '/event-placeholder.png'; }}
          />
        </Box>
      ) : (
        <Box sx={{ width: '100%', aspectRatio: '16/9', mb: 2, overflow: 'hidden', borderTopLeftRadius: 8, borderTopRightRadius: 8, background: '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <img
            src={'/event-placeholder.png'}
            alt={'No event image available'}
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block', borderTopLeftRadius: 8, borderTopRightRadius: 8 }}
          />
        </Box>
      )}
      <Box sx={{ p: 2, flexGrow: 1 }}>
        <Box sx={{ mb: 1 }}>
          <Typography
            variant="h5"
            sx={{ fontWeight: 800, color: '#2E7D32', lineHeight: 1.15, mb: 0.5, cursor: handleOpenDialog ? 'pointer' : 'inherit', textDecoration: handleOpenDialog ? 'underline dotted' : 'none' }}
            onClick={handleOpenDialog ? () => handleOpenDialog(event) : undefined}
            tabIndex={handleOpenDialog ? 0 : undefined}
            aria-label={handleOpenDialog ? `Open details for ${event.title}` : undefined}
          >
            {event.title}
          </Typography>
          {/* Tags below title */}
          <Stack direction="row" spacing={1} sx={{ mb: 1, flexWrap: 'wrap' }}>
            {event.event_type && (
              <Chip size="small" label={event.event_type} color="primary" sx={{ fontWeight: 600 }} />
            )}
            {typeof event.points_reward === 'number' && (
              <Chip size="small" color="success" label={`Points: ${event.points_reward}`} sx={{ fontWeight: 600 }} />
            )}
            {typeof event.price === 'number' && (
              <Chip
                size="small"
                label={event.price === 0 ? 'Free' : `₱${event.price}`}
                sx={{ fontWeight: 600, ml: event.points_reward !== undefined ? 0 : 1 }}
                color={event.price === 0 ? 'success' : 'default'}
              />
            )}
          </Stack>
        </Box>
        {event.description && (
          <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary' }}>
            {event.description}
          </Typography>
        )}
        {/* Grouped info: Dates/Times and Location/Capacity */}
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 1, flexWrap: 'wrap', minHeight: 72 }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip
              size="small"
              icon={<FaCalendarAlt style={{ marginRight: 4 }} />}
              label={`Start: ${new Date(event.start_time).toLocaleString()}`}
              sx={{ fontWeight: 500 }}
            />
            <Chip
              size="small"
              icon={<FaClock style={{ marginRight: 4 }} />}
              label={`End: ${new Date(event.end_time).toLocaleString()}`}
              sx={{ fontWeight: 500 }}
            />
          </Stack>
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip
              size="small"
              icon={<FaMapMarkerAlt style={{ marginRight: 4 }} />}
              label={event.location}
              sx={{ fontWeight: 500 }}
            />
            <Chip
              size="small"
              icon={<FaUsers style={{ marginRight: 4 }} />}
              label={`Capacity: ${event.max_participants}`}
              sx={{ fontWeight: 500 }}
            />
          </Stack>
        </Stack>
        {/* Status Chips */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
          {isApproved && (
            <Chip icon={<span role="img" aria-label="check">✔️</span>} label="Registered" color="success" size="medium" sx={{ fontWeight: 600 }} />
          )}
          {isPending && (
            <Chip icon={<span role="img" aria-label="pending">⏳</span>} label="Pending Approval" color="warning" size="medium" sx={{ fontWeight: 600 }} />
          )}
          {isRejected && (
            <Chip icon={<span role="img" aria-label="rejected">❌</span>} label="Rejected" color="error" size="medium" sx={{ fontWeight: 600 }} />
          )}
          {past && (
            <Chip icon={<span role="img" aria-label="clock">⏰</span>} label="Event Ended" color="default" size="medium" sx={{ fontWeight: 600 }} />
          )}
          {full && !registration && (
            <Chip icon={<span role="img" aria-label="full">🚫</span>} label="Full" color="warning" size="medium" sx={{ fontWeight: 600 }} />
          )}
        </Box>
      </Box>
      {/* Action Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', px: 2, pb: 2 }}>
        {canRegister && (
          <Button
            variant="contained"
            color="success"
            size="small"
            onClick={() => onRegister(event.id)}
            disabled={loading === event.id}
            sx={{ mr: 1 }}
          >
            Register
          </Button>
        )}
        {isPending && (
          <Button
            variant="outlined"
            color="warning"
            size="small"
            onClick={() => onCancelPending(event.id)}
            disabled={loading === event.id}
            sx={{ mr: 1 }}
          >
            Cancel
          </Button>
        )}
        {isApproved && !past && (
          <Button
            variant="outlined"
            size="small"
            color="error"
            onClick={() => onUnregister(event.id)}
            disabled={loading === event.id}
            sx={{ mr: 1 }}
          >
            Unregister
          </Button>
        )}
      </Box>
    </Card>
  );
});

export default EventCard;
