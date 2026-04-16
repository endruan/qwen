from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from ..db.database import get_db
from ..schemas.schemas import UserRegister, UserLogin, Token, UserResponse, UserMetricCreate, UserMetricResponse
from ..services.services import create_user, authenticate_user, get_user_metrics, create_user_metric, calculate_user_goals
from ..core.security import create_access_token
from ..core.deps import get_current_user
from ..models.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return create_user(db, user_data)


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=1440)  # 24 hours
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/goals")
def get_user_goals_endpoint(current_user: User = Depends(get_current_user)):
    """Get calculated nutrition goals for current user"""
    goals = calculate_user_goals(current_user)
    return goals


@router.post("/metrics", response_model=UserMetricResponse)
def add_metric(
    metric_data: UserMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add user body metrics"""
    return create_user_metric(db, current_user.id, metric_data)


@router.get("/metrics", response_model=List[UserMetricResponse])
def get_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's metric history"""
    return get_user_metrics(db, current_user.id)
