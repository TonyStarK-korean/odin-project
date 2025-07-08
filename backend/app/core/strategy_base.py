"""
전략 기본 클래스
모든 매매 전략이 상속받아야 할 추상 클래스
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

class BaseStrategy(ABC):
    """매매 전략 기본 클래스"""
    
    def __init__(self, strategy_id: str, name: str, description: str = ""):
        """
        전략 초기화
        
        Args:
            strategy_id: 전략 고유 ID
            name: 전략 이름
            description: 전략 설명
        """
        self.strategy_id = strategy_id
        self.name = name
        self.description = description
        self.parameters = {}
    
    @abstractmethod
    def check_entry_signal(self, ohlcv_df: pd.DataFrame) -> bool:
        """
        진입 신호 확인
        
        Args:
            ohlcv_df: OHLCV 데이터프레임
            
        Returns:
            bool: 진입 신호 여부
        """
        pass
    
    @abstractmethod
    def determine_leverage(self, market_regime: str) -> float:
        """
        레버리지 결정
        
        Args:
            market_regime: 시장 국면 ('UPTREND', 'DOWNTREND', 'SIDEWAYS')
            
        Returns:
            float: 레버리지 값
        """
        pass
    
    @abstractmethod
    def set_trailing_stop(self, entry_price: float) -> Dict[str, float]:
        """
        트레일링 스탑 설정
        
        Args:
            entry_price: 진입 가격
            
        Returns:
            Dict: 스탑로스 및 익절 정보
        """
        pass
    
    def calculate_position_size(self, capital: float, risk_per_trade: float, 
                              entry_price: float, stop_loss: float) -> float:
        """
        포지션 크기 계산
        
        Args:
            capital: 총 자본금
            risk_per_trade: 거래당 위험 비율
            entry_price: 진입 가격
            stop_loss: 스탑로스 가격
            
        Returns:
            float: 포지션 크기
        """
        risk_amount = capital * risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        return position_size
    
    def calculate_pnl(self, entry_price: float, current_price: float, 
                     position_size: float, direction: str) -> float:
        """
        손익 계산
        
        Args:
            entry_price: 진입 가격
            current_price: 현재 가격
            position_size: 포지션 크기
            direction: 포지션 방향 ('long', 'short')
            
        Returns:
            float: 손익
        """
        if direction == 'long':
            return (current_price - entry_price) * position_size
        else:  # short
            return (entry_price - current_price) * position_size
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        전략 정보 반환
        
        Returns:
            Dict: 전략 정보
        """
        return {
            'strategy_id': self.strategy_id,
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters
        }

class MomentumStrategy(BaseStrategy):
    """모멘텀 기반 전략 예시"""
    
    def __init__(self):
        super().__init__(
            strategy_id="momentum_v1",
            name="모멘텀 전략 v1",
            description="RSI와 이동평균을 활용한 모멘텀 전략"
        )
        self.parameters = {
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'sma_short': 20,
            'sma_long': 50
        }
    
    def check_entry_signal(self, ohlcv_df: pd.DataFrame) -> bool:
        """모멘텀 진입 신호 확인"""
        if len(ohlcv_df) < 50:
            return False
        
        # RSI 계산
        delta = ohlcv_df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.parameters['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.parameters['rsi_period']).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 이동평균 계산
        sma_short = ohlcv_df['close'].rolling(window=self.parameters['sma_short']).mean()
        sma_long = ohlcv_df['close'].rolling(window=self.parameters['sma_long']).mean()
        
        current_rsi = rsi.iloc[-1]
        current_sma_short = sma_short.iloc[-1]
        current_sma_long = sma_long.iloc[-1]
        
        # 매수 신호: RSI < 30이고 단기이평 > 장기이평
        if current_rsi < self.parameters['rsi_oversold'] and current_sma_short > current_sma_long:
            return True
        
        return False
    
    def determine_leverage(self, market_regime: str) -> float:
        """레버리지 결정"""
        leverage_map = {
            'UPTREND': 2.0,
            'DOWNTREND': 1.5,
            'SIDEWAYS': 1.0
        }
        return leverage_map.get(market_regime, 1.0)
    
    def set_trailing_stop(self, entry_price: float) -> Dict[str, float]:
        """트레일링 스탑 설정"""
        stop_loss = entry_price * 0.95  # 5% 손절
        take_profit = entry_price * 1.15  # 15% 익절
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'trailing_stop': entry_price * 0.98  # 2% 트레일링 스탑
        }

class MeanReversionStrategy(BaseStrategy):
    """평균회귀 기반 전략 예시"""
    
    def __init__(self):
        super().__init__(
            strategy_id="mean_reversion_v1",
            name="평균회귀 전략 v1",
            description="볼린저 밴드를 활용한 평균회귀 전략"
        )
        self.parameters = {
            'bb_period': 20,
            'bb_std': 2,
            'rsi_period': 14,
            'rsi_overbought': 80,
            'rsi_oversold': 20
        }
    
    def check_entry_signal(self, ohlcv_df: pd.DataFrame) -> bool:
        """평균회귀 진입 신호 확인"""
        if len(ohlcv_df) < 20:
            return False
        
        # 볼린저 밴드 계산
        sma = ohlcv_df['close'].rolling(window=self.parameters['bb_period']).mean()
        std = ohlcv_df['close'].rolling(window=self.parameters['bb_period']).std()
        upper_band = sma + (std * self.parameters['bb_std'])
        lower_band = sma - (std * self.parameters['bb_std'])
        
        # RSI 계산
        delta = ohlcv_df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.parameters['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.parameters['rsi_period']).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_price = ohlcv_df['close'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # 매수 신호: 가격이 하단 밴드 근처이고 RSI < 30
        if (current_price <= current_lower * 1.02 and 
            current_rsi < self.parameters['rsi_oversold']):
            return True
        
        return False
    
    def determine_leverage(self, market_regime: str) -> float:
        """레버리지 결정"""
        leverage_map = {
            'UPTREND': 1.5,
            'DOWNTREND': 1.0,
            'SIDEWAYS': 2.0
        }
        return leverage_map.get(market_regime, 1.0)
    
    def set_trailing_stop(self, entry_price: float) -> Dict[str, float]:
        """트레일링 스탑 설정"""
        stop_loss = entry_price * 0.97  # 3% 손절
        take_profit = entry_price * 1.10  # 10% 익절
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'trailing_stop': entry_price * 0.99  # 1% 트레일링 스탑
        }

class BollingerBandBreakoutStrategy(BaseStrategy):
    """볼린저 밴드 돌파 매수전략"""
    
    def __init__(self):
        super().__init__(
            strategy_id="bollinger_breakout_v1",
            name="볼린저 밴드 돌파 매수전략 v1",
            description="1시간봉 기준 볼린저 밴드 돌파 매수전략 - 시가가 20BB 아래에서 시작하고 고점이 20BB+80BB 상단선 동시 돌파하면서 양봉 마감"
        )
        self.parameters = {
            'bb_20_period': 20,
            'bb_20_std': 2,
            'bb_80_period': 80,
            'bb_80_std': 2,
            'timeframe': '1h'
        }
    
    def calculate_bollinger_bands(self, ohlcv_df: pd.DataFrame, period: int, std_dev: float) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        볼린저 밴드 계산
        
        Args:
            ohlcv_df: OHLCV 데이터프레임
            period: 이동평균 기간
            std_dev: 표준편차 배수
            
        Returns:
            Tuple: (상단선, 중간선, 하단선)
        """
        sma = ohlcv_df['close'].rolling(window=period).mean()
        std = ohlcv_df['close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    def check_entry_signal(self, ohlcv_df: pd.DataFrame) -> bool:
        """
        볼린저 밴드 돌파 매수 신호 확인
        
        조건:
        1. 시가가 20볼린저 밴드 하단선 아래에서 시작
        2. 고점이 20볼린저 밴드 상단선 + 80볼린저 밴드 상단선 동시 돌파
        3. 1시간봉 캔들이 양봉으로 마감
        """
        if len(ohlcv_df) < 80:
            return False
        
        # 20볼린저 밴드 계산
        bb20_upper, bb20_middle, bb20_lower = self.calculate_bollinger_bands(
            ohlcv_df, self.parameters['bb_20_period'], self.parameters['bb_20_std']
        )
        
        # 80볼린저 밴드 계산
        bb80_upper, bb80_middle, bb80_lower = self.calculate_bollinger_bands(
            ohlcv_df, self.parameters['bb_80_period'], self.parameters['bb_80_std']
        )
        
        # 최신 캔들 데이터
        current_candle = ohlcv_df.iloc[-1]
        current_open = current_candle['open']
        current_high = current_candle['high']
        current_close = current_candle['close']
        current_low = current_candle['low']
        
        # 최신 볼린저 밴드 값
        current_bb20_lower = bb20_lower.iloc[-1]
        current_bb20_upper = bb20_upper.iloc[-1]
        current_bb80_upper = bb80_upper.iloc[-1]
        
        # 조건 1: 시가가 20볼린저 밴드 하단선 아래에서 시작
        condition1 = current_open < current_bb20_lower
        
        # 조건 2: 고점이 20볼린저 밴드 상단선 + 80볼린저 밴드 상단선 동시 돌파
        combined_upper = current_bb20_upper + current_bb80_upper
        condition2 = current_high > combined_upper
        
        # 조건 3: 양봉으로 마감 (시가 < 종가)
        condition3 = current_close > current_open
        
        # 모든 조건 만족 시 매수 신호
        return condition1 and condition2 and condition3
    
    def determine_leverage(self, market_regime: str) -> float:
        """레버리지 결정"""
        leverage_map = {
            'UPTREND': 1.5,
            'DOWNTREND': 1.0,
            'SIDEWAYS': 1.2
        }
        return leverage_map.get(market_regime, 1.0)
    
    def set_trailing_stop(self, entry_price: float) -> Dict[str, float]:
        """트레일링 스탑 설정"""
        stop_loss = entry_price * 0.97  # 3% 손절
        take_profit = entry_price * 3.00  # 200% 익절 (트레일링 스탑으로 관리)
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'trailing_stop': entry_price * 0.985,  # 1.5% 트레일링 스탑
            'max_profit_target': entry_price * 3.00  # 최대 200% 익절 목표
        }
    
    def get_entry_price(self, ohlcv_df: pd.DataFrame) -> float:
        """
        진입 가격 결정 (다음 1시간봉 눌림목에서 일부 매수)
        
        Args:
            ohlcv_df: OHLCV 데이터프레임
            
        Returns:
            float: 진입 가격 (현재 캔들 종가 기준)
        """
        current_close = ohlcv_df.iloc[-1]['close']
        
        # 다음 1시간봉 눌림목에서 매수하기 위해 현재 종가에서 약간 할인된 가격으로 설정
        entry_price = current_close * 0.995  # 0.5% 할인
        
        return entry_price
    
    def get_position_size_ratio(self) -> float:
        """
        포지션 크기 비율 (일부 매수)
        
        Returns:
            float: 전체 자본 대비 매수 비율 (0.3 = 30%)
        """
        return 0.3  # 30% 매수

# 전략 팩토리
class StrategyFactory:
    """전략 팩토리 클래스"""
    
    _strategies = {
        'momentum_v1': MomentumStrategy,
        'mean_reversion_v1': MeanReversionStrategy,
        'bollinger_breakout_v1': BollingerBandBreakoutStrategy
    }
    
    @classmethod
    def get_strategy(cls, strategy_id: str) -> BaseStrategy:
        """
        전략 인스턴스 생성
        
        Args:
            strategy_id: 전략 ID
            
        Returns:
            BaseStrategy: 전략 인스턴스
        """
        if strategy_id not in cls._strategies:
            raise ValueError(f"알 수 없는 전략 ID: {strategy_id}")
        
        return cls._strategies[strategy_id]()
    
    @classmethod
    def get_available_strategies(cls) -> Dict[str, str]:
        """
        사용 가능한 전략 목록 반환
        
        Returns:
            Dict: 전략 ID와 이름 매핑
        """
        return {strategy_id: strategy().name 
                for strategy_id, strategy in cls._strategies.items()} 