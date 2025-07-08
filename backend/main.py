"""
오딘(ODIN) - 암호화폐 자동매매 백테스팅 플랫폼
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from backend.app.api import regime, universe, live, backtest, websocket
from backend.app.core.database import init_db

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="오딘(ODIN) - 암호화폐 자동매매 플랫폼",
    description="실시간 시장 분석 및 자동매매 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(regime.router, prefix="/api", tags=["시장 분석"])
app.include_router(universe.router, prefix="/api", tags=["유니버스 스캔"])
app.include_router(live.router, prefix="/api/live", tags=["실시간 매매"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["백테스팅"])
app.include_router(websocket.router, tags=["웹소켓"])

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    await init_db()
    print("🚀 오딘(ODIN) 자동매매 시스템이 시작되었습니다!")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "오딘(ODIN) 암호화폐 자동매매 플랫폼에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "odin-trading-platform"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 