from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import anthropic

from ..database import get_db
from ..services.auth import get_current_user
from ..models import User, EarningsEvent, AIPlaybook
from ..config import settings

router = APIRouter()

@router.get("/{symbol}")
async def get_playbook(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated playbook for symbol"""
    if current_user.subscription_tier == "free":
        raise HTTPException(status_code=403, detail="Subscription required for AI playbooks")
    
    symbol = symbol.upper()
    
    # Get latest earnings event
    latest_event = db.query(EarningsEvent).filter(
        EarningsEvent.symbol == symbol
    ).order_by(EarningsEvent.earnings_date.desc()).first()
    
    if not latest_event:
        raise HTTPException(status_code=404, detail="No earnings data found")
    
    # Check if playbook already exists
    existing = db.query(AIPlaybook).filter(
        AIPlaybook.earnings_event_id == latest_event.id
    ).first()
    
    if existing:
        return {
            "symbol": symbol,
            "playbook": {
                "strategy_summary": existing.strategy_summary,
                "entry_rules": existing.entry_rules,
                "exit_rules": existing.exit_rules,
                "position_sizing": existing.position_sizing,
                "risk_warnings": existing.risk_warnings
            }
        }
    
    # Generate new playbook
    # TODO: Implement Claude integration
    return {
        "symbol": symbol,
        "playbook": {
            "strategy_summary": "AI playbook generation pending Claude API integration",
            "entry_rules": "Coming soon",
            "exit_rules": "Coming soon",
            "position_sizing": "Coming soon",
            "risk_warnings": "Coming soon"
        }
    }