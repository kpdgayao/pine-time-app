import React, { useState } from 'react';
import { Typography, Box, Alert, Dialog, Snackbar, Skeleton } from '@mui/material';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';
import { useEventRegistration } from '../hooks/useEventRegistration';
import ErrorBoundary from '../components/ErrorBoundary';
import { Event } from '../types/events';
import { useEvents } from '../hooks/useEvents';
import { usePayment } from '../contexts/PaymentContext';

// Import the new components we created
import EventFilters from '../components/EventFilters';
import EventList from '../components/EventList';
import EventDetailsDialog from '../components/EventDetailsDialog';
import PaymentDialog from '../components/PaymentDialog';
import ConfirmActionDialog from '../components/ConfirmActionDialog';

const EventsPage: React.FC = () => {
  const { showToast } = useToast();
  const registrationHook = useEventRegistration();
  
  // Use our custom hook for event data and filtering
  const { 
    loading, 
    error, 
    filters, 
    updateFilter, 
    eventTypes, 
    minPrice, 
    maxPrice, 
    categorizedEvents,
    registrations,
    refetch
  } = useEvents();
  
  // Use the payment context for payment operations
  const { isRegistrationPaid, refreshPaymentRecords } = usePayment();
  
  // Dialog states
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [openDetailsDialog, setOpenDetailsDialog] = useState(false);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [paymentEvent, setPaymentEvent] = useState<Event | null>(null);
  const [lastRegisteredEventId, setLastRegisteredEventId] = useState<number | null>(null);
  
  // Auth prompt state
  const [showAuthPrompt, setShowAuthPrompt] = useState(false);

  // Confirmation dialog state
  const [confirmAction, setConfirmAction] = useState<{
    type: 'register' | 'unregister' | 'cancel';
    eventId: number;
    eventTitle: string;
  } | null>(null);

  // Handle notifications from registration hook
  React.useEffect(() => {
    if (registrationHook.state.success) {
      showToast(`✅ ${registrationHook.state.success}`, 'success');
      refetch();
      registrationHook.clearMessages();
    }
    if (registrationHook.state.error) {
      let emoji = '❌';
      if (registrationHook.state.error.toLowerCase().includes('already registered')) emoji = '⚠️';
      if (registrationHook.state.error.toLowerCase().includes('full')) emoji = '⚠️';
      if (registrationHook.state.error.toLowerCase().includes('past')) emoji = '⏰';
      showToast(`${emoji} ${registrationHook.state.error}`, 'error');
    }
  }, [registrationHook.state.success, registrationHook.state.error, showToast, refetch, registrationHook]);

  // Helper function to find an event by ID across all categories
  const findEventById = (eventId: number): Event | undefined => {
    return [...categorizedEvents.upcomingUnregistered, 
            ...categorizedEvents.upcomingRegistered,
            ...categorizedEvents.pastEvents]
      .find(e => e.id === eventId);
  };

  // Show payment dialog after successful registration for a paid event
  React.useEffect(() => {
    // Only proceed if we have a newly registered event ID that hasn't been processed yet
    if (lastRegisteredEventId !== null && !showPaymentDialog) {
      // Find the event in all categories
      const event = findEventById(lastRegisteredEventId);
      
      if (event && (event.price ?? 0) > 0) {
        const registration = categorizedEvents.getRegistration(event);
        
        if (registration) {
          // Check if this registration is already marked as paid
          const alreadyPaid = isRegistrationPaid(event.id, registration.id);
          
          if (!alreadyPaid) {
            // Important: Set these in sequence to ensure the dialog opens properly
            setPaymentEvent(event);
            setTimeout(() => {
              setShowPaymentDialog(true);
            }, 100); // Small delay to ensure state updates properly
          } else {
            // If already paid, clear the lastRegisteredEventId
            setLastRegisteredEventId(null);
          }
        } else {
          // If there's no registration, clear the lastRegisteredEventId
          setLastRegisteredEventId(null);
        }
      } else {
        // If event doesn't exist or has no price, clear lastRegisteredEventId
        setLastRegisteredEventId(null);
      }
    }
  }, [lastRegisteredEventId, categorizedEvents, showPaymentDialog, isRegistrationPaid]);

  // Dialog handlers
  const handleOpenDetailsDialog = (event: Event) => {
    if (!user && (event.price ?? 0) > 0) {
      // For paid events, require authentication before showing details
      setShowAuthPrompt(true);
      return;
    }
    setSelectedEvent(event);
    setOpenDetailsDialog(true);
  };

  const handleCloseDetailsDialog = () => {
    setOpenDetailsDialog(false);
    setSelectedEvent(null);
  };

  const handleOpenPaymentDialog = (eventId: number) => {
    const event = findEventById(eventId);
    if (event !== undefined) {
      setPaymentEvent(event);
      setShowPaymentDialog(true);
    }
  };

  const handleClosePaymentDialog = () => {
    // Batch state updates to prevent re-renders
    setShowPaymentDialog(false);
    setLastRegisteredEventId(null);
    setPaymentEvent(null);
  };

  // Check if user is authenticated and show auth prompt if needed
  const { user } = useAuth();
  
  const checkAuthAndProceed = (callback: () => void) => {
    if (!user) {
      setShowAuthPrompt(true);
      return false;
    }
    callback();
    return true;
  };

  const handleConfirmAction = async () => {
    if (!confirmAction) return;
    
    const { type, eventId } = confirmAction;
    setConfirmAction(null); // Close dialog
    
    // Helper function to find event by ID across all event categories
    const findEventById = (id: number) => {
      return [...categorizedEvents.upcomingRegistered, 
              ...categorizedEvents.upcomingUnregistered,
              ...categorizedEvents.pastEvents].find(e => e.id === id);
    };
    
    try {
      if (type === 'register') {
        console.log('Registering for event:', eventId);
        const success = await registrationHook.register(eventId);
        if (success) {
          console.log('Registration successful, setting lastRegisteredEventId:', eventId);
          setLastRegisteredEventId(eventId);
          // Immediately refetch to update the UI with the new registration
          await refetch();
        } else {
          console.log('Registration failed or was cancelled');
        }
      } else if (type === 'unregister') {
        // Find the event object to check cancellation policy
        const event = findEventById(eventId);
        if (event) {
          const success = await registrationHook.unregister(eventId, event);
          if (success) {
            await refetch(); // Refetch after unregistration
          }
        } else {
          console.error('Event not found for unregistration:', eventId);
        }
      } else if (type === 'cancel') {
        // Find the event object to check cancellation policy
        const event = findEventById(eventId);
        if (event) {
          const success = await registrationHook.cancelPending(eventId, event);
          if (success) {
            await refetch(); // Refetch after cancellation
          }
        } else {
          console.error('Event not found for cancellation:', eventId);
        }
      }
    } catch (error) {
      console.error('Action error:', error);
      showToast(`❌ An error occurred while processing your request`, 'error');
    } finally {
      setConfirmAction(null);
    }
  };

  // Loading state
  if (loading) {
    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h5">Events</Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mt: 1 }}>
          {[...Array(4)].map((_, idx) => (
            <Box
              key={idx}
              sx={{
                flex: '1 1 300px',
                minWidth: 250,
                maxWidth: 400,
                mb: 2,
              }}
            >
              <Skeleton variant="rectangular" height={180} />
            </Box>
          ))}
        </Box>
      </Box>
    );
  }

  // Error state
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <ErrorBoundary>
      <Box
        sx={{
          mt: 3,
          px: { xs: 2, sm: 3, md: 4 },
          py: { xs: 2, sm: 3 },
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Box
          sx={{
            width: '100%',
            maxWidth: { xs: '100%', sm: 680, md: 1080, xl: 1280 },
            mx: 'auto',
          }}
        >
          <Typography variant="h5" sx={{ mb: { xs: 2, sm: 3 } }}>Events</Typography>
          
          {/* Event Filters */}
          <EventFilters
            search={filters.search}
            setSearch={(value) => updateFilter('search', value)}
            eventType={filters.eventType}
            setEventType={(value) => updateFilter('eventType', value)}
            location={filters.location}
            setLocation={(value) => updateFilter('location', value)}
            dateRange={filters.dateRange}
            setDateRange={(value) => updateFilter('dateRange', value)}
            priceRange={filters.priceRange}
            setPriceRange={(value) => updateFilter('priceRange', value)}
            sortBy={filters.sortBy}
            setSortBy={(value) => updateFilter('sortBy', value)}
            eventTypes={eventTypes}
            minPrice={minPrice}
            maxPrice={maxPrice}
          />
          
          {/* No events message */}
          {categorizedEvents.upcomingUnregistered.length === 0 && 
           categorizedEvents.upcomingRegistered.length === 0 && 
           categorizedEvents.pastEvents.length === 0 && (
            <Alert severity="info">No events found matching your criteria.</Alert>
          )}
          
          {/* Event Lists */}
          <EventList
            title="Upcoming Events (Not Registered)"
            events={categorizedEvents.upcomingUnregistered}
            getRegistration={categorizedEvents.getRegistration}
            loading={registrationHook.state.loading}
            onRegister={(eventId) => {
              checkAuthAndProceed(() => {
                const event = categorizedEvents.upcomingUnregistered.find(e => e.id === eventId);
                if (event !== undefined) {
                  setConfirmAction({
                    type: 'register',
                    eventId,
                    eventTitle: event.title
                  });
                }
              });
            }}
            isEventPaid={isRegistrationPaid}
            onUnregister={(eventId) => {
              const event = categorizedEvents.upcomingUnregistered.find(e => e.id === eventId);
              if (event !== undefined) {
                setConfirmAction({
                  type: 'unregister',
                  eventId,
                  eventTitle: event.title
                });
              }
            }}
            onCancelPending={(eventId) => {
              const event = categorizedEvents.upcomingUnregistered.find(e => e.id === eventId);
              if (event !== undefined) {
                setConfirmAction({
                  type: 'cancel',
                  eventId,
                  eventTitle: event.title
                });
              }
            }}
            onPayNow={(eventId) => {
              // Only show payment dialog if we haven't already paid
              const event = findEventById(eventId);
              const registration = event ? categorizedEvents.getRegistration(event) : undefined;
              const alreadyPaid = registration ? isRegistrationPaid(eventId, registration.id) : false;
              if (!alreadyPaid) {
                checkAuthAndProceed(() => handleOpenPaymentDialog(eventId));
              }
            }}
            onOpenDetails={(event) => checkAuthAndProceed(() => {              
              // Ensure event is defined before passing to dialog handler
              if (event) handleOpenDetailsDialog(event);
            })}
            highlight
          />
          
          <EventList
            title="Your Upcoming Events"
            events={categorizedEvents.upcomingRegistered}
            getRegistration={categorizedEvents.getRegistration}
            loading={registrationHook.state.loading}
            onRegister={(eventId) => {
              const event = categorizedEvents.upcomingRegistered.find(e => e.id === eventId);
              if (event !== undefined) {
                setConfirmAction({
                  type: 'register',
                  eventId,
                  eventTitle: event.title
                });
              }
            }}
            onUnregister={(eventId) => {
              const event = categorizedEvents.upcomingRegistered.find(e => e.id === eventId);
              if (event !== undefined) {
                setConfirmAction({
                  type: 'unregister',
                  eventId,
                  eventTitle: event.title
                });
              }
            }}
            onCancelPending={(eventId) => {
              const event = categorizedEvents.upcomingRegistered.find(e => e.id === eventId);
              if (event !== undefined) {
                setConfirmAction({
                  type: 'cancel',
                  eventId,
                  eventTitle: event.title
                });
              }
            }}
            onPayNow={(eventId) => {
              // Only show payment dialog if we haven't already paid
              const event = findEventById(eventId);
              const registration = event ? categorizedEvents.getRegistration(event) : undefined;
              const alreadyPaid = registration ? isRegistrationPaid(eventId, registration.id) : false;
              if (!alreadyPaid) {
                checkAuthAndProceed(() => handleOpenPaymentDialog(eventId));
              }
            }}
            isEventPaid={isRegistrationPaid}
            onOpenDetails={(event) => checkAuthAndProceed(() => {              
              // Ensure event is defined before passing to dialog handler
              if (event) handleOpenDetailsDialog(event);
            })}
          />
          
          <EventList
            title="Past Events"
            events={categorizedEvents.pastEvents}
            getRegistration={categorizedEvents.getRegistration}
            loading={registrationHook.state.loading}
            onRegister={(eventId) => {
              const event = categorizedEvents.pastEvents.find(e => e.id === eventId);
              if (event !== undefined) {
                setConfirmAction({
                  type: 'register',
                  eventId,
                  eventTitle: event.title
                });
              }
            }}
            onUnregister={(eventId) => {
              const event = categorizedEvents.pastEvents.find(e => e.id === eventId);
              if (event !== undefined) {
                setConfirmAction({
                  type: 'unregister',
                  eventId,
                  eventTitle: event.title
                });
              }
            }}
            onCancelPending={(eventId) => {
              const event = categorizedEvents.pastEvents.find(e => e.id === eventId);
              if (event !== undefined) {
                setConfirmAction({
                  type: 'cancel',
                  eventId,
                  eventTitle: event.title
                });
              }
            }}
            onPayNow={(eventId) => {
              // Only show payment dialog if we haven't already paid
              const event = findEventById(eventId);
              const registration = event ? categorizedEvents.getRegistration(event) : undefined;
              const alreadyPaid = registration ? isRegistrationPaid(eventId, registration.id) : false;
              if (!alreadyPaid) {
                checkAuthAndProceed(() => handleOpenPaymentDialog(eventId));
              }
            }}
            isEventPaid={isRegistrationPaid}
            onOpenDetails={(event) => checkAuthAndProceed(() => {              
              // Ensure event is defined before passing to dialog handler
              if (event) handleOpenDetailsDialog(event);
            })}
            dimmed
          />
        </Box>
      </Box>
      
      {/* Event Details Dialog */}
      <EventDetailsDialog
        open={openDetailsDialog}
        onClose={handleCloseDetailsDialog}
        event={selectedEvent}
        registrations={registrations}
        onRegister={registrationHook.register}
        setLastRegisteredEventId={setLastRegisteredEventId}
      />
      
      {/* Payment Dialog */}
      <PaymentDialog
        open={showPaymentDialog}
        onClose={handleClosePaymentDialog}
        event={paymentEvent}
        registrations={registrations}
        onSuccess={() => {
          // First close the dialog
          setShowPaymentDialog(false);
          // Then clear the event ID state
          setLastRegisteredEventId(null);
          setPaymentEvent(null);
          // Refresh payment records
          refreshPaymentRecords();
          // Finally refetch the data
          refetch();
        }}
      />
      
      {/* Confirm Action Dialog */}
      {confirmAction && (
        <ConfirmActionDialog
          open={!!confirmAction}
          onClose={() => setConfirmAction(null)}
          type={confirmAction.type}
          eventTitle={confirmAction.eventTitle}
          loading={registrationHook.state.loading}
          onConfirm={handleConfirmAction}
        />
      )}
      
      {/* Auth Prompt Dialog */}
      <Dialog 
        open={showAuthPrompt} 
        onClose={() => setShowAuthPrompt(false)} 
        maxWidth="xs" 
        fullWidth
      >
        <Box sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Login or Register Required
          </Typography>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Please log in or register to view event details and register for events.
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
            <Box component="a" href="/login" sx={{ textDecoration: 'none' }}>
              <Typography variant="button" color="primary">Login</Typography>
            </Box>
            <Box component="a" href="/register" sx={{ textDecoration: 'none', ml: 2 }}>
              <Typography variant="button" color="primary">Register</Typography>
            </Box>
          </Box>
        </Box>
      </Dialog>
      
      {/* Toast Notifications */}
      <Snackbar
        open={!!registrationHook.state.error || !!registrationHook.state.success}
        autoHideDuration={4000}
        onClose={registrationHook.clearMessages}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={registrationHook.clearMessages} 
          severity={registrationHook.state.error ? "error" : "success"} 
          sx={{ width: "100%" }}
        >
          {registrationHook.state.error || registrationHook.state.success}
        </Alert>
      </Snackbar>
    </ErrorBoundary>
  );
};

export default EventsPage;