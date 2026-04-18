from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.jwt import get_current_user


router = APIRouter()


@router.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "avatar_url": current_user.avatar_url,
        "total_xp": current_user.total_xp,
        "current_streak": current_user.current_streak,
        "longest_streak": current_user.longest_streak,
        "is_admin": current_user.is_admin
    }


@router.put("/profile")
def update_profile(
    first_name: str = None,
    last_name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if first_name is not None:
        current_user.first_name = first_name
    if last_name is not None:
        current_user.last_name = last_name
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "total_xp": current_user.total_xp,
        "current_streak": current_user.current_streak,
        "longest_streak": current_user.longest_streak
    }
