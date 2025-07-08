#!/bin/bash

echo "🛑 오딘(ODIN) 암호화폐 자동매매 플랫폼 중지"

# Docker Compose로 전체 서비스 중지
echo "🐳 Docker Compose로 서비스 중지 중..."
docker-compose down

echo "🧹 컨테이너 정리 중..."
docker system prune -f

echo ""
echo "✅ 오딘(ODIN) 플랫폼이 중지되었습니다!"
echo ""
echo "📝 데이터베이스 데이터는 보존됩니다."
echo "   - 완전 삭제: docker-compose down -v"
echo ""
echo "�� 다시 시작: ./start.sh" 