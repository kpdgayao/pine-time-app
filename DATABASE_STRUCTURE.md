# Pine Time Database Structure

This document outlines the database structure for the Pine Time application, with a focus on the PostgreSQL implementation and the gamification system.

## Database Overview

The Pine Time application uses PostgreSQL 17.4 as its primary database system. The database schema is designed to support:

- User management and authentication
- Event creation and management
- Registration and attendance tracking
- Gamification (badges, points, and streaks)
- Administrative functions

## Core Tables

### Users

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    user_type VARCHAR(50) DEFAULT 'regular',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);
```

### Events

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL,
    location VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    max_participants INTEGER,
    points_reward INTEGER DEFAULT 0,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Registrations

```sql
CREATE TABLE registrations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'registered',
    payment_status VARCHAR(50) DEFAULT 'pending',
    UNIQUE (user_id, event_id)
);
```

### Payments

```sql
CREATE TABLE payment (
    id SERIAL PRIMARY KEY,
    registration_id INTEGER NOT NULL REFERENCES registrations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    amount_paid NUMERIC NOT NULL,
    payment_channel CHARACTER VARYING(50) NOT NULL,
    payment_date TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Gamification Tables

### Badges

```sql
CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    badge_type VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    icon_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### User Badges

```sql
CREATE TABLE user_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_id INTEGER NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    level INTEGER DEFAULT 1 NOT NULL,
    earned_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE (user_id, badge_id)
);
```

### Points Transactions

```sql
CREATE TABLE points_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    points INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    description TEXT,
    event_id INTEGER REFERENCES events(id) ON DELETE SET NULL,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Event Attendees

```sql
CREATE TABLE event_attendees (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'attended',
    check_in_time TIMESTAMP WITH TIME ZONE,
    check_out_time TIMESTAMP WITH TIME ZONE,
    UNIQUE (user_id, event_id)
);
```

## Relationships

- **Users to Events**: One-to-many (a user can create multiple events)
- **Users to Registrations**: One-to-many (a user can register for multiple events)
- **Events to Registrations**: One-to-many (an event can have multiple registrations)
- **Registrations to Payments**: One-to-one (a registration can have one payment record)
- **Users to Payments**: One-to-many (a user can make multiple payments)
- **Events to Payments**: One-to-many (an event can have multiple payments)
- **Users to User Badges**: One-to-many (a user can earn multiple badges)
- **Badges to User Badges**: One-to-many (a badge can be earned by multiple users)
- **Users to Points Transactions**: One-to-many (a user can have multiple points transactions)
- **Events to Points Transactions**: One-to-many (an event can generate multiple points transactions)
- **Users to Event Attendees**: One-to-many (a user can attend multiple events)
- **Events to Event Attendees**: One-to-many (an event can have multiple attendees)

## Gamification System

The Pine Time gamification system consists of three main components:

1. **Badges**: Achievements that users earn by completing specific actions
2. **Points**: Currency earned through participation and achievements
3. **Streaks**: Rewards for consistent weekly participation

### Badge Types and Levels

Badges have different types and categories, and can be leveled up:

- **Event Explorer**: Earned by attending different types of events
- **Social Butterfly**: Earned by connecting with other attendees
- **Trivia Master**: Earned by winning trivia nights
- **Consistent Attendee**: Earned by maintaining attendance streaks
- **Community Builder**: Earned by bringing new members

Each badge can have multiple levels (1-5), with increasing requirements for each level.

### Points System

Points are earned through:

- **Event Attendance**: Base points for attending events
- **Streak Bonuses**: Additional points for maintaining weekly attendance
- **Badge Achievements**: Points awarded when earning new badges
- **Special Activities**: Bonus points for participating in special activities

Points can be viewed on user profiles and leaderboards.

### Streak Tracking

The system tracks consecutive weeks of activity:

- A streak is maintained by participating in at least one event per week
- Streaks are reset if a week is missed
- Streak bonuses increase with the length of the streak
- Special badges are awarded for maintaining streaks

## Database Connection Management

The application implements connection pooling for PostgreSQL with the following parameters:

- **Pool Size**: 5 (default connections in pool)
- **Max Overflow**: 10 (maximum additional connections)
- **Pool Timeout**: 30 seconds (time to wait for a connection)
- **Pool Recycle**: 1800 seconds (connection lifetime)

## Indexes and Performance Optimizations

The following indexes are implemented for performance:

```sql
-- User lookup optimization
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Event filtering optimization
CREATE INDEX idx_events_start_time ON events(start_time);
CREATE INDEX idx_events_event_type ON events(event_type);

-- Registration queries optimization
CREATE INDEX idx_registrations_user_id ON registrations(user_id);
CREATE INDEX idx_registrations_event_id ON registrations(event_id);
CREATE INDEX idx_registrations_status ON registrations(status);

-- Payment queries optimization
CREATE INDEX idx_payment_registration_id ON payment(registration_id);
CREATE INDEX idx_payment_user_id ON payment(user_id);
CREATE INDEX idx_payment_event_id ON payment(event_id);
CREATE INDEX idx_payment_payment_date ON payment(payment_date);

-- Badge queries optimization
CREATE INDEX idx_user_badges_user_id ON user_badges(user_id);
CREATE INDEX idx_user_badges_badge_id ON user_badges(badge_id);

-- Points queries optimization
CREATE INDEX idx_points_transactions_user_id ON points_transactions(user_id);
CREATE INDEX idx_points_transactions_transaction_date ON points_transactions(transaction_date);

-- Attendance tracking optimization
CREATE INDEX idx_event_attendees_user_id ON event_attendees(user_id);
CREATE INDEX idx_event_attendees_event_id ON event_attendees(event_id);
```

## Data Migration and Maintenance

The application includes utilities for database maintenance:

- **Sequence Reset**: `reset_postgres_sequences.py` for resetting PostgreSQL sequences
- **Data Migration**: Scripts for migrating between database systems
- **Backup Utilities**: Automated backup configurations
