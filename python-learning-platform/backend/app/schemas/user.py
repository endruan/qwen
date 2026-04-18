from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Auth schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    total_xp: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None


# Lesson schemas
class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: str
    order_index: int = 0
    difficulty: str = "beginner"
    estimated_time: int = 10
    xp_reward: int = 10
    is_published: bool = True


class LessonCreate(LessonBase):
    section_id: int
    slug: str


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    order_index: Optional[int] = None
    difficulty: Optional[str] = None
    estimated_time: Optional[int] = None
    xp_reward: Optional[int] = None
    is_published: Optional[bool] = None
    slug: Optional[str] = None


class LessonResponse(LessonBase):
    id: int
    slug: str
    section_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LessonDetailResponse(LessonResponse):
    tasks: List["TaskResponse"] = []
    quiz: Optional["QuizResponse"] = None
    is_completed: bool = False
    progress_score: float = 0.0


# Section schemas
class SectionBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int = 0
    icon: str = "book"
    is_published: bool = True


class SectionCreate(SectionBase):
    slug: str


class SectionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    icon: Optional[str] = None
    is_published: Optional[bool] = None
    slug: Optional[str] = None


class SectionResponse(SectionBase):
    id: int
    slug: str
    created_at: datetime
    lessons_count: int = 0
    
    class Config:
        from_attributes = True


class SectionWithLessons(SectionResponse):
    lessons: List[LessonResponse] = []


# Task schemas
class TaskBase(BaseModel):
    title: str
    description: str
    starter_code: Optional[str] = None
    expected_output: Optional[str] = None
    test_cases: Optional[str] = None
    solution_code: Optional[str] = None
    order_index: int = 0
    task_type: str = "coding"


class TaskCreate(TaskBase):
    lesson_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    starter_code: Optional[str] = None
    expected_output: Optional[str] = None
    test_cases: Optional[str] = None
    solution_code: Optional[str] = None
    order_index: Optional[int] = None
    task_type: Optional[str] = None


class TaskResponse(TaskBase):
    id: int
    lesson_id: int
    
    class Config:
        from_attributes = True


# Quiz schemas
class QuizBase(BaseModel):
    questions: str  # JSON string
    passing_score: int = 70


class QuizCreate(QuizBase):
    lesson_id: int


class QuizUpdate(BaseModel):
    questions: Optional[str] = None
    passing_score: Optional[int] = None


class QuizResponse(QuizBase):
    id: int
    lesson_id: int
    
    class Config:
        from_attributes = True


# Progress schemas
class UserProgressBase(BaseModel):
    is_completed: bool = False
    score: float = 0.0
    time_spent: int = 0
    attempts: int = 0


class UserProgressCreate(UserProgressBase):
    user_id: int
    lesson_id: int


class UserProgressResponse(UserProgressBase):
    id: int
    user_id: int
    lesson_id: int
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProgressSummary(BaseModel):
    total_lessons: int
    completed_lessons: int
    completion_percentage: float
    total_xp: int
    current_streak: int
    longest_streak: int


# Achievement schemas
class AchievementBase(BaseModel):
    name: str
    description: str
    icon: Optional[str] = None
    category: str = "general"
    requirement_type: str
    requirement_value: int
    xp_reward: int = 50
    is_hidden: bool = False


class AchievementCreate(AchievementBase):
    pass


class AchievementResponse(AchievementBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserAchievementResponse(BaseModel):
    id: int
    achievement: AchievementResponse
    earned_at: datetime
    
    class Config:
        from_attributes = True


# Code submission schemas
class CodeSubmissionCreate(BaseModel):
    task_id: int
    code: str


class CodeSubmissionResponse(BaseModel):
    id: int
    task_id: int
    code: str
    output: Optional[str] = None
    error: Optional[str] = None
    is_correct: bool
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CodeExecutionRequest(BaseModel):
    code: str
    timeout: int = 10


class CodeExecutionResponse(BaseModel):
    output: str = ""
    error: str = ""
    execution_time: float = 0.0
    memory_used: int = 0
    is_success: bool = False


# Favorite schemas
class FavoriteLessonCreate(BaseModel):
    lesson_id: int


class FavoriteLessonResponse(BaseModel):
    id: int
    lesson_id: int
    lesson: LessonResponse
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard/Stats schemas
class DashboardStats(BaseModel):
    total_lessons: int
    completed_lessons: int
    completion_percentage: float
    total_xp: int
    current_streak: int
    longest_streak: int
    total_submissions: int
    achievements_count: int
    recent_activity: List[dict] = []


# Update forward references
UserResponse.model_rebuild()
LessonDetailResponse.model_rebuild()
SectionWithLessons.model_rebuild()
TaskResponse.model_rebuild()
QuizResponse.model_rebuild()
