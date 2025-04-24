import { useState, useEffect, useMemo } from 'react';
import dayjs from 'dayjs';
import { Event, Registration } from '../types/events';
import { useAuth } from '../contexts/AuthContext';
import api, { apiLongTimeout, retryApiCall } from '../utils/api';
import { extractErrorMessage } from '../utils/extractErrorMessage';

export interface EventFilters {
  search: string;
  eventType: string;
  location: string;
  dateRange: [dayjs.Dayjs | null, dayjs.Dayjs | null];
  priceRange: [number, number];
  sortBy: string;
}

// Track paid registrations to prevent Pay Now button from showing after payment
export interface PaidRegistration {
  eventId: number;
  registrationId: number;
  timestamp: number;
}

export const useEvents = () => {
  const { user } = useAuth();
  const [events, setEvents] = useState<Event[]>([]);
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [paidRegistrations, setPaidRegistrations] = useState<PaidRegistration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Define a constant for the localStorage key to ensure consistency
  const PAID_REGISTRATIONS_KEY = 'pine_time_paid_registrations';
  
  // Load paid registrations from localStorage if available
  useEffect(() => {
    const savedPaidRegs = localStorage.getItem(PAID_REGISTRATIONS_KEY);
    if (savedPaidRegs) {
      try {
        const parsed = JSON.parse(savedPaidRegs);
        if (Array.isArray(parsed)) {
          setPaidRegistrations(parsed);
        }
      } catch (e) {
        console.error('Error parsing paid registrations from localStorage', e);
      }
    }
  }, []);
  
  // Filter states with defaults
  const [filters, setFilters] = useState<EventFilters>({
    search: '',
    eventType: '',
    location: '',
    dateRange: [null, null],
    priceRange: [0, 1000],
    sortBy: 'start-soonest'
  });

  // State for min/max price (now fetched from API)
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(1000);
  
  useEffect(() => {
    setFilters(prev => ({
      ...prev,
      priceRange: [minPrice, maxPrice]
    }));
  }, [minPrice, maxPrice]);

  // State for event types (now fetched from API)
  const [eventTypes, setEventTypes] = useState<string[]>([]);

  // Fetch events and registrations with robust error handling
  const fetchEventsAndRegistrations = async () => {
    setLoading(true);
    setError(null);
    try {
      // Convert filters to API parameters
      const params: any = {
        skip: 0,
        limit: 100
      };
      
      if (filters.search) params.search = filters.search;
      if (filters.eventType) params.event_type = filters.eventType;
      if (filters.location) params.location = filters.location;
      if (filters.dateRange[0]) params.start_date = filters.dateRange[0].toISOString();
      if (filters.dateRange[1]) params.end_date = filters.dateRange[1].toISOString();
      if (filters.priceRange[0] > 0) params.min_price = filters.priceRange[0];
      if (filters.priceRange[1] < maxPrice) params.max_price = filters.priceRange[1];
      if (filters.sortBy) params.sort_by = filters.sortBy;
      
      // Use retryApiCall with apiLongTimeout for better handling of potential timeouts
      const eventsData = await retryApiCall(
        () => apiLongTimeout.get('/events/', { params }),
        { items: [], total: 0 }, // fallback value
        2,  // max retries
        1000 // retry delay in ms
      );
      
      // Handle both paginated and non-paginated responses
      if (eventsData && Array.isArray(eventsData.items)) {
        setEvents(eventsData.items);
      } else if (Array.isArray(eventsData)) {
        setEvents(eventsData);
      } else {
        setEvents([]);
      }
      
      // Only fetch registrations if authenticated
      if (user) {
        try {
          const regsRes = await api.get('/registrations/users/me/registrations');
          setRegistrations(Array.isArray(regsRes.data) ? regsRes.data : regsRes.data?.items || []);
        } catch (regErr) {
          console.error('Error fetching registrations:', regErr);
          setRegistrations([]); // If failed, just set empty
        }
      } else {
        setRegistrations([]);
      }
      
      // Fetch event types for the filter dropdown
      try {
        const typesRes = await api.get('/events/types');
        const fetchedTypes = Array.isArray(typesRes.data) ? typesRes.data : [];
        // Only update if we got types and they're different from what we have
        if (fetchedTypes.length > 0 && JSON.stringify(fetchedTypes) !== JSON.stringify(eventTypes)) {
          setEventTypes(fetchedTypes);
        }
      } catch (typesErr) {
        console.error('Error fetching event types:', typesErr);
        // Keep using existing event types
      }
      
      // Fetch price range for the price slider
      try {
        const priceRangeRes = await api.get('/events/price-range');
        if (priceRangeRes.data && 
            typeof priceRangeRes.data.min_price === 'number' && 
            typeof priceRangeRes.data.max_price === 'number') {
          setMinPrice(priceRangeRes.data.min_price);
          setMaxPrice(priceRangeRes.data.max_price);
        }
      } catch (priceErr) {
        console.error('Error fetching price range:', priceErr);
        // Keep using existing min/max price
      }
    } catch (err) {
      setError(extractErrorMessage(err));
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  // Debounce fetch when filters change
  useEffect(() => {
    const debounceTimeout = setTimeout(() => {
      fetchEventsAndRegistrations();
    }, 300); // Wait 300ms after filter changes before fetching
    
    return () => clearTimeout(debounceTimeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);
  
  // Fetch when user changes (no debounce needed)
  useEffect(() => {
    fetchEventsAndRegistrations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);
  
  // Additionally fetch event types and price range at initial load
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        // Fetch event types with retry mechanism
        const typesData = await retryApiCall(
          () => apiLongTimeout.get('/events/types'),
          [], // fallback value
          2,  // max retries
          1000 // retry delay in ms
        );
        
        if (Array.isArray(typesData) && typesData.length > 0) {
          setEventTypes(typesData);
        }
        
        // Fetch price range with retry mechanism
        const priceRangeData = await retryApiCall(
          () => apiLongTimeout.get('/events/price-range'),
          { min_price: 0, max_price: 1000 }, // fallback value
          2,  // max retries
          1000 // retry delay in ms
        );
        
        if (priceRangeData && 
            typeof priceRangeData.min_price === 'number' && 
            typeof priceRangeData.max_price === 'number') {
          setMinPrice(priceRangeData.min_price);
          setMaxPrice(priceRangeData.max_price);
          
          // Update filters with new price range
          setFilters(prev => ({
            ...prev,
            priceRange: [priceRangeData.min_price, priceRangeData.max_price]
          }));
        }
      } catch (err) {
        console.error('Error fetching metadata:', err);
      }
    };
    
    fetchMetadata();
  }, []);

  // We don't need client-side filtering anymore since we use server-side filtering
  // Just pass through the events that the API returns based on our filters
  const filteredEvents = useMemo(() => {
    // Ensure we only show active events (server should handle this, but just in case)
    return events.filter(e => e.is_active);
  }, [events]);

  // Split events into categories for UI display
  const categorizedEvents = useMemo(() => {
    const now = dayjs();
    
    // Helper function to safely get registration for an event
    const getRegistration = (event: Event): Registration | undefined => {
      const regs = registrations.filter(r => r.event_id === event.id);
      return (
        regs.find(r => r.status === 'approved') ||
        regs.find(r => r.status === 'pending') ||
        regs.find(r => r.status === 'rejected') ||
        regs.find(r => r.status === 'cancelled') ||
        undefined
      );
    };
    
    // Split events into categories
    return {
      upcomingUnregistered: filteredEvents.filter(e => 
        dayjs(e.end_time).isAfter(now) && !getRegistration(e)
      ),
      upcomingRegistered: filteredEvents.filter(e => 
        dayjs(e.end_time).isAfter(now) && !!getRegistration(e)
      ),
      pastEvents: filteredEvents.filter(e => 
        dayjs(e.end_time).isBefore(now)
      ),
      getRegistration
    };
  }, [filteredEvents, registrations]);

  // Helper function to update a specific filter
  const updateFilter = <K extends keyof EventFilters>(
    key: K, 
    value: EventFilters[K]
  ) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // Function to mark a registration as paid
  const markRegistrationAsPaid = (eventId: number, registrationId: number) => {
    // Verify we have valid IDs
    if (!eventId || !registrationId) {
      console.error('Invalid eventId or registrationId in markRegistrationAsPaid', { eventId, registrationId });
      return;
    }
    
    const newPaidReg: PaidRegistration = {
      eventId,
      registrationId,
      timestamp: Date.now()
    };
    
    // Check if this registration is already marked as paid to prevent duplicates
    const alreadyPaid = paidRegistrations.some(
      pr => pr.eventId === eventId && pr.registrationId === registrationId
    );
    
    if (alreadyPaid) {
      console.log(`Registration ${registrationId} for event ${eventId} already marked as paid`);
      return;
    }
    
    const updatedPaidRegs = [...paidRegistrations, newPaidReg];
    setPaidRegistrations(updatedPaidRegs);
    
    // Save to localStorage for persistence
    try {
      localStorage.setItem(PAID_REGISTRATIONS_KEY, JSON.stringify(updatedPaidRegs));
    } catch (e) {
      console.error('Error saving paid registrations to localStorage', e);
    }
  };
  
  // Check if a registration has been paid
  const isRegistrationPaid = (eventId: number, registrationId?: number) => {
    // Verify we have valid IDs
    if (!eventId) {
      console.error('Invalid eventId in isRegistrationPaid', { eventId });
      return false;
    }
    
    // If no registrationId is provided, we need both eventId and registrationId to mark as paid
    if (!registrationId) {
      return false;
    }
    
    // Check if this specific registration has been marked as paid
    const matchingRegistration = paidRegistrations.find(
      pr => pr.eventId === eventId && pr.registrationId === registrationId
    );
    
    return !!matchingRegistration;
  };

  return {
    events,
    registrations,
    loading,
    error,
    filters,
    updateFilter,
    eventTypes,
    minPrice,
    maxPrice,
    categorizedEvents,
    markRegistrationAsPaid,
    isRegistrationPaid,
    refetch: fetchEventsAndRegistrations
  };
};
