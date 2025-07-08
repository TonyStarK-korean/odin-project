"""
백테스팅 API
백테스트 실행 및 결과 조회 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio
import uuid

from backend.app.core.database import get_db
from backend.app.models.trade_models import (
    BacktestJob, BacktestRequest, BacktestJobResponse
)
from backend.app.core.strategy_base import StrategyFactory
from backend.app.core.market_analysis import market_analyzer

router = APIRouter()

# 백테스트 작업 상태 관리 (실제 운영에서는 Redis 등 사용 권장)
backtest_jobs = {}

async def run_backtest(job_id: str, request: BacktestRequest):
    """
    백테스트 실행 (백그라운드 작업)
    
    Args:
        job_id: 작업 ID
        request: 백테스트 요청
    """
    try:
        # 작업 상태를 RUNNING으로 업데이트
        backtest_jobs[job_id]["status"] = "RUNNING"
        
        # 전략 가져오기
        strategy = StrategyFactory.get_strategy(request.strategy_id)
        
        # 백테스트 실행 (간단한 시뮬레이션)
        results = await simulate_backtest(strategy, request)
        
        # 결과 저장
        backtest_jobs[job_id]["status"] = "COMPLETED"
        backtest_jobs[job_id]["results"] = results
        
        print(f"백테스트 완료: {job_id}")
        
    except Exception as e:
        backtest_jobs[job_id]["status"] = "FAILED"
        backtest_jobs[job_id]["error"] = str(e)
        print(f"백테스트 실패: {job_id} - {e}")

async def simulate_backtest(strategy, request: BacktestRequest) -> Dict[str, Any]:
    """
    백테스트 시뮬레이션 (실제 구현에서는 더 복잡한 로직 필요)
    
    Args:
        strategy: 매매 전략
        request: 백테스트 요청
        
    Returns:
        Dict: 백테스트 결과
    """
    # 볼린저 밴드 돌파 전략인 경우 실제 OHLCV 데이터로 백테스트
    if request.strategy_id == "bollinger_breakout_v1":
        return await run_bollinger_breakout_backtest(strategy, request)
    
    # 기존 랜덤 시뮬레이션 (다른 전략들)
    import random
    
    # 시뮬레이션 기간 계산
    days = (request.end_date - request.start_date).days
    trades = []
    current_capital = request.initial_capital
    equity_curve = []
    
    # 일별 시뮬레이션
    for day in range(days):
        # 랜덤 거래 시뮬레이션
        if random.random() < 0.3:  # 30% 확률로 거래 발생
            trade = {
                "date": request.start_date + timedelta(days=day),
                "symbol": f"COIN{random.randint(1, 10)}/USDT",
                "action": random.choice(["BUY", "SELL"]),
                "direction": random.choice(["LONG", "SHORT"]),
                "price": random.uniform(100, 1000),
                "size": random.uniform(0.1, 1.0),
                "pnl": random.uniform(-50, 100)
            }
            trades.append(trade)
            current_capital += trade["pnl"]
        
        equity_curve.append({
            "date": request.start_date + timedelta(days=day),
            "equity": current_capital
        })
    
    # 성과 계산
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t["pnl"] > 0])
    total_pnl = sum(t["pnl"] for t in trades)
    final_capital = request.initial_capital + total_pnl
    total_return = ((final_capital - request.initial_capital) / request.initial_capital) * 100
    
    # MDD 계산 (간단한 버전)
    max_equity = max(e["equity"] for e in equity_curve)
    min_equity = min(e["equity"] for e in equity_curve)
    mdd = ((max_equity - min_equity) / max_equity) * 100 if max_equity > 0 else 0
    
    return {
        "summary": {
            "initial_capital": request.initial_capital,
            "final_capital": final_capital,
            "total_return": round(total_return, 2),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": round((winning_trades / total_trades * 100), 2) if total_trades > 0 else 0,
            "total_pnl": round(total_pnl, 2),
            "max_drawdown": round(mdd, 2)
        },
        "trades": trades,
        "equity_curve": equity_curve,
        "statistics": {
            "sharpe_ratio": round(random.uniform(0.5, 2.0), 2),  # 랜덤 샤프 비율
            "profit_factor": round(random.uniform(1.0, 3.0), 2),  # 랜덤 수익 팩터
            "avg_win": round(sum(t["pnl"] for t in trades if t["pnl"] > 0) / winning_trades, 2) if winning_trades > 0 else 0,
            "avg_loss": round(sum(t["pnl"] for t in trades if t["pnl"] < 0) / (total_trades - winning_trades), 2) if (total_trades - winning_trades) > 0 else 0
        }
    }

async def run_bollinger_breakout_backtest(strategy, request: BacktestRequest) -> Dict[str, Any]:
    """
    볼린저 밴드 돌파 전략 백테스트
    
    Args:
        strategy: 볼린저 밴드 돌파 전략
        request: 백테스트 요청
        
    Returns:
        Dict: 백테스트 결과
    """
    import pandas as pd
    import numpy as np
    from datetime import timedelta
    
    # 테스트용 OHLCV 데이터 생성 (실제로는 거래소 API에서 가져와야 함)
    ohlcv_data = generate_test_ohlcv_data(request.start_date, request.end_date)
    
    trades = []
    current_capital = request.initial_capital
    equity_curve = []
    position = None
    
    # 1시간봉 기준으로 백테스트 실행
    for i in range(80, len(ohlcv_data)):  # 80개 데이터 이후부터 시작 (볼린저 밴드 계산을 위해)
        current_data = ohlcv_data.iloc[:i+1]
        current_candle = current_data.iloc[-1]
        current_date = current_candle.name
        
        # 포지션이 없고 매수 신호가 있는 경우
        if position is None and strategy.check_entry_signal(current_data):
            # 진입 가격 결정
            entry_price = strategy.get_entry_price(current_data)
            position_size_ratio = strategy.get_position_size_ratio()
            position_size = current_capital * position_size_ratio
            
            # 포지션 생성
            position = {
                "entry_date": current_date,
                "entry_price": entry_price,
                "size": position_size,
                "direction": "LONG",
                "highest_price": entry_price  # 최고가 추적을 위한 초기값
            }
            
            # 거래 기록
            trade = {
                "date": current_date,
                "symbol": "BTC/USDT",
                "action": "BUY",
                "direction": "LONG",
                "price": entry_price,
                "size": position_size,
                "pnl": 0,
                "strategy_signal": "볼린저 밴드 돌파 매수",
                "stop_loss": entry_price * 0.97,
                "max_profit_target": entry_price * 3.00
            }
            trades.append(trade)
        
        # 포지션이 있는 경우 청산 조건 확인
        elif position is not None:
            current_price = current_candle['close']
            entry_price = position["entry_price"]
            position_size = position["size"]
            
            # 손익 계산
            pnl = (current_price - entry_price) * position_size / entry_price
            
            # 트레일링 스탑 설정 가져오기
            stop_info = strategy.set_trailing_stop(entry_price)
            stop_loss = stop_info['stop_loss']
            max_profit_target = stop_info['max_profit_target']
            
            # 트레일링 스탑 업데이트 (최고가 추적)
            if 'highest_price' not in position:
                position['highest_price'] = current_price
            else:
                position['highest_price'] = max(position['highest_price'], current_price)
            
            # 트레일링 스탑 계산 (최고가 대비 1.5% 하락 시 청산)
            # 이는 수익을 보호하면서 최대 50%까지 익절할 수 있게 해줍니다
            trailing_stop = position['highest_price'] * 0.985
            
            should_close = False
            close_reason = ""
            
            if current_price <= stop_loss:
                should_close = True
                close_reason = "손절"
            elif current_price >= max_profit_target:
                should_close = True
                close_reason = "최대 익절 (200%)"
            elif current_price <= trailing_stop and position['highest_price'] > entry_price * 1.02:
                # 최고가가 진입가보다 2% 이상 높을 때만 트레일링 스탑 작동
                should_close = True
                close_reason = "트레일링 스탑"
            
            # 청산
            if should_close:
                # 거래 기록 업데이트
                trades[-1]["pnl"] = pnl
                trades[-1]["close_date"] = current_date
                trades[-1]["close_price"] = current_price
                trades[-1]["close_reason"] = close_reason
                trades[-1]["highest_price_reached"] = position['highest_price']
                trades[-1]["max_profit_percentage"] = ((position['highest_price'] - entry_price) / entry_price) * 100
                
                # 자본 업데이트
                current_capital += pnl
                
                # 포지션 초기화
                position = None
        
        # 자본 곡선 업데이트
        equity_curve.append({
            "date": current_date,
            "equity": current_capital
        })
    
    # 마지막 포지션이 있다면 청산
    if position is not None:
        last_candle = ohlcv_data.iloc[-1]
        current_price = last_candle['close']
        entry_price = position["entry_price"]
        position_size = position["size"]
        pnl = (current_price - entry_price) * position_size / entry_price
        
        trades[-1]["pnl"] = pnl
        trades[-1]["close_date"] = last_candle.name
        trades[-1]["close_price"] = current_price
        trades[-1]["close_reason"] = "백테스트 종료"
        trades[-1]["highest_price_reached"] = position['highest_price']
        trades[-1]["max_profit_percentage"] = ((position['highest_price'] - entry_price) / entry_price) * 100
        
        current_capital += pnl
        equity_curve[-1]["equity"] = current_capital
    
    # 성과 계산
    total_trades = len([t for t in trades if t.get("close_date")])
    winning_trades = len([t for t in trades if t.get("pnl", 0) > 0])
    total_pnl = sum(t.get("pnl", 0) for t in trades)
    final_capital = request.initial_capital + total_pnl
    total_return = ((final_capital - request.initial_capital) / request.initial_capital) * 100
    
    # MDD 계산
    equities = [e["equity"] for e in equity_curve]
    max_equity = max(equities)
    min_equity = min(equities)
    mdd = ((max_equity - min_equity) / max_equity) * 100 if max_equity > 0 else 0
    
    # 샤프 비율 계산 (간단한 버전)
    returns = []
    for i in range(1, len(equity_curve)):
        prev_equity = equity_curve[i-1]["equity"]
        curr_equity = equity_curve[i]["equity"]
        if prev_equity > 0:
            returns.append((curr_equity - prev_equity) / prev_equity)
    
    sharpe_ratio = 0
    if returns:
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        if std_return > 0:
            sharpe_ratio = avg_return / std_return * np.sqrt(24)  # 1시간봉 기준
    
    return {
        "summary": {
            "initial_capital": request.initial_capital,
            "final_capital": round(final_capital, 2),
            "total_return": round(total_return, 2),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": round((winning_trades / total_trades * 100), 2) if total_trades > 0 else 0,
            "total_pnl": round(total_pnl, 2),
            "max_drawdown": round(mdd, 2)
        },
        "trades": trades,
        "equity_curve": equity_curve,
        "statistics": {
            "sharpe_ratio": round(sharpe_ratio, 2),
            "profit_factor": round(sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) > 0) / abs(sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) < 0)), 2) if sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) < 0) != 0 else 0,
            "avg_win": round(sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) > 0) / winning_trades, 2) if winning_trades > 0 else 0,
            "avg_loss": round(sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) < 0) / (total_trades - winning_trades), 2) if (total_trades - winning_trades) > 0 else 0
        }
    }

def generate_test_ohlcv_data(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    테스트용 OHLCV 데이터 생성
    
    Args:
        start_date: 시작일
        end_date: 종료일
        
    Returns:
        pd.DataFrame: OHLCV 데이터
    """
    import pandas as pd
    import numpy as np
    
    # 1시간봉 기준으로 데이터 생성
    date_range = pd.date_range(start=start_date, end=end_date, freq='1H')
    
    # 기본 가격 시뮬레이션 (트렌드 + 노이즈)
    base_price = 50000  # BTC 기준 가격
    trend = np.linspace(0, 0.2, len(date_range))  # 20% 상승 트렌드
    noise = np.random.normal(0, 0.02, len(date_range))  # 2% 표준편차 노이즈
    
    prices = base_price * (1 + trend + noise)
    
    # OHLCV 데이터 생성
    ohlcv_data = []
    
    for i, (date, price) in enumerate(zip(date_range, prices)):
        # 변동성 추가
        volatility = 0.01  # 1% 변동성
        
        # OHLC 생성
        open_price = price * (1 + np.random.normal(0, volatility))
        high_price = max(open_price, price) * (1 + abs(np.random.normal(0, volatility)))
        low_price = min(open_price, price) * (1 - abs(np.random.normal(0, volatility)))
        close_price = price * (1 + np.random.normal(0, volatility))
        
        # 볼륨 생성
        volume = np.random.uniform(100, 1000)
        
        ohlcv_data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    df = pd.DataFrame(ohlcv_data, index=date_range)
    return df

@router.post("/backtest")
async def create_backtest(
    request: BacktestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    백테스트 실행 요청
    
    Args:
        request: 백테스트 요청
        background_tasks: 백그라운드 작업
        
    Returns:
        Dict: 백테스트 작업 정보
    """
    try:
        # 전략 유효성 검사
        try:
            strategy = StrategyFactory.get_strategy(request.strategy_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"유효하지 않은 전략: {str(e)}")
        
        # 날짜 유효성 검사
        if request.start_date >= request.end_date:
            raise HTTPException(status_code=400, detail="시작일은 종료일보다 이전이어야 합니다.")
        
        # 작업 ID 생성
        job_id = str(uuid.uuid4())
        
        # 데이터베이스에 작업 저장
        backtest_job = BacktestJob(
            strategy_id=request.strategy_id,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            timeframe=request.timeframe,
            status="PENDING"
        )
        db.add(backtest_job)
        db.commit()
        
        # 메모리에 작업 정보 저장
        backtest_jobs[job_id] = {
            "job_id": job_id,
            "strategy_id": request.strategy_id,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "initial_capital": request.initial_capital,
            "timeframe": request.timeframe,
            "status": "PENDING",
            "created_at": datetime.now(),
            "results": None,
            "error": None
        }
        
        # 백그라운드에서 백테스트 실행
        background_tasks.add_task(run_backtest, job_id, request)
        
        return {
            "message": "백테스트가 시작되었습니다.",
            "job_id": job_id,
            "strategy_id": request.strategy_id,
            "strategy_name": strategy.name,
            "status": "PENDING",
            "created_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"백테스트 생성 실패: {str(e)}")

@router.get("/history")
async def get_backtest_history(
    limit: int = 20,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    백테스트 히스토리 조회
    
    Args:
        limit: 조회할 작업 수 (기본값: 20)
        
    Returns:
        Dict: 백테스트 히스토리
    """
    try:
        backtest_jobs_db = db.query(BacktestJob).order_by(
            BacktestJob.created_at.desc()
        ).limit(limit).all()
        
        history = []
        for job in backtest_jobs_db:
            # 메모리에서 최신 상태 확인
            memory_job = next((j for j in backtest_jobs.values() if j["job_id"] == str(job.job_id)), None)
            
            status = memory_job["status"] if memory_job else job.status
            
            history.append({
                "job_id": job.job_id,
                "created_at": job.created_at,
                "strategy_id": job.strategy_id,
                "start_date": job.start_date,
                "end_date": job.end_date,
                "initial_capital": job.initial_capital,
                "timeframe": job.timeframe,
                "status": status,
                "results_summary": job.results.get("summary") if job.results else None
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "count": len(history),
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 조회 실패: {str(e)}")

@router.get("/result/{job_id}")
async def get_backtest_result(job_id: str) -> Dict[str, Any]:
    """
    특정 백테스트 결과 조회
    
    Args:
        job_id: 작업 ID
        
    Returns:
        Dict: 백테스트 결과
    """
    try:
        if job_id not in backtest_jobs:
            raise HTTPException(status_code=404, detail="백테스트 작업을 찾을 수 없습니다.")
        
        job = backtest_jobs[job_id]
        
        if job["status"] == "PENDING":
            return {
                "job_id": job_id,
                "status": "PENDING",
                "message": "백테스트가 진행 중입니다.",
                "created_at": job["created_at"].isoformat()
            }
        elif job["status"] == "RUNNING":
            return {
                "job_id": job_id,
                "status": "RUNNING",
                "message": "백테스트가 실행 중입니다.",
                "created_at": job["created_at"].isoformat()
            }
        elif job["status"] == "FAILED":
            return {
                "job_id": job_id,
                "status": "FAILED",
                "error": job.get("error", "알 수 없는 오류"),
                "created_at": job["created_at"].isoformat()
            }
        else:  # COMPLETED
            return {
                "job_id": job_id,
                "status": "COMPLETED",
                "created_at": job["created_at"].isoformat(),
                "strategy_id": job["strategy_id"],
                "start_date": job["start_date"].isoformat(),
                "end_date": job["end_date"].isoformat(),
                "initial_capital": job["initial_capital"],
                "timeframe": job["timeframe"],
                "results": job["results"]
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결과 조회 실패: {str(e)}")

@router.get("/strategies")
async def get_available_strategies() -> Dict[str, Any]:
    """
    사용 가능한 전략 목록 조회
    
    Returns:
        Dict: 전략 목록
    """
    try:
        strategies = StrategyFactory.get_available_strategies()
        
        strategy_details = []
        for strategy_id, strategy_name in strategies.items():
            strategy = StrategyFactory.get_strategy(strategy_id)
            strategy_details.append({
                "strategy_id": strategy_id,
                "name": strategy_name,
                "description": strategy.description,
                "parameters": strategy.parameters
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "count": len(strategy_details),
            "strategies": strategy_details
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전략 목록 조회 실패: {str(e)}")

@router.delete("/job/{job_id}")
async def delete_backtest_job(job_id: str) -> Dict[str, Any]:
    """
    백테스트 작업 삭제
    
    Args:
        job_id: 작업 ID
        
    Returns:
        Dict: 삭제 결과
    """
    try:
        if job_id not in backtest_jobs:
            raise HTTPException(status_code=404, detail="백테스트 작업을 찾을 수 없습니다.")
        
        # 메모리에서 삭제
        del backtest_jobs[job_id]
        
        return {
            "message": "백테스트 작업이 삭제되었습니다.",
            "job_id": job_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 삭제 실패: {str(e)}") 