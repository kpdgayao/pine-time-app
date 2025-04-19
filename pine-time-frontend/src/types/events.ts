export interface EventBase {
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
  registration_count?: number;
}

export interface Event extends EventBase {
  id: number;
}

export interface Registration {
  id: number;
  event_id: number;
  user_id: number;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
}
