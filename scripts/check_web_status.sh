#!/bin/bash

# 웹 애플리케이션 상태 확인 스크립트

echo "🔍 웹 애플리케이션 상태 확인 중..."
echo ""

# 1. 컨테이너 상태 확인
echo "1️⃣ 컨테이너 상태:"
docker compose ps web

echo ""
echo "2️⃣ 웹 컨테이너 로그 (마지막 50줄):"
docker compose logs --tail=50 web

echo ""
echo "3️⃣ 포트 바인딩 확인:"
docker compose ps web | grep -E "PORTS|5000" || echo "   포트 정보를 찾을 수 없습니다"

echo ""
echo "4️⃣ 컨테이너 내부 프로세스 확인:"
if docker compose ps web | grep -q "Up"; then
    echo "   Gunicorn 프로세스:"
    docker compose exec web ps aux | grep -E "gunicorn|python" || echo "   프로세스를 찾을 수 없습니다"
    
    echo ""
    echo "   포트 5000 리스닝 확인:"
    docker compose exec web netstat -tlnp 2>/dev/null | grep 5000 || \
    docker compose exec web ss -tlnp 2>/dev/null | grep 5000 || \
    echo "   netstat/ss 명령어를 사용할 수 없습니다"
else
    echo "   ⚠️ 웹 컨테이너가 실행되지 않았습니다"
fi

echo ""
echo "5️⃣ 로컬에서 연결 테스트:"
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "   ✅ localhost:5000 연결 성공"
else
    echo "   ❌ localhost:5000 연결 실패"
fi

echo ""
echo "6️⃣ 환경 변수 확인:"
docker compose exec web env 2>/dev/null | grep -E "DATABASE_URL|FLASK|KEYCLOAK" | head -10 || echo "   환경 변수를 확인할 수 없습니다"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 요약:"
echo ""

if docker compose ps web | grep -q "Up"; then
    echo "   ✅ 웹 컨테이너: 실행 중"
else
    echo "   ❌ 웹 컨테이너: 실행되지 않음"
fi

if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "   ✅ 웹 애플리케이션: 응답 중"
else
    echo "   ❌ 웹 애플리케이션: 응답 없음"
fi

echo ""
echo "💡 다음 명령어로 더 자세히 확인:"
echo "   docker compose logs -f web"
echo "   docker compose exec web ps aux"
echo "   docker compose exec web curl http://localhost:5000"

