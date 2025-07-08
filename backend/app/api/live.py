"""
실시간 매매 API
실시간 매매 상태 관리 및 제어 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.trade_models import (
    LiveTradingStatus, LiveTradingRequest, LiveTradingStatusResponse,
    TradeLog, TradeLogCreate, TradeLogResponse
)
from app.core.strategy_base import StrategyFactory

router = APIRouter()

# 전역 변수로 실시간 매매 상태 관리 (실제 운영에서는 Redis 등 사용 권장)
live_trading_state = {
    "is_active": False,
    "strategy_id": None,
    "risk_per_trade": 0.05,
    "total_pnl": 0.0,
    "daily_pnl": 0.0,
    "last_updated": datetime.now(),
    "current_positions": [],
    "start_time": None
}

@router.get("/status")
async def get_live_status(db: Session = Depends(get_db)) -> LiveTradingStatusResponse:
    """
    실시간 매매 상태 조회
    
    Returns:
        LiveTradingStatusResponse: 현재 매매 상태
    """
    try:
        # 데이터베이스에서 상태 조회 (없으면 기본값 사용)
        db_status = db.query(LiveTradingStatus).first()
        
        if db_status:
            return LiveTradingStatusResponse(
                is_active=db_status.is_active,
                strategy_id=db_status.strategy_id,
                risk_per_trade=db_status.risk_per_trade,
                total_pnl=db_status.total_pnl,
                daily_pnl=db_status.daily_pnl,
                last_updated=db_status.last_updated
            )
        else:
            return LiveTradingStatusResponse(
                is_active=False,
                strategy_id=None,
                risk_per_trade=0.05,
                total_pnl=0.0,
                daily_pnl=0.0,
                last_updated=datetime.now()
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")

@router.post("/start")
async def start_live_trading(
    request: LiveTradingRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    실시간 매매 시작
    
    Args:
        request: 매매 시작 요청
        
    Returns:
        Dict: 시작 결과
    """
    try:
        # 전략 유효성 검사
        try:
            strategy = StrategyFactory.get_strategy(request.strategy_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"유효하지 않은 전략: {str(e)}")
        
        # 현재 상태 확인
        current_status = db.query(LiveTradingStatus).first()
        
        if current_status and current_status.is_active:
            raise HTTPException(status_code=400, detail="이미 매매가 실행 중입니다.")
        
        # 매매 상태 업데이트
        if current_status:
            current_status.is_active = True
            current_status.strategy_id = request.strategy_id
            current_status.risk_per_trade = request.risk_per_trade
            current_status.last_updated = datetime.now()
        else:
            new_status = LiveTradingStatus(
                is_active=True,
                strategy_id=request.strategy_id,
                risk_per_trade=request.risk_per_trade,
                total_pnl=0.0,
                daily_pnl=0.0
            )
            db.add(new_status)
        
        db.commit()
        
        # 전역 상태 업데이트
        live_trading_state.update({
            "is_active": True,
            "strategy_id": request.strategy_id,
            "risk_per_trade": request.risk_per_trade,
            "start_time": datetime.now()
        })
        
        return {
            "message": "실시간 매매가 시작되었습니다.",
            "strategy_id": request.strategy_id,
            "strategy_name": strategy.name,
            "risk_per_trade": request.risk_per_trade,
            "start_time": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매매 시작 실패: {str(e)}")

@router.post("/stop")
async def stop_live_trading(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    실시간 매매 중단
    
    Returns:
        Dict: 중단 결과
    """
    try:
        # 현재 상태 확인
        current_status = db.query(LiveTradingStatus).first()
        
        if not current_status or not current_status.is_active:
            raise HTTPException(status_code=400, detail="실행 중인 매매가 없습니다.")
        
        # 매매 상태 업데이트
        current_status.is_active = False
        current_status.last_updated = datetime.now()
        db.commit()
        
        # 전역 상태 업데이트
        live_trading_state.update({
            "is_active": False,
            "strategy_id": None,
            "start_time": None
        })
        
        return {
            "message": "실시간 매매가 중단되었습니다.",
            "stop_time": datetime.now().isoformat(),
            "total_pnl": current_status.total_pnl,
            "daily_pnl": current_status.daily_pnl
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매매 중단 실패: {str(e)}")

@router.get("/positions")
async def get_current_positions(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    현재 보유 포지션 조회
    
    Returns:
        Dict: 현재 포지션 목록
    """
    try:
        # 최근 거래 로그에서 현재 포지션 추정
        # 실제 운영에서는 별도 포지션 테이블 사용 권장
        recent_trades = db.query(TradeLog).filter(
            TradeLog.is_backtest == False
        ).order_by(TradeLog.timestamp.desc()).limit(50).all()
        
        # 포지션 분석 (간단한 예시)
        positions = []
        position_map = {}
        
        for trade in recent_trades:
            symbol = trade.symbol
            if symbol not in position_map:
                position_map[symbol] = {
                    "symbol": symbol,
                    "direction": trade.direction,
                    "entry_price": trade.price,
                    "size": trade.size,
                    "pnl": 0.0,
                    "last_trade": trade.timestamp
                }
            else:
                # 포지션 업데이트 (실제로는 더 복잡한 로직 필요)
                if trade.action == "CLOSE":
                    position_map[symbol]["pnl"] = trade.pnl
                else:
                    position_map[symbol]["size"] += trade.size
                    position_map[symbol]["last_trade"] = trade.timestamp
        
        # 활성 포지션만 필터링
        for symbol, pos in position_map.items():
            if pos["size"] > 0:
                positions.append(pos)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_positions": len(positions),
            "positions": positions,
            "total_pnl": sum(pos["pnl"] for pos in positions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포지션 조회 실패: {str(e)}")

@router.get("/trades/recent")
async def get_recent_trades(
    limit: int = 20,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    최근 거래 내역 조회
    
    Args:
        limit: 조회할 거래 수 (기본값: 20)
        
    Returns:
        Dict: 최근 거래 내역
    """
    try:
        recent_trades = db.query(TradeLog).filter(
            TradeLog.is_backtest == False
        ).order_by(TradeLog.timestamp.desc()).limit(limit).all()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "count": len(recent_trades),
            "trades": [
                TradeLogResponse(
                    log_id=trade.log_id,
                    timestamp=trade.timestamp,
                    strategy_id=trade.strategy_id,
                    symbol=trade.symbol,
                    action=trade.action,
                    direction=trade.direction,
                    price=trade.price,
                    size=trade.size,
                    pnl=trade.pnl,
                    is_backtest=trade.is_backtest,
                    metadata=trade.metadata
                ).dict()
                for trade in recent_trades
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"거래 내역 조회 실패: {str(e)}")

@router.get("/performance")
async def get_trading_performance(
    days: int = 7,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    매매 성과 분석
    
    Args:
        days: 분석 기간 (일)
        
    Returns:
        Dict: 성과 분석 결과
    """
    try:
        # 지정 기간의 거래 내역 조회
        start_date = datetime.now() - timedelta(days=days)
        trades = db.query(TradeLog).filter(
            TradeLog.is_backtest == False,
            TradeLog.timestamp >= start_date
        ).order_by(TradeLog.timestamp).all()
        
        # 성과 계산
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        losing_trades = len([t for t in trades if t.pnl < 0])
        
        total_pnl = sum(t.pnl for t in trades)
        winning_pnl = sum(t.pnl for t in trades if t.pnl > 0)
        losing_pnl = sum(t.pnl for t in trades if t.pnl < 0)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_win = winning_pnl / winning_trades if winning_trades > 0 else 0
        avg_loss = losing_pnl / losing_trades if losing_trades > 0 else 0
        
        return {
            "period": f"{days}일",
            "summary": {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": round(win_rate, 2),
                "total_pnl": round(total_pnl, 2),
                "winning_pnl": round(winning_pnl, 2),
                "losing_pnl": round(losing_pnl, 2)
            },
            "statistics": {
                "average_win": round(avg_win, 2),
                "average_loss": round(avg_loss, 2),
                "profit_factor": round(abs(winning_pnl / losing_pnl), 2) if losing_pnl != 0 else float('inf'),
                "max_win": max([t.pnl for t in trades], default=0),
                "max_loss": min([t.pnl for t in trades], default=0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성과 분석 실패: {str(e)}") 