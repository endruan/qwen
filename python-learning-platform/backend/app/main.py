from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db.session import engine, get_db
from app.models.user import Base
from app.api import auth, lessons, code, users


# Create tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Python Learning Platform API",
    description="API for interactive Python learning platform",
    version="1.0.0"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(lessons.router, prefix="/api/v1", tags=["Lessons"])
app.include_router(code.router, prefix="/api/v1/code", tags=["Code Execution"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])


@app.get("/")
def root():
    return {
        "message": "Welcome to Python Learning Platform API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
