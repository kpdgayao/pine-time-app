import React, { useMemo } from 'react';
import { Box, Typography, useMediaQuery, useTheme } from '@mui/material';
import { Event, Registration } from '../types/events';
import EventCard from './EventCard';
import SkeletonCard from './SkeletonCard';

interface EventListProps {
  title: string;
  events: Event[];
  getRegistration: (event: Event) => Registration | undefined;
  loading: number | null; // Changed from boolean to match EventCard's expected prop type
  onRegister: (eventId: number) => void;
  onUnregister: (eventId: number) => void;
  onCancelPending: (eventId: number) => void;
  onPayNow: (eventId: number) => void;
  onOpenDetails: (event: Event) => void;
  isEventPaid?: (eventId: number, registrationId: number) => boolean;
  highlight?: boolean;
  dimmed?: boolean;
}

const EventList: React.FC<EventListProps> = ({
  title,
  events,
  getRegistration,
  loading,
  onRegister,
  onUnregister,
  onCancelPending,
  onPayNow,
  onOpenDetails,
  isEventPaid = () => false,
  highlight = false,
  dimmed = false
}) => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));
  const isMediumScreen = useMediaQuery(theme.breakpoints.between('sm', 'md'));
  
  // Determine number of skeleton cards to show based on screen size
  const skeletonCount = useMemo(() => {
    if (isSmallScreen) return 2;
    if (isMediumScreen) return 4;
    return 6;
  }, [isSmallScreen, isMediumScreen]);
  
  // Show skeleton cards while loading
  if (loading === -1) {
    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>{title}</Typography>
        <Box 
          sx={{ 
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              sm: 'repeat(auto-fill, minmax(320px, 1fr))',
              md: 'repeat(auto-fill, minmax(340px, 1fr))',
            },
            gap: 2 
          }}
        >
          {[...Array(skeletonCount)].map((_, index) => (
            <SkeletonCard key={index} type="event" />
          ))}
        </Box>
      </Box>
    );
  }
  
  // Return null if no events
  if (!events || events.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h6" sx={{ mb: 1 }}>{title}</Typography>
      <Box 
        sx={{ 
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(auto-fill, minmax(320px, 1fr))',
            md: 'repeat(auto-fill, minmax(340px, 1fr))',
          },
          gap: 2 
        }}
      >
        {events.map(event => {
          const registration = getRegistration(event);
          const isPaid = registration ? isEventPaid(event.id, registration.id) : false;
          
          return (
            <EventCard
              key={event.id}
              event={event}
              registration={registration}
              loading={loading}
              onRegister={onRegister}
              onUnregister={onUnregister}
              onCancelPending={onCancelPending}
              onPayNow={onPayNow}
              handleOpenDialog={() => onOpenDetails(event)}
              highlight={highlight}
              dimmed={dimmed}
              isPaid={isPaid}
              sx={{
                height: '100%', 
                minHeight: 320, 
                display: 'flex', 
                flexDirection: 'column', 
                maxWidth: 400, 
                width: '100%',
              }}
            />
          );
        })}
      </Box>
    </Box>
  );
};

export default React.memo(EventList);
