"""
시장 분석 핵심 로직 모듈
시장 국면 분석 및 유니버스 스캔 기능을 제공합니다.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import ccxt
import asyncio
from datetime import datetime, timedelta

class MarketAnalyzer:
    """시장 분석 클래스"""
    
    def __init__(self, exchange_name: str = "binance"):
        """
        시장 분석기 초기화
        
        Args:
            exchange_name: 거래소 이름 (기본값: binance)
        """
        self.exchange = getattr(ccxt, exchange_name)({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
    
    def analyze_market_regime(self, btc_ohlcv_df: pd.DataFrame) -> str:
        """
        비트코인 기반 시장 국면 분석
        
        Args:
            btc_ohlcv_df: 비트코인 OHLCV 데이터 (최소 120개 캔들)
            
        Returns:
            str: 'UPTREND', 'DOWNTREND', 'SIDEWAYS'
        """
        if len(btc_ohlcv_df) < 120:
            raise ValueError("최소 120개 캔들이 필요합니다.")
        
        # 이동평균 계산
        btc_ohlcv_df['SMA20'] = btc_ohlcv_df['close'].rolling(window=20).mean()
        btc_ohlcv_df['SMA60'] = btc_ohlcv_df['close'].rolling(window=60).mean()
        btc_ohlcv_df['SMA120'] = btc_ohlcv_df['close'].rolling(window=120).mean()
        
        # 최신 데이터
        current_price = btc_ohlcv_df['close'].iloc[-1]
        sma20 = btc_ohlcv_df['SMA20'].iloc[-1]
        sma60 = btc_ohlcv_df['SMA60'].iloc[-1]
        sma120 = btc_ohlcv_df['SMA120'].iloc[-1]
        
        # 시장 국면 판단
        if current_price > sma20 > sma60 > sma120:
            return 'UPTREND'
        elif current_price < sma20 < sma60 < sma120:
            return 'DOWNTREND'
        else:
            return 'SIDEWAYS'
    
    def scan_universe(self, market_regime: str, all_tickers_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        시장 국면에 따른 유니버스 스캔
        
        Args:
            market_regime: 시장 국면 ('UPTREND', 'DOWNTREND', 'SIDEWAYS')
            all_tickers_data: 모든 티커 데이터 리스트
            
        Returns:
            List[Dict]: 선정된 코인 목록 [{"symbol": "BTC/USDT", "direction": "long"}, ...]
        """
        # USDT 페어만 필터링
        usdt_pairs = [ticker for ticker in all_tickers_data if ticker['symbol'].endswith('/USDT')]
        
        # 상승률/하락률 기준으로 정렬
        if market_regime == 'UPTREND':
            # 상승률 기준 정렬
            sorted_by_change = sorted(usdt_pairs, key=lambda x: x.get('change_pct', 0), reverse=True)
            top_change = sorted_by_change[:10]
            
            # 거래대금 기준 정렬
            sorted_by_volume = sorted(usdt_pairs, key=lambda x: x.get('quote_volume', 0), reverse=True)
            top_volume = sorted_by_volume[:10]
            
            # 가중 점수 계산
            selected = self._calculate_weighted_score(top_change, top_volume, 0.6, 0.4)
            return [{"symbol": item['symbol'], "direction": "long"} for item in selected[:5]]
            
        elif market_regime == 'DOWNTREND':
            # 하락률 기준 정렬
            sorted_by_change = sorted(usdt_pairs, key=lambda x: x.get('change_pct', 0))
            top_change = sorted_by_change[:10]
            
            # 거래대금 기준 정렬
            sorted_by_volume = sorted(usdt_pairs, key=lambda x: x.get('quote_volume', 0), reverse=True)
            top_volume = sorted_by_volume[:10]
            
            # 가중 점수 계산
            selected = self._calculate_weighted_score(top_change, top_volume, 0.6, 0.4)
            return [{"symbol": item['symbol'], "direction": "short"} for item in selected[:5]]
            
        else:  # SIDEWAYS
            # 상승/하락 각각 5개씩 선정
            sorted_by_change = sorted(usdt_pairs, key=lambda x: x.get('change_pct', 0), reverse=True)
            top_gainers = sorted_by_change[:10]
            top_losers = sorted_by_change[-10:]
            
            sorted_by_volume = sorted(usdt_pairs, key=lambda x: x.get('quote_volume', 0), reverse=True)
            top_volume = sorted_by_volume[:10]
            
            # 상승 종목 선정
            selected_long = self._calculate_weighted_score(top_gainers, top_volume, 0.6, 0.4)[:5]
            # 하락 종목 선정
            selected_short = self._calculate_weighted_score(top_losers, top_volume, 0.6, 0.4)[:5]
            
            result = []
            result.extend([{"symbol": item['symbol'], "direction": "long"} for item in selected_long])
            result.extend([{"symbol": item['symbol'], "direction": "short"} for item in selected_short])
            
            return result
    
    def _calculate_weighted_score(self, change_list: List[Dict], volume_list: List[Dict], 
                                 change_weight: float, volume_weight: float) -> List[Dict]:
        """
        가중 점수 계산
        
        Args:
            change_list: 변화율 기준 상위 리스트
            volume_list: 거래대금 기준 상위 리스트
            change_weight: 변화율 가중치
            volume_weight: 거래대금 가중치
            
        Returns:
            List[Dict]: 가중 점수로 정렬된 리스트
        """
        # 점수 계산을 위한 딕셔너리 생성
        scores = {}
        
        # 변화율 점수 계산
        for i, item in enumerate(change_list):
            symbol = item['symbol']
            if symbol not in scores:
                scores[symbol] = {'symbol': symbol, 'data': item, 'score': 0}
            scores[symbol]['score'] += (10 - i) * change_weight
        
        # 거래대금 점수 계산
        for i, item in enumerate(volume_list):
            symbol = item['symbol']
            if symbol not in scores:
                scores[symbol] = {'symbol': symbol, 'data': item, 'score': 0}
            scores[symbol]['score'] += (10 - i) * volume_weight
        
        # 점수로 정렬
        sorted_items = sorted(scores.values(), key=lambda x: x['score'], reverse=True)
        return [item['data'] for item in sorted_items]
    
    async def get_btc_ohlcv(self, timeframe: str = '1h', limit: int = 200) -> pd.DataFrame:
        """
        비트코인 OHLCV 데이터 조회
        
        Args:
            timeframe: 시간프레임 (1m, 5m, 15m, 1h, 4h, 1d)
            limit: 조회할 캔들 수
            
        Returns:
            pd.DataFrame: OHLCV 데이터
        """
        try:
            ohlcv = await self.exchange.fetch_ohlcv('BTC/USDT', timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"비트코인 데이터 조회 실패: {e}")
            raise
    
    async def get_all_tickers(self) -> List[Dict[str, Any]]:
        """
        모든 티커 데이터 조회
        
        Returns:
            List[Dict]: 모든 티커 정보
        """
        try:
            tickers = await self.exchange.fetch_tickers()
            return [
                {
                    'symbol': symbol,
                    'change_pct': ticker.get('percentage', 0),
                    'quote_volume': ticker.get('quoteVolume', 0),
                    'last': ticker.get('last', 0)
                }
                for symbol, ticker in tickers.items()
            ]
        except Exception as e:
            print(f"티커 데이터 조회 실패: {e}")
            raise

# 전역 인스턴스
market_analyzer = MarketAnalyzer() 