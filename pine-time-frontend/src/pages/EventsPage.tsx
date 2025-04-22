import React, { useEffect, useState, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Typography, TextField, Select, MenuItem, Box, Snackbar, Alert, Skeleton, Slider, InputLabel, FormControl, Dialog, DialogTitle, DialogContent, DialogActions, Button, IconButton, Stack } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs, { Dayjs } from 'dayjs';

import EventCard from '../components/EventCard';
import { useEventRegistration } from '../hooks/useEventRegistration';
import { useToast } from '../contexts/ToastContext';
import { extractErrorMessage } from '../utils/extractErrorMessage';
import { Event, Registration } from '../types/events';
import api from '../api/client';

const EventsPage: React.FC = () => {
  const { showToast } = useToast();
  const { user } = useAuth();
  const [showAuthPrompt, setShowAuthPrompt] = useState(false);
  const [events, setEvents] = useState<Event[]>([]);
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [eventType, setEventType] = useState('');
  const [location, setLocation] = useState('');
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null]>([null, null]);
  const [priceRange, setPriceRange] = useState<number[]>([0, 1000]);
  const [sortBy, setSortBy] = useState('start-soonest');

  const { state, register, unregister, cancelPending, clearMessages } = useEventRegistration();
  const { loading: regLoading, error: regError, success: regSuccess } = state;

  // Toast feedback for event registration
  useEffect(() => {
    if (regSuccess) {
      showToast(`✅ ${regSuccess}`, 'success');
    }
    if (regError) {
      let emoji = '❌';
      if (regError.toLowerCase().includes('already registered')) emoji = '⚠️';
      if (regError.toLowerCase().includes('full')) emoji = '⚠️';
      if (regError.toLowerCase().includes('past')) emoji = '⏰';
      showToast(`${emoji} ${regError}`, 'error');
    }
  }, [regSuccess, regError, showToast]);

  // Payment dialog state
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentChannel, setPaymentChannel] = useState('GCash');

  const [paymentSubmitting, setPaymentSubmitting] = useState(false);
  const [paymentMsg, setPaymentMsg] = useState('');

  // Dialog handlers
  const handleOpenDialog = (eventData: Event) => {
    if (!user) {
      setShowAuthPrompt(true);
      return;
    }
    setSelectedEvent(eventData);
    setOpenDialog(true);
  };
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedEvent(null);
  };



  // Get min/max price for slider
  const minPrice = useMemo(() => Math.min(...events.map(e => e.price ?? 0), 0), [events]);
  const maxPrice = useMemo(() => Math.max(...events.map(e => e.price ?? 0), 1000), [events]);
  useEffect(() => {
    setPriceRange([minPrice, maxPrice]);
  }, [minPrice, maxPrice]);
  // Payment registration handler
  const handlePaymentSubmit = async () => {
    console.log('[DEBUG] handlePaymentSubmit called', {
      selectedEvent,
      paymentModalEvent,
      paymentSubmitting,
      paymentAmount,
      paymentChannel
    });
    if (!paymentModalEvent) {
      console.log('[DEBUG] No paymentModalEvent, aborting payment submit');
      return;
    }
    setPaymentSubmitting(true);
    setPaymentMsg('');
    try {
      const registration = registrations.find(r => r.event_id === paymentModalEvent.id && r.status === 'pending');
      if (!registration) {
        showToast('❗ No pending registration found for this event.', 'error');
        setPaymentSubmitting(false);
        console.log('[DEBUG] No pending registration found for event', paymentModalEvent.id);
        return;
      }
      console.log('[DEBUG] Submitting payment with payload:', {
        registration_id: registration.id,
        user_id: registration.user_id,
        event_id: paymentModalEvent.id,
        amount_paid: parseFloat(paymentAmount),
        payment_channel: paymentChannel
      });
      await api.post('/payments/payments/register', {
        registration_id: registration.id,
        user_id: registration.user_id,
        event_id: paymentModalEvent.id,
        amount_paid: parseFloat(paymentAmount),
        payment_channel: paymentChannel
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      showToast('✅ Payment submitted! Awaiting admin verification. 🪙', 'success');
      setShowPaymentDialog(false);
      console.log('[DEBUG] Payment submitted successfully');
    } catch (err: any) {
      showToast(`❌ ${extractErrorMessage(err)}`, 'error');
      console.error('[DEBUG] Payment submission error:', err);
    } finally {
      setPaymentSubmitting(false);
    }
  };


  // Extracted fetch logic into a reusable function
  const fetchEventsAndRegistrations = async () => {
    setLoading(true);
    setError(null);
    try {
      // Always fetch events
      const eventsRes = await api.get('/events/');
      const eventsData = Array.isArray(eventsRes.data)
        ? eventsRes.data
        : eventsRes.data?.items || [];
      setEvents(eventsData);

      // Only fetch registrations if authenticated
      if (user) {
        try {
          const regsRes = await api.get('/registrations/users/me/registrations');
          setRegistrations(Array.isArray(regsRes.data) ? regsRes.data : regsRes.data?.items || []);
        } catch (regErr) {
          setRegistrations([]); // If failed, just set empty
        }
      } else {
        setRegistrations([]); // Clear for unauthenticated users
      }
    } catch (err) {
      setError(extractErrorMessage(err));
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchEventsAndRegistrations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // Refetch when registration/unregistration/cancellation is successful
  useEffect(() => {
    if (regSuccess) {
      fetchEventsAndRegistrations();
      clearMessages();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [regSuccess]);

  // Track the last registered event to robustly trigger payment modal
  const [lastRegisteredEventId, setLastRegisteredEventId] = useState<number | null>(null);
  const [paymentModalEvent, setPaymentModalEvent] = useState<Event | null>(null);

  // Handle closing the payment modal and reset event/payment state
  const handleClosePaymentDialog = () => {
    console.log('[DEBUG] Closing payment dialog');
    setShowPaymentDialog(false);
    setLastRegisteredEventId(null);
    setPaymentModalEvent(null);
  };

  // Show payment modal after registrations are updated and pending registration for a paid event is found
  useEffect(() => {
    console.log('[DEBUG] useEffect - registrations updated', { lastRegisteredEventId, events, registrations });
    if (lastRegisteredEventId) {
      const eventObj = events.find(e => e.id === lastRegisteredEventId);
      if (eventObj && (eventObj.price ?? 0) > 0) {
        const reg = registrations.find(
          r => r.event_id === lastRegisteredEventId && r.status === 'pending'
        );
        console.log('[DEBUG] Found registration for modal?', reg);
        if (reg) {
          console.log('[DEBUG] Opening payment modal for event', eventObj);
          setPaymentModalEvent(eventObj);
          setShowPaymentDialog(true);
          // Do NOT reset lastRegisteredEventId here
        }
      }
    }
  }, [registrations, events, lastRegisteredEventId]);

  const filteredEvents = useMemo(() => {
    let filtered = events.filter(e => e.is_active);
    // Event type
    if (eventType) filtered = filtered.filter(e => e.event_type === eventType);
    // Search
    if (search) filtered = filtered.filter(e =>
      e.title.toLowerCase().includes(search.toLowerCase()) ||
      e.description.toLowerCase().includes(search.toLowerCase()) ||
      e.location.toLowerCase().includes(search.toLowerCase())
    );
    // Location
    if (location) filtered = filtered.filter(e => e.location.toLowerCase().includes(location.toLowerCase()));
    // Date range
    if (dateRange[0]) filtered = filtered.filter(e => dayjs(e.start_time).isAfter(dateRange[0]!.startOf('day').subtract(1, 'ms')));
    if (dateRange[1]) filtered = filtered.filter(e => dayjs(e.end_time).isBefore(dateRange[1]!.endOf('day').add(1, 'ms')));
    // Price range
    filtered = filtered.filter(e => (e.price ?? 0) >= priceRange[0] && (e.price ?? 0) <= priceRange[1]);
    // Sorting
    switch (sortBy) {
      case 'start-soonest':
        filtered = filtered.slice().sort((a, b) => dayjs(a.start_time).diff(dayjs(b.start_time)));
        break;
      case 'start-latest':
        filtered = filtered.slice().sort((a, b) => dayjs(b.start_time).diff(dayjs(a.start_time)));
        break;
      case 'title-az':
        filtered = filtered.slice().sort((a, b) => a.title.localeCompare(b.title));
        break;
      case 'price-low':
        filtered = filtered.slice().sort((a, b) => (a.price ?? 0) - (b.price ?? 0));
        break;
      case 'price-high':
        filtered = filtered.slice().sort((a, b) => (b.price ?? 0) - (a.price ?? 0));
        break;
    }
    return filtered;
  }, [events, search, eventType, location, dateRange, priceRange, sortBy]);

  // Unique event types for filter
  const eventTypes = useMemo(() => Array.from(new Set(events.map(e => e.event_type))).filter(Boolean), [events]);

  // Loading skeletons
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
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
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
        {/* Responsive filter bar */}
        <Box
          sx={{
            display: 'flex',
            flexWrap: { xs: 'wrap', sm: 'nowrap' },
            gap: { xs: 1.5, sm: 2 },
            mb: { xs: 2, sm: 3 },
            alignItems: 'center',
            background: { xs: 'transparent', sm: 'background.surface' },
            px: { xs: 0, sm: 2 },
            py: { xs: 0, sm: 1 },
            borderRadius: { xs: 0, sm: 2 },
            boxShadow: { xs: 'none', sm: 1 },
            position: 'relative',
          }}
        >
          {/* On mobile, allow filter collapse/expand (simple version) */}
          {/* Could add a toggle button for advanced collapse, but keep inline for now */}
          <TextField
            label="Search"
            value={search}
            onChange={e => setSearch(e.target.value)}
            size="small"
            sx={{ flex: { xs: '1 1 100%', sm: '0 1 180px' } }}
          />
          <Select
            value={eventType}
            onChange={e => setEventType(e.target.value)}
            displayEmpty
            size="small"
            sx={{ minWidth: 120 }}
          >
            <MenuItem value="">All Types</MenuItem>
            {eventTypes.map(type => (
              <MenuItem key={type} value={type}>{type}</MenuItem>
            ))}
          </Select>
          <DatePicker
            label="Start Date"
            value={dateRange[0]}
            onChange={date => setDateRange([date, dateRange[1]])}
            slotProps={{ textField: { size: 'small' } }}
          />
          <DatePicker
            label="End Date"
            value={dateRange[1]}
            onChange={date => setDateRange([dateRange[0], date])}
            slotProps={{ textField: { size: 'small' } }}
          />
          <TextField
            label="Location"
            value={location}
            onChange={e => setLocation(e.target.value)}
            size="small"
            sx={{ flex: { xs: '1 1 100%', sm: '0 1 160px' } }}
          />
          <Box sx={{ minWidth: 160, px: { xs: 0, sm: 1 } }}>
            <Typography variant="body2" sx={{ mb: 0.5 }}>Price Range</Typography>
            <Slider
              value={priceRange}
              min={minPrice}
              max={maxPrice}
              step={10}
              onChange={(_, val) => setPriceRange(val as number[])}
              valueLabelDisplay="auto"
              size="small"
            />
          </Box>
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel id="sort-by-label">Sort By</InputLabel>
            <Select
              labelId="sort-by-label"
              value={sortBy}
              label="Sort By"
              onChange={e => setSortBy(e.target.value)}
            >
              <MenuItem value="start-soonest">Start Date (Soonest)</MenuItem>
              <MenuItem value="start-latest">Start Date (Latest)</MenuItem>
              <MenuItem value="title-az">Event Title (A-Z)</MenuItem>
              <MenuItem value="price-low">Price (Low to High)</MenuItem>
              <MenuItem value="price-high">Price (High to Low)</MenuItem>
            </Select>
          </FormControl>
        </Box>
        {/* Responsive grid layout for event cards */}
        <Box
          sx={{
            width: '100%',
            maxWidth: { xs: '100%', sm: 680, md: 1080, xl: 1280 },
            mx: 'auto',
            px: { xs: 1, sm: 2, md: 3 }, // horizontal padding
            display: 'grid',
            justifyContent: 'center',
            gridTemplateColumns: {
              xs: '1fr',
              sm: 'repeat(auto-fit, minmax(320px, 1fr))',
              md: 'repeat(auto-fit, minmax(340px, 1fr))',
              lg: 'repeat(auto-fit, minmax(360px, 1fr))',
            },
            gap: { xs: 2, sm: 2.5 },
            alignItems: 'stretch',
            minHeight: 240,
          }}
        >
          {filteredEvents.length === 0 && (
            <Box gridColumn={{ xs: '1/-1' }}><Alert severity="info">No events found.</Alert></Box>
          )}
          {/* Split events into sections */}
{(() => {
  const now = dayjs();
  const getReg = (event: Event) => {
    const regs = registrations.filter(r => r.event_id === event.id);
    return (
      regs.find(r => r.status === 'approved') ||
      regs.find(r => r.status === 'pending') ||
      regs.find(r => r.status === 'rejected') ||
      regs.find(r => r.status === 'cancelled') ||
      undefined
    );
  };
  const upcomingUnregistered = filteredEvents.filter(e => dayjs(e.end_time).isAfter(now) && !getReg(e));
  const upcomingRegistered = filteredEvents.filter(e => dayjs(e.end_time).isAfter(now) && getReg(e));
  const pastEvents = filteredEvents.filter(e => dayjs(e.end_time).isBefore(now));

  return (
    <>
      {/* Upcoming events not registered */}
      {upcomingUnregistered.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>Upcoming Events (Not Registered)</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {upcomingUnregistered.map(event => (
              <EventCard
                key={event.id}
                event={event}
                registration={getReg(event)}
                loading={regLoading}
                onRegister={async (eventId: number) => {
                  const success = await register(eventId);
                  if (success) setLastRegisteredEventId(eventId);
                }}
                onUnregister={unregister}
                onCancelPending={cancelPending}
                handleOpenDialog={handleOpenDialog}
                highlight
                sx={{
                  height: '100%', minHeight: 320, display: 'flex', flexDirection: 'column', maxWidth: 400, mx: 'auto', my: 1,
                }}
              />
            ))}
          </Box>
        </Box>
      )}
      {/* Upcoming events registered */}
      {upcomingRegistered.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>Your Upcoming Events</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {upcomingRegistered.map(event => (
              <EventCard
                key={event.id}
                event={event}
                registration={getReg(event)}
                loading={regLoading}
                onRegister={async (eventId: number) => {
                  const success = await register(eventId);
                  if (success) setLastRegisteredEventId(eventId);
                }}
                onUnregister={unregister}
                onCancelPending={cancelPending}
                handleOpenDialog={handleOpenDialog}
                sx={{
                  height: '100%', minHeight: 320, display: 'flex', flexDirection: 'column', maxWidth: 400, mx: 'auto', my: 1,
                }}
              />
            ))}
          </Box>
        </Box>
      )}
      {/* Past events */}
      {pastEvents.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>Past Events</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {pastEvents.map(event => (
              <EventCard
                key={event.id}
                event={event}
                registration={getReg(event)}
                loading={regLoading}
                onRegister={async (eventId: number) => {
                  const success = await register(eventId);
                  if (success) setLastRegisteredEventId(eventId);
                }}
                onUnregister={unregister}
                onCancelPending={cancelPending}
                handleOpenDialog={handleOpenDialog}
                dimmed
                sx={{
                  height: '100%', minHeight: 320, display: 'flex', flexDirection: 'column', maxWidth: 400, mx: 'auto', my: 1,
                }}
              />
            ))}
          </Box>
        </Box>
      )}
    </>
  );
})()}
        </Box>
      </Box>
      {/* ...rest of the dialogs/snackbar remain unchanged... */}
    {/* Event Details Dialog */}
    <Dialog
      open={openDialog}
      onClose={handleCloseDialog}
      maxWidth="md"
      fullWidth
      aria-labelledby="event-details-dialog-title"
    >
      {selectedEvent ? (
        <React.Fragment>
          <DialogTitle sx={{ display: 'flex', alignItems: 'center', pr: 5 }}>
            <Box sx={{ flexGrow: 1 }}>{selectedEvent!.title}</Box>
            <IconButton aria-label="close" onClick={handleCloseDialog} sx={{ ml: 1 }}>
              <CloseIcon />
            </IconButton>
          </DialogTitle>
          <DialogContent dividers>
            {selectedEvent!.image_url && (
              <Box sx={{ mb: 2, width: '100%', maxHeight: 350, overflow: 'hidden', borderRadius: 2 }}>
                <img
                  src={selectedEvent!.image_url}
                  alt={`Image for ${selectedEvent!.title}`}
                  style={{ width: '100%', objectFit: 'cover', borderRadius: 8, maxHeight: 350 }}
                  onError={e => { (e.currentTarget as HTMLImageElement).src = '/event-placeholder.png'; }}
                />
              </Box>
            )}
            <Typography variant="body1" sx={{ mb: 2 }}>
              {selectedEvent!.description || 'No description available.'}
            </Typography>
            <Stack spacing={1} direction="column">
              <Typography variant="body2"><strong>Date:</strong> {dayjs(selectedEvent!.start_time).format('MMM D, YYYY h:mm A')} - {dayjs(selectedEvent!.end_time).format('MMM D, YYYY h:mm A')}</Typography>
              <Typography variant="body2"><strong>Location:</strong> {selectedEvent!.location}</Typography>
              <Typography variant="body2"><strong>Capacity:</strong> {selectedEvent!.max_participants}</Typography>
              <Typography variant="body2"><strong>Price:</strong> {selectedEvent!.price === 0 ? 'Free' : `₱${selectedEvent!.price}`}</Typography>
              <Typography variant="body2"><strong>Points:</strong> {selectedEvent!.points_reward}</Typography>
            </Stack>
          </DialogContent>
          <DialogActions>
            {/* Registration Button Logic */}
            {(() => {
              const now = dayjs();
              const eventEnded = dayjs(selectedEvent!.end_time).isBefore(now);
              const reg = registrations.find(r => r.event_id === selectedEvent!.id);
              const full = (selectedEvent!.registration_count ?? 0) >= selectedEvent!.max_participants;
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
                <Button variant="contained" color="primary" onClick={() => { 
                  setSelectedEvent(selectedEvent!); 
                  register(selectedEvent!.id).then(success => {
                    if (success) setLastRegisteredEventId(selectedEvent!.id);
                  });
                  handleCloseDialog(); 
                }}>
                  Register
                </Button>
              );
            })()}
            <Button onClick={handleCloseDialog}>Close</Button>
          </DialogActions>
        </React.Fragment>
      ) : null}
    </Dialog>

    {/* Auth Prompt Dialog */}
    <Dialog open={showAuthPrompt} onClose={() => setShowAuthPrompt(false)} maxWidth="xs" fullWidth>
      <DialogTitle>Login or Register Required</DialogTitle>
      <DialogContent>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Please log in or register to view event details and register for events.
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button href="/login" variant="contained" color="primary">Login</Button>
        <Button href="/register" variant="outlined" color="primary">Register</Button>
        <Button onClick={() => setShowAuthPrompt(false)}>Cancel</Button>
      </DialogActions>
    </Dialog>

    <Snackbar
      open={!!regError || !!regSuccess}
      autoHideDuration={4000}
      onClose={clearMessages}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
    >
      {(!!regError && regError !== "") ? (
        <Alert onClose={clearMessages} severity="error" sx={{ width: "100%" }}>
          {regError}
        </Alert>
      ) : (!!regSuccess && regSuccess !== "") ? (
        <Alert onClose={clearMessages} severity="success" sx={{ width: "100%" }}>
          {regSuccess}
        </Alert>
      ) : undefined}
    </Snackbar>
    {/* Payment Dialog */}
    <Dialog open={showPaymentDialog} onClose={handleClosePaymentDialog} maxWidth="xs" fullWidth>
      <DialogTitle>Submit Payment</DialogTitle>
      <DialogContent>
        {/* QR Code for InstaPay Payment */}
        <Stack alignItems="center" spacing={1} sx={{ mb: 2 }}>
          <img
            src="/instapay-qr.jpg"
            alt="InstaPay QR Code"
            style={{ width: 180, height: 180, borderRadius: 8, border: '1px solid #ccc', marginBottom: 4 }}
          />
          <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center' }}>
            Scan this QR code to pay via InstaPay.<br />
            <span style={{ fontWeight: 'bold', color: '#2E7D32', letterSpacing: 2 }}>
              KE**N PH***P G.
            </span>
            <br />
            <span style={{ fontSize: 12, color: '#888' }}>Transfer fees may apply.</span>
          </Typography>
        </Stack>
        <Stack spacing={2} mt={1}>
          <Typography variant="subtitle1">
            Event: <b>{paymentModalEvent?.title}</b>
          </Typography>
          <Typography variant="subtitle2">
            Amount Due: <b>₱{paymentModalEvent?.price?.toLocaleString()}</b>
          </Typography>
          <TextField
            label="Amount Paid"
            type="number"
            value={paymentAmount}
            onChange={e => setPaymentAmount(e.target.value)}
            fullWidth
            required
          />
          <TextField
            label="Payment Channel"
            value={paymentChannel}
            onChange={e => setPaymentChannel(e.target.value)}
            fullWidth
            required
            placeholder="GCash, Maya, BPI, etc."
          />

          {paymentMsg && <Alert severity={paymentMsg.includes('success') ? 'success' : 'error'}>{paymentMsg}</Alert>}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowPaymentDialog(false)} disabled={paymentSubmitting}>Cancel</Button>
        <Button 
          onClick={() => {
            console.log('[DEBUG] Submit Payment button clicked', { paymentSubmitting, paymentModalEvent });
            handlePaymentSubmit();
          }} 
          disabled={paymentSubmitting || !paymentModalEvent} 
          variant="contained" 
          color="primary"
        >
          {paymentSubmitting ? 'Submitting...' : 'Submit Payment'}
        </Button>
      </DialogActions>
    </Dialog>
  </Box>
);

}

export default EventsPage;
