"""
유니버스 스캔 API
시장 국면에 따른 최적 코인 선정 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

from backend.app.core.market_analysis import market_analyzer

router = APIRouter()

@router.get("/universe")
async def get_universe() -> Dict[str, Any]:
    """
    현재 유니버스 목록 조회
    
    Returns:
        Dict: 선정된 코인 목록 및 분석 정보
    """
    try:
        # 시장 국면 분석
        btc_df = await market_analyzer.get_btc_ohlcv(timeframe='1h', limit=200)
        market_regime = market_analyzer.analyze_market_regime(btc_df)
        
        # 모든 티커 데이터 조회
        all_tickers = await market_analyzer.get_all_tickers()
        
        # 유니버스 스캔 실행
        selected_universe = market_analyzer.scan_universe(market_regime, all_tickers)
        
        # 선정된 코인들의 상세 정보 추가
        detailed_universe = []
        for coin in selected_universe:
            # 해당 코인의 티커 정보 찾기
            ticker_info = next((t for t in all_tickers if t['symbol'] == coin['symbol']), None)
            
            if ticker_info:
                detailed_universe.append({
                    "symbol": coin['symbol'],
                    "direction": coin['direction'],
                    "change_pct": round(ticker_info['change_pct'], 2),
                    "quote_volume": ticker_info['quote_volume'],
                    "last_price": ticker_info['last'],
                    "market_regime": market_regime
                })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "market_regime": market_regime,
            "selected_count": len(detailed_universe),
            "universe": detailed_universe,
            "analysis": {
                "total_tickers_analyzed": len(all_tickers),
                "usdt_pairs_count": len([t for t in all_tickers if t['symbol'].endswith('/USDT')]),
                "selection_criteria": f"시장 국면: {market_regime}, 상승률/거래대금 가중 점수 기준"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유니버스 스캔 실패: {str(e)}")

@router.get("/universe/top-gainers")
async def get_top_gainers(limit: int = 20) -> Dict[str, Any]:
    """
    상승률 상위 코인 목록
    
    Args:
        limit: 조회할 코인 수 (기본값: 20)
        
    Returns:
        Dict: 상승률 상위 코인 목록
    """
    try:
        all_tickers = await market_analyzer.get_all_tickers()
        
        # USDT 페어만 필터링
        usdt_pairs = [ticker for ticker in all_tickers if ticker['symbol'].endswith('/USDT')]
        
        # 상승률 기준 정렬
        top_gainers = sorted(usdt_pairs, key=lambda x: x.get('change_pct', 0), reverse=True)[:limit]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "count": len(top_gainers),
            "top_gainers": [
                {
                    "symbol": ticker['symbol'],
                    "change_pct": round(ticker['change_pct'], 2),
                    "quote_volume": ticker['quote_volume'],
                    "last_price": ticker['last']
                }
                for ticker in top_gainers
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상승률 상위 조회 실패: {str(e)}")

@router.get("/universe/top-losers")
async def get_top_losers(limit: int = 20) -> Dict[str, Any]:
    """
    하락률 상위 코인 목록
    
    Args:
        limit: 조회할 코인 수 (기본값: 20)
        
    Returns:
        Dict: 하락률 상위 코인 목록
    """
    try:
        all_tickers = await market_analyzer.get_all_tickers()
        
        # USDT 페어만 필터링
        usdt_pairs = [ticker for ticker in all_tickers if ticker['symbol'].endswith('/USDT')]
        
        # 하락률 기준 정렬 (오름차순)
        top_losers = sorted(usdt_pairs, key=lambda x: x.get('change_pct', 0))[:limit]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "count": len(top_losers),
            "top_losers": [
                {
                    "symbol": ticker['symbol'],
                    "change_pct": round(ticker['change_pct'], 2),
                    "quote_volume": ticker['quote_volume'],
                    "last_price": ticker['last']
                }
                for ticker in top_losers
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"하락률 상위 조회 실패: {str(e)}")

@router.get("/universe/top-volume")
async def get_top_volume(limit: int = 20) -> Dict[str, Any]:
    """
    거래대금 상위 코인 목록
    
    Args:
        limit: 조회할 코인 수 (기본값: 20)
        
    Returns:
        Dict: 거래대금 상위 코인 목록
    """
    try:
        all_tickers = await market_analyzer.get_all_tickers()
        
        # USDT 페어만 필터링
        usdt_pairs = [ticker for ticker in all_tickers if ticker['symbol'].endswith('/USDT')]
        
        # 거래대금 기준 정렬
        top_volume = sorted(usdt_pairs, key=lambda x: x.get('quote_volume', 0), reverse=True)[:limit]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "count": len(top_volume),
            "top_volume": [
                {
                    "symbol": ticker['symbol'],
                    "quote_volume": ticker['quote_volume'],
                    "change_pct": round(ticker['change_pct'], 2),
                    "last_price": ticker['last']
                }
                for ticker in top_volume
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"거래대금 상위 조회 실패: {str(e)}")

@router.get("/universe/analysis")
async def get_universe_analysis() -> Dict[str, Any]:
    """
    유니버스 분석 통계
    
    Returns:
        Dict: 유니버스 분석 통계 정보
    """
    try:
        all_tickers = await market_analyzer.get_all_tickers()
        
        # USDT 페어만 필터링
        usdt_pairs = [ticker for ticker in all_tickers if ticker['symbol'].endswith('/USDT')]
        
        # 통계 계산
        total_pairs = len(usdt_pairs)
        gainers = [t for t in usdt_pairs if t.get('change_pct', 0) > 0]
        losers = [t for t in usdt_pairs if t.get('change_pct', 0) < 0]
        unchanged = [t for t in usdt_pairs if t.get('change_pct', 0) == 0]
        
        # 평균 변화율
        avg_change = sum(t.get('change_pct', 0) for t in usdt_pairs) / total_pairs if total_pairs > 0 else 0
        
        # 거래대금 통계
        total_volume = sum(t.get('quote_volume', 0) for t in usdt_pairs)
        avg_volume = total_volume / total_pairs if total_pairs > 0 else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_usdt_pairs": total_pairs,
                "gainers": len(gainers),
                "losers": len(losers),
                "unchanged": len(unchanged),
                "gainers_percentage": round((len(gainers) / total_pairs) * 100, 2) if total_pairs > 0 else 0,
                "losers_percentage": round((len(losers) / total_pairs) * 100, 2) if total_pairs > 0 else 0
            },
            "statistics": {
                "average_change_pct": round(avg_change, 2),
                "total_volume": total_volume,
                "average_volume": round(avg_volume, 2),
                "max_gainer": max(usdt_pairs, key=lambda x: x.get('change_pct', 0)) if usdt_pairs else None,
                "max_loser": min(usdt_pairs, key=lambda x: x.get('change_pct', 0)) if usdt_pairs else None,
                "highest_volume": max(usdt_pairs, key=lambda x: x.get('quote_volume', 0)) if usdt_pairs else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유니버스 분석 실패: {str(e)}") 