from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.session import get_db
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, Token
from app.services.services import UserService
from app.core.security import verify_password, get_password_hash
from app.core.jwt import create_access_token
from app.core.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user."""
    # Check if user exists
    existing_user = UserService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check username
    existing_username = db.query(UserService).filter(
        UserService.username == user_data.username
    ).first()
    
    # Create user
    user = UserService.create_user(db, user_data)
    
    return user


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    user = UserService.get_user_by_email(db, login_data.email)
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token = create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Update streak on login
    UserService.update_streak(db, user.id)
    
    # Check for achievements
    from app.services.services import AchievementService
    AchievementService.check_and_award_achievements(db, user.id)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(lambda: None)  # Will be replaced with actual dependency
):
    """Get current user information."""
    # This will use the dependency injection for auth
    return current_user
