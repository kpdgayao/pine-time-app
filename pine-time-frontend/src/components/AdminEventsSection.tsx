import React, { useEffect, useState } from "react";
import api from "../api/client";
import { extractErrorMessage } from '../utils/extractErrorMessage';
import EventEditDialog from "./EventEditDialog";
import AdminEventRegistrationsModal from "./AdminEventRegistrationsModal";

import StatusBadge from "./StatusBadge";
import { formatDate, formatRelativeTime, isPast } from "./dateUtils";
import {
  Table, TableHead, TableRow, TableCell, TableBody, TablePagination,
  Paper, Stack, Button, CircularProgress, Alert, IconButton, Tooltip, Checkbox, Snackbar, Typography, Dialog, DialogTitle, DialogActions
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PeopleIcon from '@mui/icons-material/People';

interface EventBase {
  title: string;
  description: string;
  event_type: string;
  location: string;
  start_time: string;
  end_time: string;
  max_participants: number;
  points_reward: number;
  is_active: boolean;
  image_url?: string;
  price?: number;
}
interface Event extends EventBase {
  id: number;
}

const PAGE_SIZE = 10;

const AdminEventsSection: React.FC = () => {
  // Registration dialog state
  const [regDialogOpen, setRegDialogOpen] = useState(false);
  const [regEventId, setRegEventId] = useState<number | undefined>(undefined);
  // Stats for events
  const [eventStats, setEventStats] = useState<Record<number, { registration_count: number; revenue: number }>>({});
  const [events, setEvents] = useState<Event[]>([]); 
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [editEvent, setEditEvent] = useState<Event | null>(null);
  const [editOpen, setEditOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);

  const fetchEvents = async (searchVal = search, pageVal = page) => {
    setLoading(true);
    setError(null);
    try {
      const params: any = { skip: (pageVal - 1) * PAGE_SIZE, limit: PAGE_SIZE };
      if (searchVal) params.q = searchVal;
      const res = await api.get('/events/', { params });
      setEvents(res.data);
      // Fetch stats for each event
      const stats: Record<number, { registration_count: number; revenue: number }> = {};
      let statsErrors = 0;
      await Promise.all(
        (res.data || []).map(async (event: Event) => {
          try {
            const statsRes = await api.get(`/events/${event.id}/stats`);
            stats[event.id] = {
              registration_count: statsRes.data.registration_count ?? 0,
              revenue: statsRes.data.revenue ?? 0,
            };
          } catch (err: any) {
            statsErrors += 1;
            const status = err?.response?.status;
            const data = err?.response?.data;
            const msg = extractErrorMessage(err) || "Unknown error";
            console.error(`[Event Stats] Failed for event ${event.id}:`, {
              status,
              data,
              msg,
              error: err,
            });
            stats[event.id] = { registration_count: 0, revenue: 0 };
          }
        })
      );
      setEventStats(stats);
      if (statsErrors > 0) {
        setError(prev => (prev ? prev + ` Some event stats could not be loaded (${statsErrors} errors).` : `Some event stats could not be loaded (${statsErrors} errors).`));
      }
    } catch (err: any) {
      setError(
        err?.response?.data?.detail || "Failed to fetch events. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
    // eslint-disable-next-line
  }, [page]);

  const handleEdit = (event: Event) => {
    setEditEvent(event);
    setEditOpen(true);
  };
  const handleEditSave = (updated: Event) => {
    setEvents((prev: Event[]) => prev.map((e: Event) => (e.id === updated.id ? updated : e)));
  };
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [eventToDelete, setEventToDelete] = useState<Event | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({ open: false, message: '', severity: 'success' });

  const handleDelete = (event: Event) => {
    setEventToDelete(event);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!eventToDelete) return;
    setLoading(true);
    setError(null);
    try {
      await api.delete(`/events/${eventToDelete.id}`);
      setEvents((prev: Event[]) => prev.filter((e: Event) => e.id !== eventToDelete.id));
      setSnackbar({ open: true, message: `Event '${eventToDelete.title}' deleted.`, severity: 'success' });
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to delete event.");
      setSnackbar({ open: true, message: `Failed to delete event.`, severity: 'error' });
    } finally {
      setLoading(false);
      setDeleteDialogOpen(false);
      setEventToDelete(null);
    }
  };
  const handleCreate = () => {
    setEditEvent(null);
    setCreateOpen(true);
  };
  const handleCreateSave = (created: Event) => {
    setEvents((prev: Event[]) => [created, ...prev]);
    setPage(1);
  };
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchEvents(search, 1);
  };
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    fetchEvents(search, newPage);
  };

  // Robust handling for API response formats (array, paginated dict, or unexpected)
// Support flexible API response structure: array, paginated object, or null
let eventsArray: Event[] = [];
if (Array.isArray(events)) {
  eventsArray = events;
} else if (events && typeof (events as any) === 'object' && Array.isArray((events as any).items)) {
  eventsArray = (events as any).items;
} else if (events == null) {
  eventsArray = [];
} else {
  // Unexpected format, log for debugging
  console.error('Unexpected events data format:', events);
  eventsArray = [];
}

const filteredEvents = eventsArray.filter(
  (_event) =>
    _event.title.toLowerCase().includes(search.toLowerCase()) ||
    _event.description.toLowerCase().includes(search.toLowerCase()) ||
    _event.location.toLowerCase().includes(search.toLowerCase())
);


  return (
    <Paper sx={{ p: 2, mb: 2 }} elevation={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Event Management</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreate}>
          Add Event
        </Button>
      </Stack>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {loading ? (
        <Stack alignItems="center" py={4}><CircularProgress /></Stack>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox" aria-label="Select All Events"><Checkbox disabled /></TableCell>
              <TableCell>ID</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Start</TableCell>
              <TableCell>End</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Registered</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredEvents.map(_event => {
              const stats = eventStats[_event.id] || { registration_count: 0 };
              new Date();
              let status: 'Active' | 'Full' | 'Past' = 'Active';
              if (isPast(_event.end_time)) status = 'Past';
              else if (stats.registration_count >= _event.max_participants) status = 'Full';
              return (
                <TableRow key={_event.id} hover tabIndex={-1}>
                  <TableCell padding="checkbox"><Checkbox inputProps={{ 'aria-label': `Select event ${_event.title}` }} disabled /></TableCell>
                  <TableCell>{_event.id}</TableCell>
                  <TableCell>{_event.title}</TableCell>
                  <TableCell>{_event.event_type}</TableCell>
                  <TableCell>
                    <Tooltip title={formatDate(_event.start_time)}><span>{formatRelativeTime(_event.start_time)}</span></Tooltip>
                  </TableCell>
                  <TableCell>
                    <Tooltip title={formatDate(_event.end_time)}><span>{formatRelativeTime(_event.end_time)}</span></Tooltip>
                  </TableCell>
                  <TableCell>{_event.location}</TableCell>
                  <TableCell><StatusBadge status={status} /></TableCell>
                  <TableCell>{stats.registration_count} / {_event.max_participants}</TableCell>
                  <TableCell align="right">
                    <Tooltip title="Edit" arrow><IconButton aria-label="Edit" color="primary" onClick={() => handleEdit(_event)} size="small"><EditIcon /></IconButton></Tooltip>
                    <Tooltip title="Delete" arrow><IconButton aria-label="Delete" color="error" onClick={() => handleDelete(_event)} size="small"><DeleteIcon /></IconButton></Tooltip>
                    <Tooltip title="View Registrations">
                      <IconButton
                        onClick={() => {
                          setRegEventId(_event.id);
                          setRegDialogOpen(true);
                        }}
                        color="primary"
                      >
                        <PeopleIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}
      <TablePagination
        rowsPerPageOptions={[10, 25, 50]}
        component="div"
        count={eventsArray.length}
        rowsPerPage={PAGE_SIZE}
        page={page - 1}
        onPageChange={(_, newPage) => handlePageChange(newPage + 1)}
      />
      <form onSubmit={handleSearch} style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
        <input
          placeholder="Search by title, description, or location"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ padding: 8, width: 260, marginRight: 8 }}
          aria-label="Search events"
        />
        <button type="submit" style={{ padding: "8px 16px" }}>Search</button>
      </form>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        message={snackbar.message}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Event</DialogTitle>
        <Typography sx={{ px: 3, pt: 1 }}>Are you sure you want to delete event '{eventToDelete?.title}'?</Typography>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} color="inherit">Cancel</Button>
          <Button onClick={confirmDelete} color="error">Delete</Button>
        </DialogActions>
      </Dialog>
      <EventEditDialog
        event={editEvent}
        open={editOpen}
        onClose={() => setEditOpen(false)}
        onSave={handleEditSave}
        isCreate={false}
      />
      <EventEditDialog
        event={null}
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSave={handleCreateSave}
        isCreate={true}
      />
      <AdminEventRegistrationsModal
        eventId={regEventId}
        open={regDialogOpen}
        onClose={() => setRegDialogOpen(false)}
      />
    </Paper>
  );
};

export default AdminEventsSection;
