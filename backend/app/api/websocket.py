"""
웹소켓 API
실시간 데이터 스트리밍을 위한 웹소켓 엔드포인트
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime
import logging

from app.core.market_analysis import market_analyzer

router = APIRouter()

# 웹소켓 연결 관리
class ConnectionManager:
    """웹소켓 연결 관리자"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """웹소켓 연결"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {
            "client_id": client_id or f"client_{len(self.active_connections)}",
            "connected_at": datetime.now(),
            "subscriptions": []
        }
        logging.info(f"웹소켓 연결: {self.connection_data[websocket]['client_id']}")
    
    def disconnect(self, websocket: WebSocket):
        """웹소켓 연결 해제"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            client_id = self.connection_data.get(websocket, {}).get("client_id", "unknown")
            del self.connection_data[websocket]
            logging.info(f"웹소켓 연결 해제: {client_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """개별 클라이언트에게 메시지 전송"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logging.error(f"메시지 전송 실패: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """모든 클라이언트에게 메시지 브로드캐스트"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logging.error(f"브로드캐스트 실패: {e}")
                disconnected.append(connection)
        
        # 연결이 끊어진 클라이언트 제거
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """연결 정보 반환"""
        return {
            "active_connections": len(self.active_connections),
            "clients": [
                {
                    "client_id": data["client_id"],
                    "connected_at": data["connected_at"].isoformat(),
                    "subscriptions": data["subscriptions"]
                }
                for data in self.connection_data.values()
            ]
        }

# 전역 연결 관리자
manager = ConnectionManager()

@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    실시간 데이터 웹소켓 엔드포인트
    
    실시간으로 다음 데이터를 스트리밍:
    - 시장 국면 정보
    - 유니버스 업데이트
    - 거래 로그
    - 포지션 상태
    - 시스템 상태
    """
    await manager.connect(websocket)
    
    try:
        # 클라이언트에게 연결 확인 메시지 전송
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": "웹소켓 연결이 설정되었습니다.",
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
        
        # 실시간 데이터 스트리밍 시작
        await start_live_streaming(websocket)
        
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"웹소켓 오류: {e}")
        manager.disconnect(websocket)

async def start_live_streaming(websocket: WebSocket):
    """
    실시간 데이터 스트리밍
    
    Args:
        websocket: 웹소켓 연결
    """
    try:
        while True:
            # 실시간 데이터 수집
            live_data = await collect_live_data()
            
            # 클라이언트에게 데이터 전송
            await manager.send_personal_message(
                json.dumps(live_data),
                websocket
            )
            
            # 5초마다 업데이트
            await asyncio.sleep(5)
            
    except Exception as e:
        logging.error(f"스트리밍 오류: {e}")

async def collect_live_data() -> Dict[str, Any]:
    """
    실시간 데이터 수집
    
    Returns:
        Dict: 실시간 데이터
    """
    try:
        # 시장 국면 데이터
        btc_df = await market_analyzer.get_btc_ohlcv(timeframe='1h', limit=200)
        market_regime = market_analyzer.analyze_market_regime(btc_df)
        
        # 유니버스 데이터
        all_tickers = await market_analyzer.get_all_tickers()
        selected_universe = market_analyzer.scan_universe(market_regime, all_tickers)
        
        # 시스템 상태
        system_status = {
            "status": "healthy",
            "uptime": "00:00:00",  # 실제로는 서버 시작 시간부터 계산
            "memory_usage": "0%",
            "cpu_usage": "0%"
        }
        
        return {
            "type": "live_data",
            "timestamp": datetime.now().isoformat(),
            "market_regime": {
                "regime": market_regime,
                "btc_price": btc_df['close'].iloc[-1],
                "change_24h": round(((btc_df['close'].iloc[-1] - btc_df['close'].iloc[-24]) / btc_df['close'].iloc[-24]) * 100, 2) if len(btc_df) >= 24 else 0
            },
            "universe": {
                "selected_count": len(selected_universe),
                "symbols": [coin["symbol"] for coin in selected_universe[:5]]
            },
            "system": system_status,
            "connections": manager.get_connection_info()
        }
        
    except Exception as e:
        logging.error(f"실시간 데이터 수집 실패: {e}")
        return {
            "type": "error",
            "message": f"데이터 수집 실패: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.websocket("/ws/trades")
async def trades_websocket(websocket: WebSocket):
    """
    거래 로그 웹소켓 엔드포인트
    
    실시간 거래 로그를 스트리밍합니다.
    """
    await manager.connect(websocket, "trades_client")
    
    try:
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": "거래 로그 스트리밍이 시작되었습니다.",
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
        
        # 거래 로그 시뮬레이션 (실제로는 데이터베이스에서 실시간 조회)
        await simulate_trade_logs(websocket)
        
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"거래 로그 웹소켓 오류: {e}")
        manager.disconnect(websocket)

async def simulate_trade_logs(websocket: WebSocket):
    """
    거래 로그 시뮬레이션
    
    Args:
        websocket: 웹소켓 연결
    """
    import random
    
    symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT", "LINK/USDT"]
    actions = ["BUY", "SELL", "CLOSE"]
    directions = ["LONG", "SHORT"]
    
    try:
        while True:
            # 랜덤 거래 로그 생성 (실제로는 실제 거래 데이터 사용)
            if random.random() < 0.1:  # 10% 확률로 거래 발생
                trade_log = {
                    "type": "trade_log",
                    "timestamp": datetime.now().isoformat(),
                    "symbol": random.choice(symbols),
                    "action": random.choice(actions),
                    "direction": random.choice(directions),
                    "price": round(random.uniform(100, 50000), 2),
                    "size": round(random.uniform(0.1, 10), 4),
                    "pnl": round(random.uniform(-100, 200), 2),
                    "strategy_id": "momentum_v1"
                }
                
                await manager.send_personal_message(
                    json.dumps(trade_log),
                    websocket
                )
            
            # 2초마다 체크
            await asyncio.sleep(2)
            
    except Exception as e:
        logging.error(f"거래 로그 시뮬레이션 오류: {e}")

@router.websocket("/ws/positions")
async def positions_websocket(websocket: WebSocket):
    """
    포지션 상태 웹소켓 엔드포인트
    
    실시간 포지션 상태를 스트리밍합니다.
    """
    await manager.connect(websocket, "positions_client")
    
    try:
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": "포지션 상태 스트리밍이 시작되었습니다.",
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
        
        # 포지션 상태 시뮬레이션
        await simulate_position_updates(websocket)
        
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"포지션 웹소켓 오류: {e}")
        manager.disconnect(websocket)

async def simulate_position_updates(websocket: WebSocket):
    """
    포지션 상태 시뮬레이션
    
    Args:
        websocket: 웹소켓 연결
    """
    import random
    
    symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT"]
    
    try:
        while True:
            # 랜덤 포지션 상태 생성
            positions = []
            for symbol in symbols:
                if random.random() < 0.3:  # 30% 확률로 포지션 보유
                    position = {
                        "symbol": symbol,
                        "direction": random.choice(["LONG", "SHORT"]),
                        "entry_price": round(random.uniform(100, 50000), 2),
                        "current_price": round(random.uniform(100, 50000), 2),
                        "size": round(random.uniform(0.1, 5), 4),
                        "unrealized_pnl": round(random.uniform(-500, 1000), 2),
                        "pnl_percentage": round(random.uniform(-10, 20), 2)
                    }
                    positions.append(position)
            
            position_update = {
                "type": "position_update",
                "timestamp": datetime.now().isoformat(),
                "total_positions": len(positions),
                "total_unrealized_pnl": round(sum(pos["unrealized_pnl"] for pos in positions), 2),
                "positions": positions
            }
            
            await manager.send_personal_message(
                json.dumps(position_update),
                websocket
            )
            
            # 3초마다 업데이트
            await asyncio.sleep(3)
            
    except Exception as e:
        logging.error(f"포지션 시뮬레이션 오류: {e}")

@router.get("/ws/status")
async def get_websocket_status() -> Dict[str, Any]:
    """
    웹소켓 연결 상태 조회
    
    Returns:
        Dict: 웹소켓 연결 상태
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "connections": manager.get_connection_info()
    } 