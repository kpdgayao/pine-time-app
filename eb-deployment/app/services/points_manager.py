from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app import models


class PointsManager:
    """
    Service class to handle points and badges logic.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def award_points(
        self, 
        user_id: int, 
        points: int, 
        transaction_type: str, 
        description: str,
        event_id: Optional[int] = None
    ) -> models.PointsTransaction:
        """
        Award points to a user and create a transaction record.
        
        Args:
            user_id: ID of the user to award points to
            points: Number of points to award (positive for earning, negative for redeeming)
            transaction_type: Type of transaction (earned, redeemed, expired)
            description: Description of the transaction
            event_id: Optional ID of the related event
            
        Returns:
            The created PointsTransaction object
        """
        # Get the user
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Create transaction record
        transaction = models.PointsTransaction(
            user_id=user_id,
            points=points,
            transaction_type=transaction_type,
            description=description,
            event_id=event_id,
            transaction_date=datetime.utcnow()
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        # Check if user qualifies for any badges after this transaction
        self.check_and_award_badges(user_id)
        
        return transaction
    
    def get_user_points_balance(self, user_id: int) -> int:
        """
        Get the current points balance for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            The current points balance
        """
        # Sum all points transactions for the user
        transactions = self.db.query(models.PointsTransaction).filter(
            models.PointsTransaction.user_id == user_id
        ).all()
        
        balance = sum(transaction.points for transaction in transactions)
        return balance
    
    def get_user_badges(self, user_id: int) -> List[models.Badge]:
        """
        Get all badges earned by a user, organized by category and level.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary of badges organized by category and level
        """
        # Get all badges for the user
        badges = self.db.query(models.Badge).filter(
            models.Badge.user_id == user_id
        ).all()
        
        # Organize badges by category and level
        result = []
        for badge in badges:
            # Extract badge level from badge_type (e.g., "event_master_bronze")
            badge_parts = badge.badge_type.split('_')
            level = badge_parts[-1] if badge_parts[-1] in ['bronze', 'silver', 'gold'] else None
            
            # Create badge info with level information
            badge_info = {
                "id": badge.id,
                "badge_type": badge.badge_type,
                "name": badge.name,
                "description": badge.description,
                "image_url": badge.image_url,
                "earned_date": badge.earned_date,
                "level": level
            }
            result.append(badge_info)
            
        return result
    
    def calculate_attendance_streak(self, user_id: int) -> int:
        """
        Calculate the current weekly attendance streak for a user.
        
        A streak is defined as consecutive weeks where the user attended at least one event.
        
        Args:
            user_id: ID of the user
            
        Returns:
            The current streak count in weeks
        """
        from datetime import timedelta
        
        # Get all attended events for the user, ordered by date
        attended_registrations = self.db.query(models.Registration).filter(
            models.Registration.user_id == user_id,
            models.Registration.status == "attended"
        ).all()
        
        if not attended_registrations:
            return 0
            
        # Get event dates for each registration
        event_dates = []
        for registration in attended_registrations:
            event = self.db.query(models.Event).filter(models.Event.id == registration.event_id).first()
            if event:
                event_dates.append(event.start_time.date())
                
        # Sort dates
        event_dates.sort(reverse=True)
        
        # Calculate streak by checking consecutive weeks
        streak = 1
        current_week = event_dates[0].isocalendar()[1]  # Get week number of most recent event
        current_year = event_dates[0].isocalendar()[0]  # Get year of most recent event
        
        for i in range(1, len(event_dates)):
            date = event_dates[i]
            week = date.isocalendar()[1]
            year = date.isocalendar()[0]
            
            # Check if this date is in the previous week
            if (year == current_year and week == current_week - 1) or \
               (year == current_year - 1 and current_week == 1 and week == 52):
                streak += 1
                current_week = week
                current_year = year
            # If same week as current, continue checking
            elif year == current_year and week == current_week:
                continue
            # Break in the streak
            else:
                break
                
        return streak
    
    def check_and_award_badges(self, user_id: int) -> List[models.Badge]:
        """
        Check if a user qualifies for any badges and award them if they do.
        
        Args:
            user_id: ID of the user to check
            
        Returns:
            List of newly awarded badges
        """
        # Get user's current badges
        current_badges = self.db.query(models.Badge).filter(
            models.Badge.user_id == user_id
        ).all()
        current_badge_types = [badge.badge_type for badge in current_badges]
        
        # Get user's event attendance
        attended_events = self.db.query(models.Registration).filter(
            models.Registration.user_id == user_id,
            models.Registration.status == "attended"
        ).all()
        
        # Get user's points balance
        points_balance = self.get_user_points_balance(user_id)
        
        # Calculate attendance streak
        streak_weeks = self.calculate_attendance_streak(user_id)
        
        # Check for event attendance badges
        newly_awarded_badges = []
        
        # Event Master Badge (attended events) - Bronze, Silver, Gold levels
        if "event_master_bronze" not in current_badge_types and len(attended_events) >= 5:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="event_master_bronze",
                name="Event Master Bronze",
                description="Attended 5 or more events",
                image_url="/static/badges/event_master_bronze.png"
            )
            newly_awarded_badges.append(badge)
            
        if "event_master_silver" not in current_badge_types and len(attended_events) >= 15:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="event_master_silver",
                name="Event Master Silver",
                description="Attended 15 or more events",
                image_url="/static/badges/event_master_silver.png"
            )
            newly_awarded_badges.append(badge)
            
        if "event_master_gold" not in current_badge_types and len(attended_events) >= 30:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="event_master_gold",
                name="Event Master Gold",
                description="Attended 30 or more events",
                image_url="/static/badges/event_master_gold.png"
            )
            newly_awarded_badges.append(badge)
        
        # Points Collector Badge (earned points) - Bronze, Silver, Gold levels
        if "points_collector_bronze" not in current_badge_types and points_balance >= 500:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="points_collector_bronze",
                name="Points Collector Bronze",
                description="Earned 500 or more points",
                image_url="/static/badges/points_collector_bronze.png"
            )
            newly_awarded_badges.append(badge)
            
        if "points_collector_silver" not in current_badge_types and points_balance >= 2000:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="points_collector_silver",
                name="Points Collector Silver",
                description="Earned 2000 or more points",
                image_url="/static/badges/points_collector_silver.png"
            )
            newly_awarded_badges.append(badge)
            
        if "points_collector_gold" not in current_badge_types and points_balance >= 5000:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="points_collector_gold",
                name="Points Collector Gold",
                description="Earned 5000 or more points",
                image_url="/static/badges/points_collector_gold.png"
            )
            newly_awarded_badges.append(badge)
        
        # Streak Master Badge (consecutive weekly attendance) - Bronze, Silver, Gold levels
        if "streak_master_bronze" not in current_badge_types and streak_weeks >= 3:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="streak_master_bronze",
                name="Streak Master Bronze",
                description="Attended events for 3 consecutive weeks",
                image_url="/static/badges/streak_master_bronze.png"
            )
            newly_awarded_badges.append(badge)
            
        if "streak_master_silver" not in current_badge_types and streak_weeks >= 8:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="streak_master_silver",
                name="Streak Master Silver",
                description="Attended events for 8 consecutive weeks",
                image_url="/static/badges/streak_master_silver.png"
            )
            newly_awarded_badges.append(badge)
            
        if "streak_master_gold" not in current_badge_types and streak_weeks >= 12:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="streak_master_gold",
                name="Streak Master Gold",
                description="Attended events for 12 consecutive weeks",
                image_url="/static/badges/streak_master_gold.png"
            )
            newly_awarded_badges.append(badge)
        
        # Check for event type specific badges
        event_types = {}
        for registration in attended_events:
            event = self.db.query(models.Event).filter(models.Event.id == registration.event_id).first()
            if event:
                event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        # Trivia Champion Badge (attended trivia events) - Bronze, Silver, Gold levels
        if "trivia_champion_bronze" not in current_badge_types and event_types.get("trivia", 0) >= 3:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="trivia_champion_bronze",
                name="Trivia Champion Bronze",
                description="Attended 3 or more trivia events",
                image_url="/static/badges/trivia_champion_bronze.png"
            )
            newly_awarded_badges.append(badge)
            
        if "trivia_champion_silver" not in current_badge_types and event_types.get("trivia", 0) >= 8:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="trivia_champion_silver",
                name="Trivia Champion Silver",
                description="Attended 8 or more trivia events",
                image_url="/static/badges/trivia_champion_silver.png"
            )
            newly_awarded_badges.append(badge)
            
        if "trivia_champion_gold" not in current_badge_types and event_types.get("trivia", 0) >= 15:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="trivia_champion_gold",
                name="Trivia Champion Gold",
                description="Attended 15 or more trivia events",
                image_url="/static/badges/trivia_champion_gold.png"
            )
            newly_awarded_badges.append(badge)
        
        # Game Night Enthusiast Badge (attended game night events) - Bronze, Silver, Gold levels
        if "game_night_enthusiast_bronze" not in current_badge_types and event_types.get("game_night", 0) >= 3:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="game_night_enthusiast_bronze",
                name="Game Night Enthusiast Bronze",
                description="Attended 3 or more game night events",
                image_url="/static/badges/game_night_enthusiast_bronze.png"
            )
            newly_awarded_badges.append(badge)
            
        if "game_night_enthusiast_silver" not in current_badge_types and event_types.get("game_night", 0) >= 8:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="game_night_enthusiast_silver",
                name="Game Night Enthusiast Silver",
                description="Attended 8 or more game night events",
                image_url="/static/badges/game_night_enthusiast_silver.png"
            )
            newly_awarded_badges.append(badge)
            
        if "game_night_enthusiast_gold" not in current_badge_types and event_types.get("game_night", 0) >= 15:
            badge = self._create_badge(
                user_id=user_id,
                badge_type="game_night_enthusiast_gold",
                name="Game Night Enthusiast Gold",
                description="Attended 15 or more game night events",
                image_url="/static/badges/game_night_enthusiast_gold.png"
            )
            newly_awarded_badges.append(badge)
        
        return newly_awarded_badges
    
    def _create_badge(
        self, 
        user_id: int, 
        badge_type: str, 
        name: str, 
        description: str, 
        image_url: Optional[str] = None
    ) -> models.Badge:
        """
        Helper method to create a badge for a user.
        """
        badge = models.Badge(
            user_id=user_id,
            badge_type=badge_type,
            name=name,
            description=description,
            image_url=image_url,
            earned_date=datetime.utcnow()
        )
        
        self.db.add(badge)
        self.db.commit()
        self.db.refresh(badge)
        
        return badge