from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import docker
import json
import time
import tempfile
import os

from app.db.session import get_db
from app.models.user import User, Task, CodeSubmission, UserProgress, Lesson
from app.schemas.user import (
    CodeSubmissionCreate, CodeSubmissionResponse, CodeExecutionRequest,
    CodeExecutionResponse, ProgressSummary, DashboardStats
)
from app.core.jwt import get_current_user


router = APIRouter()


def execute_python_code(code: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Execute Python code in a Docker container with resource limits.
    Returns output, error, execution time, and memory usage.
    """
    try:
        client = docker.from_env()
        
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            start_time = time.time()
            
            # Run the code in a container
            container = client.containers.run(
                "python:3.11-slim",
                command=f"python /code/{os.path.basename(temp_file)}",
                volumes={temp_file: {'bind': f'/code/{os.path.basename(temp_file)}', 'mode': 'ro'}},
                remove=True,
                mem_limit="128m",
                cpu_quota=50000,  # 50% of CPU
                network_disabled=True,
                stdout=True,
                stderr=True,
                detach=False,
                tty=False
            )
            
            end_time = time.time()
            
            output = ""
            error = ""
            
            if isinstance(container, tuple):
                output, error = container
            else:
                output = container.decode('utf-8') if isinstance(container, bytes) else str(container)
            
            return {
                "output": output,
                "error": error,
                "execution_time": round(end_time - start_time, 3),
                "memory_used": 0,  # Would need more complex tracking
                "is_success": not error.strip()
            }
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
            
    except docker.errors.DockerException as e:
        # Fallback: try to execute directly (for development)
        import subprocess
        try:
            start_time = time.time()
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            end_time = time.time()
            
            return {
                "output": result.stdout,
                "error": result.stderr,
                "execution_time": round(end_time - start_time, 3),
                "memory_used": 0,
                "is_success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "error": f"Code execution timed out after {timeout} seconds",
                "execution_time": timeout,
                "memory_used": 0,
                "is_success": False
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "execution_time": 0,
                "memory_used": 0,
                "is_success": False
            }
    except Exception as e:
        return {
            "output": "",
            "error": str(e),
            "execution_time": 0,
            "memory_used": 0,
            "is_success": False
        }


@router.post("/execute", response_model=CodeExecutionResponse)
def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    result = execute_python_code(request.code, request.timeout)
    return result


@router.post("/submit", response_model=CodeSubmissionResponse)
def submit_code(
    submission_data: CodeSubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == submission_data.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Execute the code
    result = execute_python_code(submission_data.code)
    
    # Check if correct (simple string comparison for now)
    is_correct = False
    if task.expected_output and result["is_success"]:
        is_correct = task.expected_output.strip() in result["output"] or \
                     result["output"].strip() == task.expected_output.strip()
    
    # Also check test cases if available
    if task.test_cases:
        try:
            test_cases = json.loads(task.test_cases)
            all_passed = True
            for test_case in test_cases:
                test_result = execute_python_code(test_case.get("input", ""))
                expected = test_case.get("expected", "")
                if expected not in test_result.get("output", ""):
                    all_passed = False
                    break
            is_correct = is_correct or all_passed
        except:
            pass
    
    # Save submission
    submission = CodeSubmission(
        user_id=current_user.id,
        task_id=submission_data.task_id,
        code=submission_data.code,
        output=result["output"],
        error=result["error"],
        is_correct=is_correct,
        execution_time=result["execution_time"],
        memory_used=result["memory_used"]
    )
    
    db.add(submission)
    
    # Update progress if correct
    if is_correct:
        lesson = db.query(Lesson).filter(Lesson.id == task.lesson_id).first()
        if lesson:
            progress = db.query(UserProgress).filter(
                UserProgress.user_id == current_user.id,
                UserProgress.lesson_id == lesson.id
            ).first()
            
            if not progress:
                progress = UserProgress(
                    user_id=current_user.id,
                    lesson_id=lesson.id,
                    attempts=1,
                    score=100.0,
                    is_completed=True
                )
                db.add(progress)
                
                # Add XP
                current_user.total_xp += lesson.xp_reward
            else:
                progress.attempts += 1
                if not progress.is_completed:
                    progress.is_completed = True
                    progress.completed_at = time.time()
                    progress.score = max(progress.score, 100.0)
                    current_user.total_xp += lesson.xp_reward
    
    db.commit()
    db.refresh(submission)
    
    return submission


@router.get("/submissions", response_model=List[CodeSubmissionResponse])
def get_my_submissions(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    submissions = db.query(CodeSubmission).filter(
        CodeSubmission.user_id == current_user.id
    ).order_by(CodeSubmission.created_at.desc()).offset(skip).limit(limit).all()
    
    return submissions


@router.get("/progress/summary", response_model=ProgressSummary)
def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_lessons = db.query(Lesson).filter(Lesson.is_published == True).count()
    completed_lessons = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.is_completed == True
    ).count()
    
    completion_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "completion_percentage": round(completion_percentage, 2),
        "total_xp": current_user.total_xp,
        "current_streak": current_user.current_streak,
        "longest_streak": current_user.longest_streak
    }


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_lessons = db.query(Lesson).filter(Lesson.is_published == True).count()
    completed_lessons = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.is_completed == True
    ).count()
    
    completion_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    total_submissions = db.query(CodeSubmission).filter(
        CodeSubmission.user_id == current_user.id
    ).count()
    
    achievements_count = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id
    ).count()  # Placeholder
    
    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "completion_percentage": round(completion_percentage, 2),
        "total_xp": current_user.total_xp,
        "current_streak": current_user.current_streak,
        "longest_streak": current_user.longest_streak,
        "total_submissions": total_submissions,
        "achievements_count": achievements_count,
        "recent_activity": []
    }
