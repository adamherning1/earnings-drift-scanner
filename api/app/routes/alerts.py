from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..services.auth import get_current_user
from ..models import User, Alert

router = APIRouter()

@router.get("/")
async def get_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's alerts"""
    alerts = db.query(Alert).filter(Alert.user_id == current_user.id).all()
    return {"alerts": alerts}

@router.post("/create")
async def create_alert(
    symbol: str,
    alert_type: str,
    threshold: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new alert"""
    alert = Alert(
        user_id=current_user.id,
        symbol=symbol.upper(),
        alert_type=alert_type,
        threshold=threshold
    )
    db.add(alert)
    db.commit()
    return {"message": "Alert created", "alert_id": alert.id}