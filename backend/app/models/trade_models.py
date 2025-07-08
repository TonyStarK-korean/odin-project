"""
거래 관련 데이터베이스 모델
PostgreSQL에 저장되는 거래 로그 및 백테스트 결과 모델
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from backend.app.core.database import Base
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# SQLAlchemy 모델
class TradeLog(Base):
    """거래 로그 테이블"""
    __tablename__ = "trade_logs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    strategy_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)  # BUY, SELL, CLOSE
    direction = Column(String(10), nullable=False)  # LONG, SHORT
    price = Column(Float, nullable=False)
    size = Column(Float, nullable=False)
    pnl = Column(Float, default=0.0)
    is_backtest = Column(Boolean, default=False)
    trade_metadata = Column(JSON, nullable=True)  # 추가 거래 정보

class BacktestJob(Base):
    """백테스트 작업 테이블"""
    __tablename__ = "backtest_jobs"
    
    job_id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    strategy_id = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    timeframe = Column(String(10), nullable=False)
    status = Column(String(20), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    results = Column(JSON, nullable=True)  # 백테스트 결과 데이터

class LiveTradingStatus(Base):
    """실시간 매매 상태 테이블"""
    __tablename__ = "live_trading_status"
    
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=False)
    strategy_id = Column(String(100), nullable=True)
    risk_per_trade = Column(Float, default=0.05)
    total_pnl = Column(Float, default=0.0)
    daily_pnl = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Pydantic 모델 (API 요청/응답용)
class TradeLogCreate(BaseModel):
    strategy_id: str
    symbol: str
    action: str
    direction: str
    price: float
    size: float
    pnl: float = 0.0
    is_backtest: bool = False
    trade_metadata: Optional[Dict[str, Any]] = None

class TradeLogResponse(BaseModel):
    log_id: int
    timestamp: datetime
    strategy_id: str
    symbol: str
    action: str
    direction: str
    price: float
    size: float
    pnl: float
    is_backtest: bool
    trade_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class BacktestRequest(BaseModel):
    strategy_id: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    timeframe: str = "1h"

class BacktestJobResponse(BaseModel):
    job_id: int
    created_at: datetime
    strategy_id: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    timeframe: str
    status: str
    results: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class LiveTradingRequest(BaseModel):
    strategy_id: str
    risk_per_trade: float = 0.05

class LiveTradingStatusResponse(BaseModel):
    is_active: bool
    strategy_id: Optional[str] = None
    risk_per_trade: float
    total_pnl: float
    daily_pnl: float
    last_updated: datetime

    class Config:
        from_attributes = True 