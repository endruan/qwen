from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Auth schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# Module schemas
class ModuleBase(BaseModel):
    title_ru: str
    title_en: str
    description_ru: Optional[str] = None
    description_en: Optional[str] = None
    order: int = 0


class ModuleCreate(ModuleBase):
    pass


class ModuleResponse(ModuleBase):
    id: int
    is_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Lesson schemas
class LessonBase(BaseModel):
    title_ru: str
    title_en: str
    content_ru: str
    content_en: str
    order: int = 0
    difficulty: str = "beginner"
    estimated_time: int = 10


class LessonCreate(LessonBase):
    module_id: int


class LessonResponse(LessonBase):
    id: int
    module_id: int
    is_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Task schemas
class TaskBase(BaseModel):
    title_ru: str
    title_en: str
    description_ru: str
    description_en: str
    starter_code: Optional[str] = ""
    expected_output: Optional[str] = None
    test_cases: Optional[str] = None
    order: int = 0


class TaskCreate(TaskBase):
    lesson_id: int


class TaskResponse(TaskBase):
    id: int
    lesson_id: int
    is_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Achievement schemas
class AchievementBase(BaseModel):
    name_ru: str
    name_en: str
    description_ru: Optional[str] = None
    description_en: Optional[str] = None
    icon: Optional[str] = None
    requirement_type: str
    requirement_value: int
    points: int = 10


class AchievementResponse(AchievementBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True


class UserAchievementResponse(BaseModel):
    id: int
    achievement: AchievementResponse
    earned_at: datetime
    
    class Config:
        from_attributes = True


# Progress schemas
class UserProgressBase(BaseModel):
    lesson_id: int
    is_completed: bool = False
    score: float = 0.0


class UserProgressResponse(UserProgressBase):
    id: int
    user_id: int
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Code execution schemas
class CodeExecutionRequest(BaseModel):
    code: str
    task_id: Optional[int] = None


class CodeExecutionResponse(BaseModel):
    output: str
    error: Optional[str] = None
    is_correct: bool = False
    execution_time: float
    memory_used: int


# Dashboard schemas
class DashboardStats(BaseModel):
    total_lessons: int
    completed_lessons: int
    completion_percentage: float
    total_tasks: int
    completed_tasks: int
    current_streak: int
    longest_streak: int
    total_achievements: int
    total_submissions: int


class LessonProgress(BaseModel):
    lesson_id: int
    title_ru: str
    title_en: str
    is_completed: bool
    completed_at: Optional[datetime]
