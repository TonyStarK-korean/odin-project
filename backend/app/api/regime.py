"""
시장 국면 분석 API
현재 시장 국면을 분석하고 반환하는 엔드포인트
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import pandas as pd
from datetime import datetime

from backend.app.core.market_analysis import market_analyzer

router = APIRouter()

@router.get("/regime")
async def get_market_regime() -> Dict[str, Any]:
    """
    현재 시장 국면 분석
    
    Returns:
        Dict: 시장 국면 정보
    """
    try:
        # 비트코인 OHLCV 데이터 조회
        btc_df = await market_analyzer.get_btc_ohlcv(timeframe='1h', limit=200)
        
        # 시장 국면 분석
        regime = market_analyzer.analyze_market_regime(btc_df)
        
        # 추가 분석 정보
        current_price = btc_df['close'].iloc[-1]
        sma20 = btc_df['close'].rolling(window=20).mean().iloc[-1]
        sma60 = btc_df['close'].rolling(window=60).mean().iloc[-1]
        sma120 = btc_df['close'].rolling(window=120).mean().iloc[-1]
        
        # 24시간 변화율 계산
        price_24h_ago = btc_df['close'].iloc[-24] if len(btc_df) >= 24 else btc_df['close'].iloc[0]
        change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
        
        return {
            "regime": regime,
            "timestamp": datetime.now().isoformat(),
            "btc_price": current_price,
            "sma20": sma20,
            "sma60": sma60,
            "sma120": sma120,
            "change_24h": round(change_24h, 2),
            "analysis": {
                "current_price_vs_sma20": "above" if current_price > sma20 else "below",
                "sma20_vs_sma60": "above" if sma20 > sma60 else "below",
                "sma60_vs_sma120": "above" if sma60 > sma120 else "below"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시장 분석 실패: {str(e)}")

@router.get("/regime/history")
async def get_regime_history(days: int = 7) -> Dict[str, Any]:
    """
    과거 시장 국면 히스토리 조회
    
    Args:
        days: 조회할 일수 (기본값: 7일)
        
    Returns:
        Dict: 과거 시장 국면 데이터
    """
    try:
        # 더 많은 데이터 조회 (일별 데이터)
        limit = days * 24  # 시간별 데이터
        btc_df = await market_analyzer.get_btc_ohlcv(timeframe='1h', limit=limit)
        
        # 이동평균 계산
        btc_df['SMA20'] = btc_df['close'].rolling(window=20).mean()
        btc_df['SMA60'] = btc_df['close'].rolling(window=60).mean()
        btc_df['SMA120'] = btc_df['close'].rolling(window=120).mean()
        
        # 각 시점별 시장 국면 분석
        regime_history = []
        for i in range(120, len(btc_df)):  # 120개 캔들 이후부터 분석 가능
            current_price = btc_df['close'].iloc[i]
            sma20 = btc_df['SMA20'].iloc[i]
            sma60 = btc_df['SMA60'].iloc[i]
            sma120 = btc_df['SMA120'].iloc[i]
            
            if current_price > sma20 > sma60 > sma120:
                regime = 'UPTREND'
            elif current_price < sma20 < sma60 < sma120:
                regime = 'DOWNTREND'
            else:
                regime = 'SIDEWAYS'
            
            regime_history.append({
                "timestamp": btc_df['timestamp'].iloc[i].isoformat(),
                "regime": regime,
                "price": current_price,
                "sma20": sma20,
                "sma60": sma60,
                "sma120": sma120
            })
        
        return {
            "history": regime_history,
            "summary": {
                "total_periods": len(regime_history),
                "uptrend_periods": len([r for r in regime_history if r['regime'] == 'UPTREND']),
                "downtrend_periods": len([r for r in regime_history if r['regime'] == 'DOWNTREND']),
                "sideways_periods": len([r for r in regime_history if r['regime'] == 'SIDEWAYS'])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 조회 실패: {str(e)}")

@router.get("/regime/statistics")
async def get_regime_statistics() -> Dict[str, Any]:
    """
    시장 국면 통계 정보
    
    Returns:
        Dict: 시장 국면 통계
    """
    try:
        # 최근 30일 데이터 조회
        btc_df = await market_analyzer.get_btc_ohlcv(timeframe='1h', limit=720)  # 30일 * 24시간
        
        # 이동평균 계산
        btc_df['SMA20'] = btc_df['close'].rolling(window=20).mean()
        btc_df['SMA60'] = btc_df['close'].rolling(window=60).mean()
        btc_df['SMA120'] = btc_df['close'].rolling(window=120).mean()
        
        # 각 시점별 시장 국면 분석
        regimes = []
        for i in range(120, len(btc_df)):
            current_price = btc_df['close'].iloc[i]
            sma20 = btc_df['SMA20'].iloc[i]
            sma60 = btc_df['SMA60'].iloc[i]
            sma120 = btc_df['SMA120'].iloc[i]
            
            if current_price > sma20 > sma60 > sma120:
                regimes.append('UPTREND')
            elif current_price < sma20 < sma60 < sma120:
                regimes.append('DOWNTREND')
            else:
                regimes.append('SIDEWAYS')
        
        # 통계 계산
        total_periods = len(regimes)
        uptrend_count = regimes.count('UPTREND')
        downtrend_count = regimes.count('DOWNTREND')
        sideways_count = regimes.count('SIDEWAYS')
        
        return {
            "period": "30일",
            "total_periods": total_periods,
            "uptrend": {
                "count": uptrend_count,
                "percentage": round((uptrend_count / total_periods) * 100, 2)
            },
            "downtrend": {
                "count": downtrend_count,
                "percentage": round((downtrend_count / total_periods) * 100, 2)
            },
            "sideways": {
                "count": sideways_count,
                "percentage": round((sideways_count / total_periods) * 100, 2)
            },
            "current_regime": regimes[-1] if regimes else "UNKNOWN"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}") 