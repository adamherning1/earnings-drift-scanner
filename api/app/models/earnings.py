from sqlalchemy import Column, Integer, String, DateTime, Float, Date, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class EarningsEvent(Base):
    __tablename__ = "earnings_events"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    earnings_date = Column(Date, nullable=False, index=True)
    reported_time = Column(String(10))  # BMO (Before Market Open) or AMC (After Market Close)
    
    # Actual results
    eps_actual = Column(Float)
    eps_estimate = Column(Float)
    eps_surprise = Column(Float)
    eps_surprise_pct = Column(Float)
    
    revenue_actual = Column(Float)
    revenue_estimate = Column(Float)
    revenue_surprise = Column(Float)
    revenue_surprise_pct = Column(Float)
    
    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    drift_patterns = relationship("DriftPattern", back_populates="earnings_event")
    
    # Composite index for efficient queries
    __table_args__ = (
        Index("idx_symbol_date", "symbol", "earnings_date"),
    )

class DriftPattern(Base):
    __tablename__ = "drift_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    earnings_event_id = Column(Integer, ForeignKey("earnings_events.id"))
    
    # Price data
    days_before = Column(Integer, nullable=False)  # -5 to 0 (0 = earnings day)
    open_price = Column(Float)
    close_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    volume = Column(Integer)
    
    # Calculated metrics
    daily_return = Column(Float)
    cumulative_return = Column(Float)
    relative_to_spy = Column(Float)  # Alpha vs SPY
    
    # Technical indicators
    rsi = Column(Float)
    volume_ratio = Column(Float)  # vs 20-day average
    
    # Relationships
    earnings_event = relationship("EarningsEvent", back_populates="drift_patterns")
    
    __table_args__ = (
        Index("idx_event_days", "earnings_event_id", "days_before"),
    )

class AIPlaybook(Base):
    __tablename__ = "ai_playbooks"
    
    id = Column(Integer, primary_key=True, index=True)
    earnings_event_id = Column(Integer, ForeignKey("earnings_events.id"))
    
    # Playbook content
    strategy_summary = Column(Text)
    entry_rules = Column(Text)
    exit_rules = Column(Text)
    position_sizing = Column(Text)
    risk_warnings = Column(Text)
    
    # Performance if backtested
    historical_win_rate = Column(Float)
    average_return = Column(Float)
    max_drawdown = Column(Float)
    
    # Meta
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    model_version = Column(String(50))
    
    # Relationships
    earnings_event = relationship("EarningsEvent")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    # Subscription info
    stripe_customer_id = Column(String(255), unique=True)
    subscription_tier = Column(String(50), default="free")  # free, starter, professional, institution
    subscription_status = Column(String(50), default="inactive")
    subscription_end_date = Column(DateTime(timezone=True))
    
    # Usage tracking
    searches_this_month = Column(Integer, default=0)
    last_search_at = Column(DateTime(timezone=True))
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    alerts = relationship("Alert", back_populates="user")
    searches = relationship("SearchHistory", back_populates="user")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String(10), nullable=False)
    
    # Alert conditions
    alert_type = Column(String(50))  # drift_detected, earnings_approaching, pattern_match
    threshold = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="alerts")

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String(10), nullable=False)
    searched_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="searches")