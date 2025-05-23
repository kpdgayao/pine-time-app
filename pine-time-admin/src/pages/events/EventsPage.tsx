import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Alert,
  CircularProgress,
  MenuItem
} from '@mui/material';
import { Edit, Delete, Add, Event as EventIcon } from '@mui/icons-material';
import AdminLayout from '../../components/layout/AdminLayout';
import { EventService } from '../../api/services';
import { useLoading } from '../../contexts/LoadingContext';
import type { Event } from '../../types/api';

/**
 * Events management page component
 * Allows admins to view, edit, and manage events
 */
const EventsPage: React.FC = () => {
  // State for events data and pagination
  const [events, setEvents] = useState<Event[]>([]);
  const [totalEvents, setTotalEvents] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // State for event edit modal
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [eventFormData, setEventFormData] = useState<Partial<Event>>({});
  
  // Error handling state
  const [error, setError] = useState<string | null>(null);
  
  // Loading context for managing loading states
  const { setLoading, setLoadingMessage } = useLoading();

  // Event types for dropdown
  const eventTypes = ['Workshop', 'Seminar', 'Meetup', 'Conference', 'Game Night', 'Trivia Night', 'Murder Mystery'];

  // Event statuses for dropdown
  const eventStatuses = ['draft', 'active', 'completed', 'cancelled'];

  /**
   * Fetch events data from API
   */
  const fetchEvents = async () => {
    try {
      setLoading(true);
      setLoadingMessage('Loading events...');
      setError(null);
      
      const response = await EventService.getEvents(page + 1, rowsPerPage);
      
      if (response && 'items' in response) {
        setEvents(response.items as Event[]);
        setTotalEvents(response.total);
      } else {
        setError('Failed to fetch events data');
        setEvents([]);
      }
    } catch (err) {
      setError('An error occurred while fetching events data');
      console.error('Error fetching events:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle page change in pagination
   */
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  /**
   * Handle rows per page change in pagination
   */
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  /**
   * Open edit modal for an event
   */
  const handleEditEvent = (event: Event) => {
    setSelectedEvent(event);
    setEventFormData({
      title: event.title,
      description: event.description,
      location: event.location,
      event_type: event.event_type,
      start_time: formatDateTimeForInput(event.start_time),
      end_time: formatDateTimeForInput(event.end_time),
      max_participants: event.max_participants,
      points_reward: event.points_reward,
      status: event.status
    });
    setIsEditModalOpen(true);
  };

  /**
   * Format date for datetime-local input
   */
  const formatDateTimeForInput = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toISOString().slice(0, 16);
    } catch (error) {
      console.error('Error formatting date:', error);
      return '';
    }
  };

  /**
   * Handle form input changes
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setEventFormData({
      ...eventFormData,
      [name]: value
    });
  };

  /**
   * Submit event edit form
   */
  const handleSubmitEventEdit = async () => {
    try {
      setLoading(true);
      setLoadingMessage(selectedEvent ? 'Updating event...' : 'Creating event...');
      
      let result: Event | null = null;
      
      if (selectedEvent) {
        // Update existing event
        result = await EventService.updateEvent(selectedEvent.id, eventFormData);
        
        if (result) {
          setEvents(events.map(event => 
            event.id === selectedEvent.id ? { ...event, ...result } : event
          ));
        }
      } else {
        // Create new event
        result = await EventService.createEvent(eventFormData);
        
        if (result) {
          fetchEvents(); // Refresh the events list
        }
      }
      
      if (result) {
        setIsEditModalOpen(false);
        setSelectedEvent(null);
      } else {
        setError(`Failed to ${selectedEvent ? 'update' : 'create'} event`);
      }
    } catch (err) {
      setError(`An error occurred while ${selectedEvent ? 'updating' : 'creating'} event`);
      console.error(`Error ${selectedEvent ? 'updating' : 'creating'} event:`, err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Delete an event
   */
  const handleDeleteEvent = async (eventId: string) => {
    if (!window.confirm('Are you sure you want to delete this event?')) {
      return;
    }
    
    try {
      setLoading(true);
      setLoadingMessage('Deleting event...');
      
      const result = await EventService.deleteEvent(eventId);
      
      if (result && result.success) {
        setEvents(events.filter(event => event.id !== eventId));
      } else {
        setError('Failed to delete event');
      }
    } catch (err) {
      setError('An error occurred while deleting event');
      console.error('Error deleting event:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Get status chip color based on event status
   */
  const getStatusChipProps = (status: string) => {
    switch (status) {
      case 'active':
        return { color: 'success' as const, label: 'Active' };
      case 'completed':
        return { color: 'primary' as const, label: 'Completed' };
      case 'cancelled':
        return { color: 'error' as const, label: 'Cancelled' };
      case 'draft':
      default:
        return { color: 'warning' as const, label: 'Draft' };
    }
  };

  // Fetch events when page or rowsPerPage changes
  useEffect(() => {
    fetchEvents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, rowsPerPage]);

  return (
    <AdminLayout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Events Management
          </Typography>
          <Button 
            variant="contained" 
            startIcon={<Add />}
            onClick={() => {
              setSelectedEvent(null);
              setEventFormData({
                status: 'draft',
                points_reward: 100,
                max_participants: 50
              });
              setIsEditModalOpen(true);
            }}
          >
            Create Event
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ width: '100%', overflow: 'hidden' }}>
          <TableContainer sx={{ maxHeight: 'calc(100vh - 280px)' }}>
            <Table stickyHeader aria-label="events table">
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Date & Time</TableCell>
                  <TableCell>Participants</TableCell>
                  <TableCell>Points</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {events.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Box sx={{ py: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        {totalEvents === 0 ? (
                          <Typography>No events found</Typography>
                        ) : (
                          <CircularProgress size={32} />
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : (
                  events.map((event) => {
                    const statusProps = getStatusChipProps(event.status);
                    return (
                      <TableRow key={event.id} hover>
                        <TableCell>{event.title}</TableCell>
                        <TableCell>{event.event_type}</TableCell>
                        <TableCell>{event.location}</TableCell>
                        <TableCell>
                          {new Date(event.start_time).toLocaleDateString()} {new Date(event.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </TableCell>
                        <TableCell>
                          {event.current_participants} / {event.max_participants}
                        </TableCell>
                        <TableCell>{event.points_reward}</TableCell>
                        <TableCell>
                          <Chip 
                            label={statusProps.label} 
                            color={statusProps.color} 
                            size="small" 
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton size="small" onClick={() => handleEditEvent(event)}>
                              <Edit fontSize="small" />
                            </IconButton>
                            <IconButton size="small" onClick={() => handleDeleteEvent(event.id)}>
                              <Delete fontSize="small" />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={totalEvents}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>

        {/* Event Edit Dialog */}
        <Dialog open={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>
            {selectedEvent ? 'Edit Event' : 'Create New Event'}
          </DialogTitle>
          <DialogContent dividers>
            <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
              <Grid container spacing={2}>
                <Grid sx={{ gridColumn: { xs: 'span 12' } }}>
                  <TextField
                    label="Event Title"
                    name="title"
                    value={eventFormData.title || ''}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    required
                  />
                </Grid>
                
                <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                  <TextField
                    select
                    label="Event Type"
                    name="event_type"
                    value={eventFormData.event_type || ''}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    required
                  >
                    {eventTypes.map((type) => (
                      <MenuItem key={type} value={type}>
                        {type}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                
                <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                  <TextField
                    label="Location"
                    name="location"
                    value={eventFormData.location || ''}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    required
                  />
                </Grid>
                
                <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                  <TextField
                    label="Start Time"
                    name="start_time"
                    type="datetime-local"
                    value={eventFormData.start_time || ''}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    required
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                
                <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                  <TextField
                    label="End Time"
                    name="end_time"
                    type="datetime-local"
                    value={eventFormData.end_time || ''}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    required
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                
                <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
                  <TextField
                    label="Max Participants"
                    name="max_participants"
                    type="number"
                    value={eventFormData.max_participants || ''}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    required
                    inputProps={{ min: 1 }}
                  />
                </Grid>
                
                <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
                  <TextField
                    label="Points Reward"
                    name="points_reward"
                    type="number"
                    value={eventFormData.points_reward || ''}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    required
                    inputProps={{ min: 0 }}
                  />
                </Grid>
                
                <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
                  <TextField
                    select
                    label="Status"
                    name="status"
                    value={eventFormData.status || 'draft'}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    required
                  >
                    {eventStatuses.map((status) => (
                      <MenuItem key={status} value={status}>
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                
                <Grid sx={{ gridColumn: { xs: 'span 12' } }}>
                  <TextField
                    label="Description"
                    name="description"
                    value={eventFormData.description || ''}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    required
                    multiline
                    rows={4}
                  />
                </Grid>
              </Grid>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditModalOpen(false)}>Cancel</Button>
            <Button 
              onClick={handleSubmitEventEdit} 
              variant="contained" 
              color="primary"
              startIcon={<EventIcon />}
            >
              {selectedEvent ? 'Update Event' : 'Create Event'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </AdminLayout>
  );
};

export default EventsPage;
