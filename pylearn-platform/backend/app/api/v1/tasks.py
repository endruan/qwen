from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from app.db.session import get_db
from app.schemas.schemas import TaskResponse, TaskCreate, CodeExecutionRequest, CodeExecutionResponse
from app.services.services import TaskService, LessonService, ProgressService, AchievementService
from app.models.models import User, CodeSubmission
from app.core.dependencies import get_current_active_user
from app.services.code_executor import get_code_executor

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/lesson/{lesson_id}", response_model=List[TaskResponse])
def get_tasks_by_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tasks by lesson ID."""
    # Verify lesson exists
    lesson = LessonService.get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    return TaskService.get_tasks_by_lesson(db, lesson_id)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get task by ID."""
    task = TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.post("/{task_id}/execute", response_model=CodeExecutionResponse)
def execute_task_code(
    task_id: int,
    execution_request: CodeExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Execute code for a task and check correctness."""
    task = TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    executor = get_code_executor()
    
    # Parse test cases
    test_cases = []
    if task.test_cases:
        try:
            test_cases = json.loads(task.test_cases)
        except json.JSONDecodeError:
            test_cases = []
    
    # Execute code
    if test_cases:
        all_passed, results = executor.run_tests(execution_request.code, test_cases)
        output = "\n".join([
            f"Test {i+1}: {'✓ Passed' if r['passed'] else '✗ Failed'}"
            for i, r in enumerate(results)
        ])
        error = None
        is_correct = all_passed
        execution_time = sum(r.get('execution_time', 0) for r in results) / len(results)
        memory_used = max(r.get('memory_used', 0) for r in results)
    else:
        # No test cases, just run the code
        output, error, execution_time, memory_used = executor.execute_code(execution_request.code)
        is_correct = error == ""
        
        if task.expected_output:
            is_correct = executor.check_output(output, task.expected_output)
    
    # Save submission
    submission = CodeSubmission(
        user_id=current_user.id,
        task_id=task_id,
        code=execution_request.code,
        output=output,
        error=error,
        is_correct=is_correct,
        execution_time=execution_time,
        memory_used=memory_used
    )
    db.add(submission)
    
    # If correct, mark lesson as completed and check achievements
    if is_correct:
        ProgressService.mark_lesson_completed(db, current_user.id, task.lesson_id)
        AchievementService.check_and_award_achievements(db, current_user.id)
    
    db.commit()
    
    return CodeExecutionResponse(
        output=output,
        error=error,
        is_correct=is_correct,
        execution_time=execution_time,
        memory_used=memory_used
    )


@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(lambda: None)  # Admin only - to be implemented
):
    """Create new task (admin only)."""
    # Verify lesson exists
    lesson = LessonService.get_lesson_by_id(db, task_data.lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    task = Task(**task_data.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
