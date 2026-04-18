from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User, Lesson, Section, Task, UserProgress, Quiz
from app.schemas.user import (
    LessonResponse, LessonDetailResponse, LessonCreate, LessonUpdate,
    SectionResponse, SectionWithLessons, SectionCreate, SectionUpdate,
    TaskResponse, TaskCreate, TaskUpdate, QuizResponse, QuizCreate, QuizUpdate
)
from app.core.jwt import get_current_user


router = APIRouter()


# Section endpoints
@router.get("/sections", response_model=List[SectionResponse])
def get_all_sections(db: Session = Depends(get_db)):
    sections = db.query(Section).filter(
        Section.is_published == True
    ).order_by(Section.order_index).all()
    
    result = []
    for section in sections:
        lessons_count = db.query(Lesson).filter(
            Lesson.section_id == section.id,
            Lesson.is_published == True
        ).count()
        
        section_dict = {
            "id": section.id,
            "title": section.title,
            "slug": section.slug,
            "description": section.description,
            "order_index": section.order_index,
            "icon": section.icon,
            "is_published": section.is_published,
            "created_at": section.created_at,
            "lessons_count": lessons_count
        }
        result.append(section_dict)
    
    return result


@router.get("/sections/{section_id}", response_model=SectionWithLessons)
def get_section_with_lessons(section_id: int, db: Session = Depends(get_db)):
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    lessons = db.query(Lesson).filter(
        Lesson.section_id == section_id,
        Lesson.is_published == True
    ).order_by(Lesson.order_index).all()
    
    lessons_count = len(lessons)
    
    return {
        "id": section.id,
        "title": section.title,
        "slug": section.slug,
        "description": section.description,
        "order_index": section.order_index,
        "icon": section.icon,
        "is_published": section.is_published,
        "created_at": section.created_at,
        "lessons_count": lessons_count,
        "lessons": lessons
    }


# Lesson endpoints
@router.get("/lessons", response_model=List[LessonResponse])
def get_all_lessons(
    skip: int = 0,
    limit: int = 100,
    section_id: int = None,
    difficulty: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Lesson).filter(Lesson.is_published == True)
    
    if section_id:
        query = query.filter(Lesson.section_id == section_id)
    if difficulty:
        query = query.filter(Lesson.difficulty == difficulty)
    
    lessons = query.order_by(Lesson.order_index).offset(skip).limit(limit).all()
    return lessons


@router.get("/lessons/{lesson_id}", response_model=LessonDetailResponse)
def get_lesson_detail(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    tasks = db.query(Task).filter(Task.lesson_id == lesson_id).order_by(Task.order_index).all()
    quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson_id).first()
    
    # Check user progress
    is_completed = False
    progress_score = 0.0
    
    if current_user:
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.lesson_id == lesson_id
        ).first()
        
        if progress:
            is_completed = progress.is_completed
            progress_score = progress.score
    
    return {
        "id": lesson.id,
        "title": lesson.title,
        "slug": lesson.slug,
        "description": lesson.description,
        "content": lesson.content,
        "order_index": lesson.order_index,
        "section_id": lesson.section_id,
        "difficulty": lesson.difficulty,
        "estimated_time": lesson.estimated_time,
        "xp_reward": lesson.xp_reward,
        "is_published": lesson.is_published,
        "created_at": lesson.created_at,
        "updated_at": lesson.updated_at,
        "tasks": tasks,
        "quiz": quiz,
        "is_completed": is_completed,
        "progress_score": progress_score
    }


@router.get("/lessons/slug/{slug}", response_model=LessonDetailResponse)
def get_lesson_by_slug(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.slug == slug).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    tasks = db.query(Task).filter(Task.lesson_id == lesson.id).order_by(Task.order_index).all()
    quiz = db.query(Quiz).filter(Quiz.lesson_id == lesson.id).first()
    
    is_completed = False
    progress_score = 0.0
    
    if current_user:
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.lesson_id == lesson.id
        ).first()
        
        if progress:
            is_completed = progress.is_completed
            progress_score = progress.score
    
    return {
        "id": lesson.id,
        "title": lesson.title,
        "slug": lesson.slug,
        "description": lesson.description,
        "content": lesson.content,
        "order_index": lesson.order_index,
        "section_id": lesson.section_id,
        "difficulty": lesson.difficulty,
        "estimated_time": lesson.estimated_time,
        "xp_reward": lesson.xp_reward,
        "is_published": lesson.is_published,
        "created_at": lesson.created_at,
        "updated_at": lesson.updated_at,
        "tasks": tasks,
        "quiz": quiz,
        "is_completed": is_completed,
        "progress_score": progress_score
    }


# Admin endpoints for lessons
@router.post("/lessons", response_model=LessonResponse)
def create_lesson(
    lesson_data: LessonCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    lesson = Lesson(**lesson_data.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    update_data = lesson_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lesson, key, value)
    
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/lessons/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    db.delete(lesson)
    db.commit()
    return {"message": "Lesson deleted successfully"}


# Task endpoints
@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# Quiz endpoints
@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz
