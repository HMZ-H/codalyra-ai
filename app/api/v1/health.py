from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    return {"status": "healthy", "version": "0.1.0"}


@router.get("/health/db")
def health_check_db(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}
