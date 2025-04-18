import React, { useEffect, useState } from "react";
import api from "../api/client";
import EventEditDialog from "./EventEditDialog";
import EventRegistrationsDialog from "./EventRegistrationsDialog";
import EventStatsChart from "./EventStatsChart";

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
  const [regEventId, setRegEventId] = useState<number | null>(null);
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
      await Promise.all(
        (res.data || []).map(async (event: Event) => {
          try {
            const statsRes = await api.get(`/events/${event.id}/stats`);
            stats[event.id] = {
              registration_count: statsRes.data.registration_count ?? 0,
              revenue: statsRes.data.revenue ?? 0,
            };
          } catch (err) {
            console.error(`Failed to fetch stats for event ${event.id}:`, err);
            stats[event.id] = { registration_count: 0, revenue: 0 };
          }
        })
      );
      setEventStats(stats);
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
  const handleDelete = async (event: Event) => {
    if (!window.confirm(`Delete event '${event.title}'?`)) return;
    setLoading(true);
    setError(null);
    try {
      await api.delete(`/events/${event.id}`);
      setEvents((prev: Event[]) => prev.filter((e: Event) => e.id !== event.id));
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to delete event.");
    } finally {
      setLoading(false);
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
  (e) =>
    e.title.toLowerCase().includes(search.toLowerCase()) ||
    e.description.toLowerCase().includes(search.toLowerCase()) ||
    e.location.toLowerCase().includes(search.toLowerCase())
);

// Analytics
const totalEvents = eventsArray.length;
const activeEvents = eventsArray.filter((e) => e.is_active).length;
const totalParticipants = eventsArray.reduce((sum, e) => sum + (e.max_participants || 0), 0);
const totalRegistrations = eventsArray.reduce((sum, e) => sum + (eventStats[e.id]?.registration_count || 0), 0);
const totalRevenue = eventsArray.reduce((sum, e) => sum + (eventStats[e.id]?.revenue || 0), 0);

// For chart component
const eventsForChart = eventsArray.map((e) => ({
  ...e,
  registration_count: eventStats[e.id]?.registration_count || 0,
  revenue: eventStats[e.id]?.revenue || 0,
}));

  return (
    <div>
      <h2>Event Management</h2>
      <div style={{ marginBottom: 16, display: "flex", gap: 32 }}>
        <div><strong>Total Events:</strong> {totalEvents}</div>
        <div><strong>Active Events:</strong> {activeEvents}</div>
        <div><strong>Max Total Participants:</strong> {totalParticipants}</div>
        <div><strong>Total Registrations:</strong> {totalRegistrations}</div>
        <div><strong>Total Revenue:</strong> {totalRevenue}</div>
      </div>
      <div style={{ marginBottom: 24 }}>
        <EventStatsChart events={eventsForChart} />
      </div>
      <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
        <form onSubmit={handleSearch} style={{ flex: 1 }}>
          <input
            placeholder="Search by title, description, or location"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ padding: 8, width: 260, marginRight: 8 }}
          />
          <button type="submit" style={{ padding: "8px 16px" }}>Search</button>
        </form>
        <button onClick={handleCreate} style={{ marginLeft: 16, padding: "8px 16px", background: "#2E7D32", color: "white", border: "none", borderRadius: 4 }}>
          + Create Event
        </button>
      </div>
      {loading && <div>Loading events...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
      <table style={{ width: "100%", marginTop: 8, borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#e0e0e0" }}>
            <th>ID</th>
            <th>Title</th>
            <th>Type</th>
            <th>Start</th>
            <th>End</th>
            <th>Location</th>
            <th>Active</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredEvents.length === 0 && (
            <tr><td colSpan={8} style={{ textAlign: "center", color: "#999" }}>No events found.</td></tr>
          )}
          {filteredEvents.map((event) => (
            <tr key={event.id} style={{ borderBottom: "1px solid #ccc" }}>
              <td>{event.id}</td>
              <td>{event.title}</td>
              <td>{event.event_type}</td>
              <td>{new Date(event.start_time).toLocaleString()}</td>
              <td>{new Date(event.end_time).toLocaleString()}</td>
              <td>{event.location}</td>
              <td>{event.is_active ? "Yes" : "No"}</td>
              <td>
                <button style={{ marginRight: 8 }} onClick={() => handleEdit(event)}>Edit</button>
                <button style={{ marginRight: 8 }} onClick={() => { setRegEventId(event.id); setRegDialogOpen(true); }}>Registrations</button>
                <button onClick={() => handleDelete(event)} style={{ color: "#c62828" }}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {/* Pagination */}
      <div style={{ marginTop: 16, display: "flex", justifyContent: "center" }}>
        <button onClick={() => handlePageChange(page - 1)} disabled={page === 1} style={{ marginRight: 8 }}>Prev</button>
        <span>Page {page}</span>
        <button onClick={() => handlePageChange(page + 1)} disabled={filteredEvents.length < PAGE_SIZE} style={{ marginLeft: 8 }}>Next</button>
      </div>
      {/* Dialogs */}
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
      {/* Registration dialog */}
      <EventRegistrationsDialog
        eventId={regEventId}
        open={regDialogOpen}
        onClose={() => setRegDialogOpen(false)}
      />
    </div>
  );
};

export default AdminEventsSection;
