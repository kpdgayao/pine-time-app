/**
 * API service functions for the Pine Time admin dashboard.
 * Following Pine Time's API configuration and error handling guidelines.
 */

import api, { safeApiCall, extractItems } from './index';
import { DashboardMetrics, User, Event, Badge, PointsTransaction, RecentActivity } from '../types/api';

/**
 * Dashboard API Services
 */
export const DashboardService = {
  /**
   * Get dashboard metrics data
   * @returns Promise with dashboard metrics
   */
  getMetrics: () => safeApiCall<DashboardMetrics>(
    api.get('/admin/dashboard/metrics'),
    {
      users_count: 0,
      active_events_count: 0,
      registrations_count: 0,
      badges_awarded_count: 0,
      total_points: 0
    }
  ),

  /**
   * Get recent activity data
   * @returns Promise with array of recent activities
   */
  getRecentActivities: () => 
    safeApiCall<RecentActivity[]>(
      api.get('/admin/dashboard/activities'),
      []
    ).then(data => extractItems<RecentActivity>(data, []))
};

/**
 * User Management API Services
 */
export const UserService = {
  /**
   * Get all users with pagination
   * @param page Page number to retrieve
   * @param pageSize Number of items per page
   * @returns Promise with user data and pagination info
   */
  getUsers: (page = 1, pageSize = 10) => 
    safeApiCall(
      api.get(`/users/?page=${page}&page_size=${pageSize}`),
      { items: [], total: 0, page: 1, page_size: 10, total_pages: 1 }
    ),

  /**
   * Get user by ID
   * @param userId User ID to retrieve
   * @returns Promise with user data
   */
  getUser: (userId: string) => 
    safeApiCall<User>(
      api.get(`/users/${userId}`),
      null
    ),

  /**
   * Update user by ID
   * @param userId User ID to update
   * @param userData User data to update
   * @returns Promise with updated user data
   */
  updateUser: (userId: string, userData: Partial<User>) => 
    safeApiCall<User>(
      api.put(`/users/${userId}`, userData),
      null
    ),

  /**
   * Update user points
   * @param userId User ID to update
   * @param points Points to add (positive) or remove (negative)
   * @param reason Reason for points adjustment
   * @returns Promise with success status
   */
  updateUserPoints: (userId: string, points: number, reason: string) => 
    safeApiCall<{success: boolean}>(
      api.post(`/users/${userId}/points`, { points, reason }),
      { success: false }
    )
};

/**
 * Event Management API Services
 */
export const EventService = {
  /**
   * Get all events with pagination
   * @param page Page number to retrieve
   * @param pageSize Number of items per page
   * @returns Promise with event data and pagination info
   */
  getEvents: (page = 1, pageSize = 10) => 
    safeApiCall(
      api.get(`/events/?page=${page}&page_size=${pageSize}`),
      { items: [], total: 0, page: 1, page_size: 10, total_pages: 1 }
    ),

  /**
   * Get event by ID
   * @param eventId Event ID to retrieve
   * @returns Promise with event data
   */
  getEvent: (eventId: string) => 
    safeApiCall<Event>(
      api.get(`/events/${eventId}`),
      null
    ),

  /**
   * Create a new event
   * @param eventData Event data to create
   * @returns Promise with created event data
   */
  createEvent: (eventData: Partial<Event>) => 
    safeApiCall<Event>(
      api.post('/events/', eventData),
      null
    ),

  /**
   * Update event by ID
   * @param eventId Event ID to update
   * @param eventData Event data to update
   * @returns Promise with updated event data
   */
  updateEvent: (eventId: string, eventData: Partial<Event>) => 
    safeApiCall<Event>(
      api.put(`/events/${eventId}`, eventData),
      null
    ),

  /**
   * Delete event by ID
   * @param eventId Event ID to delete
   * @returns Promise with success status
   */
  deleteEvent: (eventId: string) => 
    safeApiCall<{success: boolean}>(
      api.delete(`/events/${eventId}`),
      { success: false }
    )
};

/**
 * Badge Management API Services
 */
export const BadgeService = {
  /**
   * Get all badges
   * @returns Promise with badge data
   */
  getBadges: () => 
    safeApiCall<Badge[]>(
      api.get('/badges/'),
      []
    ).then(data => extractItems<Badge>(data, [])),

  /**
   * Get badge by ID
   * @param badgeId Badge ID to retrieve
   * @returns Promise with badge data
   */
  getBadge: (badgeId: string) => 
    safeApiCall<Badge>(
      api.get(`/badges/${badgeId}`),
      null
    )
};

/**
 * Points Management API Services
 */
export const PointsService = {
  /**
   * Get leaderboard data
   * @param limit Number of top users to retrieve
   * @returns Promise with leaderboard data
   */
  getLeaderboard: (limit = 10) => 
    safeApiCall<User[]>(
      api.get(`/points/leaderboard?limit=${limit}`),
      []
    ).then(data => extractItems<User>(data, [])),

  /**
   * Get points history for all users or filtered by user ID
   * @param userId Optional user ID to filter by
   * @returns Promise with points history data
   */
  getPointsHistory: (userId?: string) => {
    const url = userId ? `/points/history?user_id=${userId}` : '/points/history';
    return safeApiCall<PointsTransaction[]>(
      api.get(url),
      []
    ).then(data => extractItems<PointsTransaction>(data, []));
  }
};
