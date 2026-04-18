from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    submissions = relationship("CodeSubmission", back_populates="user", cascade="all, delete-orphan")
    streaks = relationship("UserStreak", back_populates="user", cascade="all, delete-orphan")


class Module(Base):
    """Course module model."""
    
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    title_ru = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=False)
    description_ru = Column(Text)
    description_en = Column(Text)
    order = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")


class Lesson(Base):
    """Lesson model."""
    
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    title_ru = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=False)
    content_ru = Column(Text, nullable=False)
    content_en = Column(Text, nullable=False)
    order = Column(Integer, default=0)
    difficulty = Column(String(20), default="beginner")  # beginner, intermediate, advanced
    estimated_time = Column(Integer, default=10)  # minutes
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    module = relationship("Module", back_populates="lessons")
    tasks = relationship("Task", back_populates="lesson", cascade="all, delete-orphan")


class Task(Base):
    """Task/Exercise model."""
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    title_ru = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=False)
    description_ru = Column(Text, nullable=False)
    description_en = Column(Text, nullable=False)
    starter_code = Column(Text, default="")
    expected_output = Column(Text)
    test_cases = Column(Text)  # JSON string with test cases
    order = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lesson = relationship("Lesson", back_populates="tasks")


class Achievement(Base):
    """Achievement model."""
    
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    name_ru = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    description_ru = Column(Text)
    description_en = Column(Text)
    icon = Column(String(255))
    requirement_type = Column(String(50))  # lessons_completed, streak_days, etc.
    requirement_value = Column(Integer)
    points = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserProgress(Base):
    """User progress tracking."""
    
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")


class UserAchievement(Base):
    """User achievements."""
    
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="achievements")


class CodeSubmission(Base):
    """Code submission history."""
    
    __tablename__ = "code_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    code = Column(Text, nullable=False)
    output = Column(Text)
    error = Column(Text)
    is_correct = Column(Boolean, default=False)
    execution_time = Column(Float)  # seconds
    memory_used = Column(Integer)  # MB
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="submissions")


class UserStreak(Base):
    """User learning streak."""
    
    __tablename__ = "user_streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="streaks")
