from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.schemas import ModuleResponse, ModuleCreate
from app.services.services import ModuleService
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.models.models import User

router = APIRouter(prefix="/modules", tags=["Modules"])


@router.get("/", response_model=List[ModuleResponse])
def get_all_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all modules."""
    return ModuleService.get_all_modules(db)


@router.get("/{module_id}", response_model=ModuleResponse)
def get_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get module by ID."""
    module = ModuleService.get_module_by_id(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    return module


@router.post("/", response_model=ModuleResponse)
def create_module(
    module_data: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Create new module (admin only)."""
    module = Module(**module_data.dict())
    db.add(module)
    db.commit()
    db.refresh(module)
    return module
