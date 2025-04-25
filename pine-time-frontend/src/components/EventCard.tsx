import React, { useMemo } from 'react';

import { Box, Typography, Chip, Stack, Skeleton } from '@mui/material';
import PineTimeCard from './PineTimeCard';
import PineTimeButton from './PineTimeButton';
import { Event, Registration } from '../types/events';
import { FaCalendarAlt, FaClock, FaMapMarkerAlt, FaUsers } from 'react-icons/fa';
import { styled } from '@mui/material/styles';
import EventImage from './EventImage';

const AnimatedCard = styled(PineTimeCard)(({ theme }) => ({
  transition: 'transform 0.18s cubic-bezier(0.4,0,0.2,1), box-shadow 0.18s cubic-bezier(0.4,0,0.2,1)',
  '&:hover, &:focus': {
    transform: 'scale(1.035)',
    boxShadow: theme.shadows[8],
    zIndex: 2,
  },
  position: 'relative',
  borderRadius: 12,
}));

const StatusBadge = styled(Box)({
  position: 'absolute',
  top: 14,
  right: 14,
  zIndex: 3,
  minWidth: 0,
});

import { usePayment } from '../contexts/PaymentContext';

interface EventCardProps {
  event: Event;
  registration?: Registration;
  loading?: number | null;
  onRegister: (id: number) => void;
  onUnregister: (id: number) => void;
  onCancelPending: (id: number) => void;
  onPayNow?: (id: number) => void;
  handleOpenDialog?: (event: Event) => void;
  highlight?: boolean;
  dimmed?: boolean;
  isPaid?: boolean;
  sx?: any;
}

const EventCard: React.FC<EventCardProps> = React.memo(function EventCard({
  event,
  registration,
  loading,
  onRegister,
  onUnregister,
  onCancelPending,
  onPayNow,
  handleOpenDialog,
  highlight = false,
  dimmed = false,
  sx = {},
}) {
  // Use the payment context to check if registration is paid
  const { isRegistrationPaid } = usePayment();
  // Memoize expensive calculations
  const { isPending, isApproved, canRegister, status } = useMemo(() => {
    const past = new Date(event?.end_time || Date.now()) < new Date();
    const full = typeof event?.registration_count === 'number' && 
                event.registration_count >= (event?.max_participants || 0);
    const isPending = registration?.status === 'pending';
    const isApproved = registration?.status === 'approved';
    const isRejected = registration?.status === 'rejected';
    const canRegister = (!registration || 
                        registration.status === 'cancelled' || 
                        registration.status === 'rejected') && 
                        !past && !full;

    // Status logic for badge
    let status: null | { 
      label: string; 
      color: 'success' | 'warning' | 'error' | 'default'; 
      icon?: React.ReactNode 
    } = null;
    
    if (isApproved) status = { label: 'Registered', color: 'success', icon: <span role="img" aria-label="check">✔️</span> };
    else if (isPending) status = { label: 'Pending', color: 'warning', icon: <span role="img" aria-label="pending">⏳</span> };
    else if (isRejected) status = { label: 'Rejected', color: 'error', icon: <span role="img" aria-label="rejected">❌</span> };
    else if (past) status = { label: 'Ended', color: 'default', icon: <span role="img" aria-label="clock">⏰</span> };
    else if (full && !registration) status = { label: 'Full', color: 'warning', icon: <span role="img" aria-label="full">🚫</span> };
    
    return { past, full, isPending, isApproved, isRejected, canRegister, status };
  }, [event, registration]);

  return (
    <AnimatedCard
      elevation={highlight ? 6 : 2}
      tabIndex={0}
      aria-label={`Event card for ${event.title}`}
      sx={{
        flex: '1 1 100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        outline: highlight ? '2.5px solid #2E7D32' : 'none',
        background: dimmed ? '#f5f5f5' : 'background.paper',
        opacity: dimmed ? 0.6 : 1,
        filter: dimmed ? 'grayscale(40%)' : 'none',
        boxShadow: highlight ? 8 : 2,
        borderRadius: 3,
        minHeight: { xs: 280, sm: 320 },
        pointerEvents: dimmed ? 'none' : 'auto',
        ...sx,
      }}
    >
      {/* Status badge (top right) */}
      {status && (
        <StatusBadge sx={{
          position: 'absolute',
          top: 10,
          right: 10,
          zIndex: 10,
        }}>
          <Chip
            size="small"
            color={status.color}
            label={<>{status.icon} {status.label}</>}
            sx={{
              fontWeight: 700,
              px: 1.2,
              boxShadow: 2,
              fontSize: 13,
              borderRadius: 2,
              background: (theme) =>
                status.color === 'success'
                  ? theme.palette.success.main
                  : status.color === 'warning'
                  ? theme.palette.warning.main
                  : status.color === 'error'
                  ? theme.palette.error.main
                  : theme.palette.grey[400],
              color: (theme) =>
                status.color === 'default' ? theme.palette.text.primary : '#fff',
              letterSpacing: 0.5,
            }}
            aria-label={status.label}
          />
        </StatusBadge>
      )}
      {/* Event image with fallback */}
      {loading ? (
        <Skeleton variant="rectangular" width="100%" height={180} animation="wave" sx={{ borderTopLeftRadius: 12, borderTopRightRadius: 12, mb: 2 }} />
      ) : (
        <Box sx={{ width: '100%', mb: 2, overflow: 'hidden', borderTopLeftRadius: 12, borderTopRightRadius: 12 }}>
          <EventImage
            event={event}
            aspectRatio="16/9"
            borderRadius="12px 12px 0 0"
            showLoading={true}
          />
        </Box>
      )}
      {/* Card Content or skeleton */}
      <Box sx={{ p: 2, flexGrow: 1 }}>
        {loading ? (
          <>
            <Skeleton variant="text" width="70%" height={32} sx={{ mb: 1 }} />
            <Skeleton variant="text" width="40%" height={24} sx={{ mb: 1 }} />
            <Skeleton variant="text" width="90%" height={20} sx={{ mb: 1 }} />
            <Skeleton variant="rectangular" width="100%" height={36} sx={{ mb: 1 }} />
          </>
        ) : (
          <>
            <Box sx={{ mb: 1 }}>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 800,
                  color: '#2E7D32',
                  lineHeight: 1.15,
                  mb: 0.5,
                  cursor: handleOpenDialog ? 'pointer' : 'inherit',
                  textDecoration: handleOpenDialog ? 'underline dotted' : 'none',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  width: '100%',
                  maxWidth: '100%',
                  display: 'block',
                }}
                onClick={handleOpenDialog ? () => handleOpenDialog(event) : undefined}
                tabIndex={handleOpenDialog ? 0 : undefined}
                aria-label={handleOpenDialog ? `Open details for ${event.title}` : undefined}
                title={event.title}
              >
                {event.title}
              </Typography>
              {/* Tags below title */}
              <Stack direction="row" spacing={1} sx={{ mb: 1, flexWrap: 'wrap' }}>
                {event.event_type && (
                  <Chip size="small" label={event.event_type} color="primary" sx={{ fontWeight: 600 }} />
                )}
                {/* Show points reward with fallback for undefined values */}
                  <Chip 
                    size="small" 
                    color="success" 
                    label={`Points: ${event.points_reward !== undefined ? event.points_reward : 0}`} 
                    sx={{ fontWeight: 600 }} 
                  />
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
              <Typography
                variant="body2"
                sx={{
                  mb: 1,
                  color: 'text.secondary',
                  maxHeight: 56,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  wordBreak: 'break-word',
                }}
                title={event.description}
              >
                {event.description}
              </Typography>
            )}
            {/* Grouped info: Dates/Times and Location/Capacity */}
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 1.5, flexWrap: 'wrap', minHeight: 72 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: { xs: 1, sm: 0 } }}>
                <Chip
                  size="small"
                  icon={<FaCalendarAlt style={{ marginRight: 4 }} />}
                  label={`Start: ${new Date(event.start_time).toLocaleString()}`}
                  sx={{ fontWeight: 500, maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis' }}
                />
                <Chip
                  size="small"
                  icon={<FaClock style={{ marginRight: 4 }} />}
                  label={`End: ${new Date(event.end_time).toLocaleString()}`}
                  sx={{ fontWeight: 500, maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis' }}
                />
              </Stack>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: { xs: 1, sm: 0 } }}>
                <Chip
                  size="small"
                  icon={<FaMapMarkerAlt style={{ marginRight: 4 }} />}
                  label={event.location}
                  sx={{ fontWeight: 500, maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis' }}
                />
                <Chip
                  size="small"
                  icon={<FaUsers style={{ marginRight: 4 }} />}
                  label={`Capacity: ${event.max_participants}`}
                  sx={{ fontWeight: 500, maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis' }}
                />
              </Stack>
            </Stack>
          </>
        )}
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', px: 2, pb: 2 }}>
        {!loading && canRegister && (
          <PineTimeButton
            variantType="primary"
            size="small"
            onClick={() => onRegister(event.id)}
            disabled={loading === event.id}
          >
            Register
          </PineTimeButton>
        )}
        {!loading && isApproved && (
          <PineTimeButton
            variantType="secondary"
            size="small"
            onClick={() => onUnregister(event.id)}
            disabled={loading === event.id}
            sx={{ ml: 1 }}
          >
            Unregister
          </PineTimeButton>
        )}
        {!loading && isPending && (
          <>
            <PineTimeButton
              variantType="secondary"
              size="small"
              onClick={() => onCancelPending(event.id)}
              disabled={loading === event.id}
              sx={{ ml: 1 }}
            >
              Cancel
            </PineTimeButton>
            {/* Only show Pay Now button if:
                1. Event has a price
                2. onPayNow handler is provided
                3. Registration is not already paid
            */}
            {(event.price ?? 0) > 0 && onPayNow && registration && 
             !isRegistrationPaid(event.id, registration.id) && (
              <PineTimeButton
                variantType="primary"
                size="small"
                onClick={() => {
                  if (event && event.id) {
                    onPayNow(event.id);
                  }
                }}
                disabled={loading === event.id}
                sx={{ ml: 1, bgcolor: '#2E7D32' }}
                aria-label="Pay now for this event"
              >
                Pay Now
              </PineTimeButton>
            )}
            {/* Show payment submitted chip only if payment is marked as paid */}
            {(event.price ?? 0) > 0 && registration && 
             isRegistrationPaid(event.id, registration.id) && (
              <Chip 
                label="Payment Submitted" 
                color="success" 
                sx={{ ml: 1, fontWeight: 600 }} 
                aria-label="Payment has been submitted"
              />
            )}
          </>
        )}
      </Box>
    </AnimatedCard>
  );
});

export default EventCard;
