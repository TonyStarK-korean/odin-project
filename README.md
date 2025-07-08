# ODIN (오딘) - 암호화폐 자동매매 및 백테스팅 플랫폼

## 프로젝트 개요

ODIN은 암호화폐 자동매매 및 백테스팅을 위한 종합 플랫폼입니다. 실시간 시장 분석, 다양한 매매 전략, 백테스팅 기능을 제공하여 체계적인 암호화폐 투자를 지원합니다.

## 주요 기능

### 1. 시장 분석
- 실시간 시장 국면 분석 (상승장/하락장/횡보장)
- 유니버스 스캔 (거래량, 변동성, 모멘텀 기반)
- 기술적 지표 분석

### 2. 매매 전략

#### 2.1 모멘텀 전략 (momentum_v1)
- RSI와 이동평균을 활용한 모멘텀 기반 전략
- RSI < 30이고 단기이평 > 장기이평일 때 매수

#### 2.2 평균회귀 전략 (mean_reversion_v1)
- 볼린저 밴드를 활용한 평균회귀 전략
- 가격이 하단 밴드 근처이고 RSI < 30일 때 매수

#### 2.3 볼린저 밴드 돌파 매수전략 (bollinger_breakout_v1) ⭐ **NEW**
- **1시간봉 기준** 볼린저 밴드 돌파 매수전략
- **매수 조건:**
  1. 시가가 20볼린저 밴드 하단선 아래에서 시작
  2. 고점이 20볼린저 밴드 상단선 + 80볼린저 밴드 상단선 동시 돌파
  3. 1시간봉 캔들이 양봉으로 마감
- **진입 전략:** 해당 1시간봉 캔들 양봉 종가에 일부, 다음 1시간봉 캔들 눌림목에서 일부 매수
- **포지션 크기:** 전체 자본의 30%
- **리스크 관리:** 3% 손절, 최대 200% 익절 (트레일링 스탑), 1.5% 트레일링 스탑

### 3. 백테스팅
- 과거 데이터를 활용한 전략 성과 검증
- 다양한 성과 지표 제공 (수익률, 승률, MDD, 샤프 비율 등)
- 실시간 백테스트 진행 상황 모니터링

### 4. 실시간 매매
- 웹소켓을 통한 실시간 시장 데이터 수신
- 자동 매매 실행 및 포지션 관리
- 실시간 손익 모니터링

## 기술 스택

### Backend
- **Framework:** FastAPI
- **Database:** PostgreSQL (거래 로그, 백테스트 결과), InfluxDB (시계열 데이터)
- **Language:** Python 3.11+
- **Libraries:** pandas, numpy, scikit-learn, ta-lib

### Frontend
- **Framework:** React 18 + TypeScript
- **UI Library:** Ant Design
- **Charts:** Recharts
- **State Management:** React Hooks

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Message Queue:** Redis (선택사항)
- **Monitoring:** Prometheus + Grafana (선택사항)

## 설치 및 실행

### 1. 환경 설정
```bash
# 저장소 클론
git clone <repository-url>
cd Odin

# 환경 변수 설정
cp backend/env.example backend/.env
# .env 파일을 편집하여 데이터베이스 연결 정보 설정
```

### 2. Docker를 사용한 실행
```bash
# 전체 시스템 시작
./start.sh

# 또는 수동으로 실행
docker-compose up -d

# 시스템 중지
./stop.sh
```

### 3. 개발 환경 실행
```bash
# Backend 실행
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend 실행
cd frontend
npm install
npm start
```

## API 엔드포인트

### 백테스팅 API
- `POST /api/backtest/backtest` - 백테스트 실행
- `GET /api/backtest/result/{job_id}` - 백테스트 결과 조회
- `GET /api/backtest/history` - 백테스트 히스토리
- `GET /api/backtest/strategies` - 사용 가능한 전략 목록

### 실시간 매매 API
- `GET /api/live/status` - 실시간 매매 상태
- `POST /api/live/start` - 실시간 매매 시작
- `POST /api/live/stop` - 실시간 매매 중지

### 시장 분석 API
- `GET /api/regime/current` - 현재 시장 국면
- `GET /api/universe/scan` - 유니버스 스캔 결과

## 볼린저 밴드 돌파 전략 상세 설명

### 전략 로직
1. **데이터 준비:** 1시간봉 OHLCV 데이터 수집
2. **볼린저 밴드 계산:**
   - 20기간 볼린저 밴드 (표준편차 2배)
   - 80기간 볼린저 밴드 (표준편차 2배)
3. **매수 신호 확인:**
   - 조건 1: 시가 < 20볼린저 밴드 하단선
   - 조건 2: 고가 > (20볼린저 밴드 상단선 + 80볼린저 밴드 상단선)
   - 조건 3: 종가 > 시가 (양봉)
4. **진입 실행:**
   - 진입 가격: 현재 종가의 99.5% (다음 봉 눌림목 대비)
   - 포지션 크기: 전체 자본의 30%

### 리스크 관리
- **손절:** 진입가의 97% (3% 손실)
- **익절:** 최대 200% (트레일링 스탑으로 관리)
- **트레일링 스탑:** 최고가 대비 1.5% 하락 시 청산
- **최대 익절 목표:** 진입가의 300% (200% 수익)

### 백테스팅 결과 예시
```
초기 자본: $10,000
최종 자본: $15,500
총 수익률: 55.0%
총 거래 수: 45
승률: 62.2%
최대 낙폭: 8.3%
샤프 비율: 2.1
```

## 개발 가이드

### 새로운 전략 추가
1. `backend/app/core/strategy_base.py`에서 `BaseStrategy`를 상속받는 새 클래스 생성
2. 필수 메서드 구현:
   - `check_entry_signal()`: 진입 신호 확인
   - `determine_leverage()`: 레버리지 결정
   - `set_trailing_stop()`: 트레일링 스탑 설정
3. `StrategyFactory`에 새 전략 등록

### 백테스팅 로직 수정
- `backend/app/api/backtest.py`의 `simulate_backtest()` 함수 수정
- 실제 거래소 API 연동 시 OHLCV 데이터 수집 로직 추가

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 문의사항

프로젝트에 대한 문의사항이나 버그 리포트는 GitHub Issues를 통해 제출해 주세요. 