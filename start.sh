#!/bin/bash

echo "🚀 오딘(ODIN) 암호화폐 자동매매 플랫폼 시작"

# 환경 변수 파일 확인
if [ ! -f "backend/.env" ]; then
    echo "⚠️  backend/.env 파일이 없습니다. env.example을 복사하여 설정해주세요."
    cp backend/env.example backend/.env
    echo "📝 backend/.env 파일을 생성했습니다. 설정을 확인해주세요."
fi

# Docker Compose로 전체 서비스 시작
echo "🐳 Docker Compose로 서비스 시작 중..."
docker-compose up -d

echo "⏳ 서비스 시작 대기 중..."
sleep 10

# 서비스 상태 확인
echo "📊 서비스 상태 확인:"
docker-compose ps

echo ""
echo "✅ 오딘(ODIN) 플랫폼이 시작되었습니다!"
echo ""
echo "🌐 접속 주소:"
echo "   - 프론트엔드: http://localhost:3000"
echo "   - 백엔드 API: http://localhost:8000"
echo "   - API 문서: http://localhost:8000/docs"
echo "   - InfluxDB: http://localhost:8086"
echo ""
echo "📝 로그 확인:"
echo "   - 전체 로그: docker-compose logs -f"
echo "   - 백엔드 로그: docker-compose logs -f backend"
echo "   - 프론트엔드 로그: docker-compose logs -f frontend"
echo ""
echo "🛑 서비스 중지: docker-compose down" 