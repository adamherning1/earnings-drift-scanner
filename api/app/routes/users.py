from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.auth import get_current_user
from ..models import User

router = APIRouter()

@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Get user profile"""
    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "subscription_tier": current_user.subscription_tier,
        "subscription_status": current_user.subscription_status,
        "searches_remaining": {
            "starter": 10,
            "professional": 50,
            "institution": 999999
        }.get(current_user.subscription_tier, 0) - current_user.searches_this_month
    }

@router.post("/subscription/upgrade")
async def upgrade_subscription(
    tier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade subscription tier"""
    # TODO: Integrate with Stripe
    return {"message": "Subscription upgrade endpoint - Stripe integration pending"}