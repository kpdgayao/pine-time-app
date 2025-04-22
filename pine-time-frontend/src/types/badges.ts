export interface Badge {
  id: number;
  name: string;
  description: string;
  icon_url?: string;
  level?: number;
  category?: string;
  progress?: number;
  next_level_threshold?: number;
}

export interface BadgeProgress {
  badge_id: number;
  user_id: number;
  current_progress: number;
  next_level_threshold: number;
  level: number;
  category: string;
}

export interface UserStats {
  total_points: number;
  total_badges: number;
  rank: number;
  total_users: number;
  streak_count: number;
  events_attended: number;
  recent_activities: RecentActivity[];
}

export interface RecentActivity {
  id: number;
  activity_type: 'event_registration' | 'badge_earned' | 'points_earned' | 'points_redeemed';
  description: string;
  timestamp: string;
  points?: number;
  badge_id?: number;
  event_id?: number;
}

export interface LeaderboardEntry {
  id: number;
  username: string;
  full_name: string;
  email: string;
  points: number;
  badges: number;
  avatar_url?: string;
  rank?: number;
}

export interface LeaderboardFilter {
  time_period: 'all_time' | 'weekly' | 'monthly';
  page: number;
  limit: number;
}
