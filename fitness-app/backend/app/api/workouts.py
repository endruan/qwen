from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..db.database import get_db
from ..schemas.schemas import (
    ExerciseCreate, ExerciseResponse,
    WorkoutCreate, WorkoutUpdate, WorkoutResponse
)
from ..services.services import (
    get_exercises, create_exercise,
    get_workouts, get_workout, create_workout, update_workout
)
from ..core.deps import get_current_user
from ..models.models import User

router = APIRouter(prefix="/workouts", tags=["Workouts"])


# Exercises endpoints
@router.get("/exercises", response_model=List[ExerciseResponse])
def list_exercises(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all exercises"""
    return get_exercises(db)


@router.post("/exercises", response_model=ExerciseResponse)
def create_exercise_endpoint(
    exercise: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new exercise"""
    return create_exercise(db, exercise)


# Workouts endpoints
@router.get("", response_model=List[WorkoutResponse])
def list_workouts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all user workouts"""
    return get_workouts(db, current_user.id)


@router.post("", response_model=WorkoutResponse)
def create_workout_endpoint(
    workout: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new workout with exercises"""
    return create_workout(db, workout, current_user.id)


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout_endpoint(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific workout"""
    workout = get_workout(db, workout_id, current_user.id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.put("/{workout_id}", response_model=WorkoutResponse)
def update_workout_endpoint(
    workout_id: int,
    workout_update: WorkoutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a workout"""
    updated = update_workout(db, workout_id, current_user.id, workout_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Workout not found")
    return updated


@router.delete("/{workout_id}")
def delete_workout_endpoint(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a workout"""
    from ..models.models import Workout
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    db.delete(workout)
    db.commit()
    
    return {"message": "Workout deleted successfully"}
