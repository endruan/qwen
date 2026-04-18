from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.schemas import DashboardStats, UserProgressResponse, UserAchievementResponse, AchievementResponse
from app.services.services import ProgressService, AchievementService
from app.core.dependencies import get_current_active_user
from app.models.models import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard statistics for current user."""
    return ProgressService.get_dashboard_stats(db, current_user.id)


@router.get("/progress", response_model=List[UserProgressResponse])
def get_user_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's lesson progress."""
    return ProgressService.get_user_progress(db, current_user.id)


@router.get("/achievements", response_model=List[UserAchievementResponse])
def get_user_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's earned achievements."""
    user_achievements = AchievementService.get_user_achievements(db, current_user.id)
    
    result = []
    for ua in user_achievements:
        achievement = db.query(AchievementService).filter(
            AchievementService.id == ua.achievement_id
        ).first()
        if achievement:
            result.append({
                "id": ua.id,
                "achievement": achievement,
                "earned_at": ua.earned_at
            })
    
    return result


@router.get("/all-achievements", response_model=List[AchievementResponse])
def get_all_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all available achievements."""
    return AchievementService.get_all_achievements(db)
