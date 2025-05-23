/**
 * Type definitions for API responses in the Pine Time admin dashboard.
 * Following Pine Time guidelines for type safety and error handling.
 */

// Basic pagination interface
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Dashboard metrics interface
export interface DashboardMetrics {
  users_count: number;
  active_events_count: number;
  registrations_count: number;
  badges_awarded_count: number;
  total_points: number;
  previous_users_count?: number;
  previous_active_events_count?: number;
  previous_registrations_count?: number;
  previous_badges_awarded_count?: number;
  previous_total_points?: number;
}

// Recent activity interface
export interface RecentActivity {
  id: string;
  type: string;
  user: string;
  action: string;
  timestamp: string;
  details?: string;
}

// User interface
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  role: string;
  points?: number;
  badges_count?: number;
  events_attended?: number;
}

// Event interface
export interface Event {
  id: string;
  title: string;
  description: string;
  location: string;
  event_type: string;
  start_time: string;
  end_time: string;
  max_participants: number;
  current_participants: number;
  points_reward: number;
  created_at: string;
  updated_at: string;
  status: 'draft' | 'active' | 'completed' | 'cancelled';
  registrations?: Registration[];
}

// Registration interface
export interface Registration {
  id: string;
  user_id: string;
  event_id: string;
  registration_date: string;
  status: 'registered' | 'attended' | 'no_show' | 'cancelled';
  payment_status: 'pending' | 'paid' | 'refunded' | 'not_required';
  user?: User;
  event?: Event;
}

// Badge interface
export interface Badge {
  id: string;
  name: string;
  description: string;
  category: string;
  level: number;
  icon_url?: string;
  requirements: string;
  points_reward: number;
}

// Points transaction interface
export interface PointsTransaction {
  id: string;
  user_id: string;
  amount: number;
  transaction_type: 'earned' | 'spent' | 'adjusted';
  reason: string;
  event_id?: string;
  badge_id?: string;
  created_at: string;
  user?: User;
  event?: Event;
  badge?: Badge;
}

// API error response
export interface ApiError {
  status_code: number;
  detail: string;
  type?: string;
  code?: string;
}
