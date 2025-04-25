import { useEffect, useState } from 'react';
import api from '../api/client';
import { safeApiCall } from '../utils/api';
import { Event } from '../types/events';
import { Badge, RecentActivity, UserStats } from '../types/badges';

/**
 * Custom hook for fetching and managing all Profile page data and state.
 * Handles API calls, loading, error, and celebration state.
 * Follows Pine Time coding guidelines for error handling and resilience.
 */
export function useProfileData() {
  const [profile, setProfile] = useState<any>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [upcomingEvents, setUpcomingEvents] = useState<Event[]>([]);
  const [recommendedEvents, setRecommendedEvents] = useState<Event[]>([]);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Celebration states
  const [showCelebration, setShowCelebration] = useState(false);
  const [celebrationBadge, setCelebrationBadge] = useState<Badge | null>(null);
  const [showLevelUpCelebration, setShowLevelUpCelebration] = useState(false);
  const [levelUpBadge, setLevelUpBadge] = useState<Badge | null>(null);
  const [previousLevel, setPreviousLevel] = useState(0);

  useEffect(() => {
    let isMounted = true;
    async function fetchProfileAndDashboard() {
      setLoading(true);
      setError('');
      try {
        // Fetch user profile
        console.log('Fetching user profile...');
        const userData = await safeApiCall(api.get('/users/me'), null);
        console.log('User data response:', userData);
        if (!userData) {
          console.log('No user data returned');
          if (isMounted) setError('Failed to load profile data');
          return;
        }
        if (isMounted) {
          const processedData = {
            ...userData,
            avatar_url: userData.avatar_url || '/avatars/default.png'
          };
          console.log('Setting profile data:', processedData);
          setProfile(processedData);
        }

        // Fetch stats
        if (userData.id) {
          const statsData = await safeApiCall(api.get(`/users/${userData.id}/stats`), null);
          if (statsData && isMounted) setStats(statsData);
        }

        // Fetch badges
        const badgesResponse = await safeApiCall(api.get('/badges/users/me/badges'), { badges: [] });
        const badgesData = Array.isArray(badgesResponse)
          ? badgesResponse
          : badgesResponse?.badges || [];
        if (isMounted) setBadges(badgesData);

        // Celebration: new badge
        const newBadge = localStorage.getItem('newBadge');
        if (newBadge) {
          try {
            const badgeData = JSON.parse(newBadge);
            if (isMounted) {
              setCelebrationBadge(badgeData);
              setShowCelebration(true);
            }
          } catch (e) {
            localStorage.removeItem('newBadge');
          }
          localStorage.removeItem('newBadge');
        }

        // Celebration: badge level up
        const levelUpData = localStorage.getItem('badgeLevelUp');
        if (levelUpData) {
          try {
            const { badge, previousLevel } = JSON.parse(levelUpData);
            if (isMounted) {
              setLevelUpBadge(badge);
              setPreviousLevel(previousLevel);
              setShowLevelUpCelebration(true);
            }
          } catch (e) {
            localStorage.removeItem('badgeLevelUp');
          }
          localStorage.removeItem('badgeLevelUp');
        }

        // Fetch upcoming events (limit 3)
        const upcomingEventsResponse = await safeApiCall(
          api.get('/events/recommended', { params: { limit: 3 } }),
          { events: [] }
        );
        const upcomingEventsData = Array.isArray(upcomingEventsResponse)
          ? upcomingEventsResponse
          : upcomingEventsResponse?.events || [];
        if (isMounted) setUpcomingEvents(upcomingEventsData.slice(0, 3));

        // Fetch recommended events
        const recommendedEventsResponse = await safeApiCall(api.get('/events/recommended'), { events: [] });
        const recommendedEventsData = Array.isArray(recommendedEventsResponse)
          ? recommendedEventsResponse
          : recommendedEventsResponse?.events || [];
        if (isMounted) setRecommendedEvents(recommendedEventsData);

        // Fetch recent activities
        const activitiesResponse = await safeApiCall(
          userData?.id ? api.get(`/users/${userData.id}/activities`) : null,
          { activities: [] }
        );
        const activitiesData = Array.isArray(activitiesResponse)
          ? activitiesResponse
          : activitiesResponse?.activities || [];
        if (isMounted) setRecentActivities(activitiesData);
      } catch (err: any) {
        if (isMounted) setError('An unexpected error occurred while loading profile data.');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    fetchProfileAndDashboard();
    return () => {
      isMounted = false;
    };
  }, []);

  return {
    profile,
    setProfile,
    stats,
    badges,
    upcomingEvents,
    recommendedEvents,
    recentActivities,
    loading,
    error,
    // Celebration state and setters
    showCelebration,
    setShowCelebration,
    celebrationBadge,
    showLevelUpCelebration,
    setShowLevelUpCelebration,
    levelUpBadge,
    previousLevel,
  };
}
