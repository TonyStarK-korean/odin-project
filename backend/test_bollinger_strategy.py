#!/usr/bin/env python3
"""
볼린저 밴드 돌파 전략 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backend.app.core.strategy_base import BollingerBandBreakoutStrategy

def generate_test_data():
    """테스트용 OHLCV 데이터 생성"""
    # 1시간봉 기준으로 100개 데이터 생성
    date_range = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    
    # 기본 가격 시뮬레이션
    base_price = 50000
    trend = np.linspace(0, 0.1, 100)  # 10% 상승 트렌드
    noise = np.random.normal(0, 0.02, 100)
    
    prices = base_price * (1 + trend + noise)
    
    ohlcv_data = []
    for i, (date, price) in enumerate(zip(date_range, prices)):
        volatility = 0.01
        
        open_price = price * (1 + np.random.normal(0, volatility))
        high_price = max(open_price, price) * (1 + abs(np.random.normal(0, volatility)))
        low_price = min(open_price, price) * (1 - abs(np.random.normal(0, volatility)))
        close_price = price * (1 + np.random.normal(0, volatility))
        
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

def test_bollinger_bands_calculation():
    """볼린저 밴드 계산 테스트"""
    print("=== 볼린저 밴드 계산 테스트 ===")
    
    strategy = BollingerBandBreakoutStrategy()
    test_data = generate_test_data()
    
    # 20볼린저 밴드 계산
    bb20_upper, bb20_middle, bb20_lower = strategy.calculate_bollinger_bands(
        test_data, 20, 2
    )
    
    print(f"20볼린저 밴드 상단선: {bb20_upper.iloc[-1]:.2f}")
    print(f"20볼린저 밴드 중간선: {bb20_middle.iloc[-1]:.2f}")
    print(f"20볼린저 밴드 하단선: {bb20_lower.iloc[-1]:.2f}")
    
    # 80볼린저 밴드 계산
    bb80_upper, bb80_middle, bb80_lower = strategy.calculate_bollinger_bands(
        test_data, 80, 2
    )
    
    print(f"80볼린저 밴드 상단선: {bb80_upper.iloc[-1]:.2f}")
    print(f"80볼린저 밴드 중간선: {bb80_middle.iloc[-1]:.2f}")
    print(f"80볼린저 밴드 하단선: {bb80_lower.iloc[-1]:.2f}")
    
    print()

def test_entry_signal():
    """진입 신호 테스트"""
    print("=== 진입 신호 테스트 ===")
    
    strategy = BollingerBandBreakoutStrategy()
    test_data = generate_test_data()
    
    # 최신 캔들 정보
    current_candle = test_data.iloc[-1]
    print(f"최신 캔들:")
    print(f"  시가: {current_candle['open']:.2f}")
    print(f"  고가: {current_candle['high']:.2f}")
    print(f"  저가: {current_candle['low']:.2f}")
    print(f"  종가: {current_candle['close']:.2f}")
    
    # 볼린저 밴드 값
    bb20_upper, bb20_middle, bb20_lower = strategy.calculate_bollinger_bands(
        test_data, 20, 2
    )
    bb80_upper, bb80_middle, bb80_lower = strategy.calculate_bollinger_bands(
        test_data, 80, 2
    )
    
    current_bb20_lower = bb20_lower.iloc[-1]
    current_bb20_upper = bb20_upper.iloc[-1]
    current_bb80_upper = bb80_upper.iloc[-1]
    
    print(f"20볼린저 밴드 하단선: {current_bb20_lower:.2f}")
    print(f"20볼린저 밴드 상단선: {current_bb20_upper:.2f}")
    print(f"80볼린저 밴드 상단선: {current_bb80_upper:.2f}")
    
    # 조건 확인
    condition1 = current_candle['open'] < current_bb20_lower
    combined_upper = current_bb20_upper + current_bb80_upper
    condition2 = current_candle['high'] > combined_upper
    condition3 = current_candle['close'] > current_candle['open']
    
    print(f"조건 1 (시가 < 20BB 하단): {condition1}")
    print(f"조건 2 (고가 > 20BB+80BB 상단): {condition2}")
    print(f"조건 3 (양봉): {condition3}")
    
    # 진입 신호 확인
    entry_signal = strategy.check_entry_signal(test_data)
    print(f"진입 신호: {entry_signal}")
    
    if entry_signal:
        entry_price = strategy.get_entry_price(test_data)
        position_size_ratio = strategy.get_position_size_ratio()
        print(f"진입 가격: {entry_price:.2f}")
        print(f"포지션 크기 비율: {position_size_ratio * 100}%")
    
    print()

def test_strategy_parameters():
    """전략 파라미터 테스트"""
    print("=== 전략 파라미터 테스트 ===")
    
    strategy = BollingerBandBreakoutStrategy()
    
    print(f"전략 ID: {strategy.strategy_id}")
    print(f"전략 이름: {strategy.name}")
    print(f"전략 설명: {strategy.description}")
    print(f"파라미터: {strategy.parameters}")
    
    # 레버리지 테스트
    print(f"상승장 레버리지: {strategy.determine_leverage('UPTREND')}")
    print(f"하락장 레버리지: {strategy.determine_leverage('DOWNTREND')}")
    print(f"횡보장 레버리지: {strategy.determine_leverage('SIDEWAYS')}")
    
    # 트레일링 스탑 테스트
    entry_price = 50000
    stop_info = strategy.set_trailing_stop(entry_price)
    print(f"진입가격: {entry_price}")
    print(f"손절가: {stop_info['stop_loss']:.2f}")
    print(f"최대 익절 목표: {stop_info['max_profit_target']:.2f} (200%)")
    print(f"초기 트레일링 스탑: {stop_info['trailing_stop']:.2f}")
    print(f"트레일링 스탑 방식: 최고가 대비 1.5% 하락 시 청산")
    
    print()

def main():
    """메인 테스트 함수"""
    print("볼린저 밴드 돌파 전략 테스트")
    print("=" * 50)
    
    test_bollinger_bands_calculation()
    test_entry_signal()
    test_strategy_parameters()
    
    print("테스트 완료!")

if __name__ == "__main__":
    main() 