from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date, timedelta
from app.models.models import (
    User, Module, Lesson, Task, Achievement,
    UserProgress, UserAchievement, CodeSubmission, UserStreak
)
from app.schemas.schemas import UserCreate, DashboardStats


class UserService:
    """User service for business logic."""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create new user."""
        from app.core.security import get_password_hash
        
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Initialize streak for new user
        streak = UserStreak(user_id=user.id)
        db.add(streak)
        db.commit()
        
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def update_streak(db: Session, user_id: int) -> UserStreak:
        """Update user streak based on activity."""
        streak = db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
        if not streak:
            streak = UserStreak(user_id=user_id)
            db.add(streak)
        
        today = datetime.utcnow().date()
        
        if streak.last_activity_date:
            last_date = streak.last_activity_date.date()
            days_diff = (today - last_date).days
            
            if days_diff == 0:
                # Already active today
                pass
            elif days_diff == 1:
                # Consecutive day
                streak.current_streak += 1
                streak.longest_streak = max(streak.longest_streak, streak.current_streak)
            else:
                # Streak broken
                streak.current_streak = 1
        else:
            # First activity
            streak.current_streak = 1
        
        streak.last_activity_date = datetime.utcnow()
        db.commit()
        db.refresh(streak)
        return streak


class ModuleService:
    """Module service."""
    
    @staticmethod
    def get_all_modules(db: Session, published_only: bool = True) -> List[Module]:
        """Get all modules."""
        query = db.query(Module)
        if published_only:
            query = query.filter(Module.is_published == True)
        return query.order_by(Module.order).all()
    
    @staticmethod
    def get_module_by_id(db: Session, module_id: int) -> Optional[Module]:
        """Get module by ID."""
        return db.query(Module).filter(Module.id == module_id).first()


class LessonService:
    """Lesson service."""
    
    @staticmethod
    def get_lessons_by_module(
        db: Session, 
        module_id: int,
        published_only: bool = True
    ) -> List[Lesson]:
        """Get lessons by module ID."""
        query = db.query(Lesson).filter(Lesson.module_id == module_id)
        if published_only:
            query = query.filter(Lesson.is_published == True)
        return query.order_by(Lesson.order).all()
    
    @staticmethod
    def get_lesson_by_id(db: Session, lesson_id: int) -> Optional[Lesson]:
        """Get lesson by ID."""
        return db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    @staticmethod
    def get_all_lessons(db: Session, published_only: bool = True) -> List[Lesson]:
        """Get all lessons."""
        query = db.query(Lesson)
        if published_only:
            query = query.filter(Lesson.is_published == True)
        return query.order_by(Lesson.order).all()


class TaskService:
    """Task service."""
    
    @staticmethod
    def get_tasks_by_lesson(
        db: Session,
        lesson_id: int,
        published_only: bool = True
    ) -> List[Task]:
        """Get tasks by lesson ID."""
        query = db.query(Task).filter(Task.lesson_id == lesson_id)
        if published_only:
            query = query.filter(Task.is_published == True)
        return query.order_by(Task.order).all()
    
    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        return db.query(Task).filter(Task.id == task_id).first()


class ProgressService:
    """Progress tracking service."""
    
    @staticmethod
    def mark_lesson_completed(
        db: Session,
        user_id: int,
        lesson_id: int,
        score: float = 100.0
    ) -> UserProgress:
        """Mark lesson as completed."""
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id == lesson_id
        ).first()
        
        if progress:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
            progress.score = score
        else:
            progress = UserProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=True,
                completed_at=datetime.utcnow(),
                score=score
            )
            db.add(progress)
        
        db.commit()
        db.refresh(progress)
        return progress
    
    @staticmethod
    def get_user_progress(
        db: Session,
        user_id: int
    ) -> List[UserProgress]:
        """Get user's progress."""
        return db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).all()
    
    @staticmethod
    def get_dashboard_stats(db: Session, user_id: int) -> DashboardStats:
        """Get dashboard statistics for user."""
        total_lessons = db.query(Lesson).filter(Lesson.is_published == True).count()
        completed_lessons = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.is_completed == True
        ).count()
        
        total_tasks = db.query(Task).filter(Task.is_published == True).count()
        completed_tasks = db.query(CodeSubmission).filter(
            CodeSubmission.user_id == user_id,
            CodeSubmission.is_correct == True
        ).distinct(CodeSubmission.task_id).count()
        
        streak = db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
        current_streak = streak.current_streak if streak else 0
        longest_streak = streak.longest_streak if streak else 0
        
        total_achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).count()
        
        total_submissions = db.query(CodeSubmission).filter(
            CodeSubmission.user_id == user_id
        ).count()
        
        completion_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        return DashboardStats(
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            completion_percentage=round(completion_percentage, 2),
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            current_streak=current_streak,
            longest_streak=longest_streak,
            total_achievements=total_achievements,
            total_submissions=total_submissions
        )


class AchievementService:
    """Achievement service."""
    
    @staticmethod
    def get_all_achievements(db: Session) -> List[Achievement]:
        """Get all achievements."""
        return db.query(Achievement).filter(Achievement.is_active == True).all()
    
    @staticmethod
    def get_user_achievements(db: Session, user_id: int) -> List[UserAchievement]:
        """Get user's earned achievements."""
        return db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()
    
    @staticmethod
    def check_and_award_achievements(db: Session, user_id: int) -> List[Achievement]:
        """Check and award achievements based on user progress."""
        awarded = []
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return awarded
        
        # Get user stats
        completed_lessons = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.is_completed == True
        ).count()
        
        streak = db.query(UserStreak).filter(UserStreak.user_id == user_id).first()
        current_streak = streak.current_streak if streak else 0
        
        # Get all achievements
        achievements = db.query(Achievement).filter(Achievement.is_active == True).all()
        earned_ids = [ua.achievement_id for ua in user.achievements]
        
        for achievement in achievements:
            if achievement.id in earned_ids:
                continue
            
            should_award = False
            
            # Check first login
            if achievement.requirement_type == "first_login":
                should_award = True
            
            # Check lessons completed
            elif achievement.requirement_type == "lessons_completed":
                should_award = completed_lessons >= achievement.requirement_value
            
            # Check streak
            elif achievement.requirement_type == "streak_days":
                should_award = current_streak >= achievement.requirement_value
            
            if should_award:
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
                db.add(user_achievement)
                awarded.append(achievement)
        
        if awarded:
            db.commit()
        
        return awarded
