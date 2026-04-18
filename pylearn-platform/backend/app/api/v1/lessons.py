from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.schemas import LessonResponse, LessonCreate
from app.services.services import LessonService, ModuleService
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.models.models import User

router = APIRouter(prefix="/lessons", tags=["Lessons"])


@router.get("/", response_model=List[LessonResponse])
def get_all_lessons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all lessons."""
    return LessonService.get_all_lessons(db)


@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get lesson by ID."""
    lesson = LessonService.get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    return lesson


@router.get("/module/{module_id}", response_model=List[LessonResponse])
def get_lessons_by_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get lessons by module ID."""
    # Verify module exists
    module = ModuleService.get_module_by_id(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    return LessonService.get_lessons_by_module(db, module_id)


@router.post("/", response_model=LessonResponse)
def create_lesson(
    lesson_data: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Create new lesson (admin only)."""
    # Verify module exists
    module = ModuleService.get_module_by_id(db, lesson_data.module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    lesson = Lesson(**lesson_data.dict())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson
