#!/bin/bash

# cryptography 패키지 설치 스크립트
# 웹 컨테이너에 cryptography 패키지를 설치합니다

echo "🔧 cryptography 패키지 설치 중..."

# 웹 컨테이너가 실행 중인지 확인
if ! docker compose ps web | grep -q "Up"; then
    echo "⚠️ 웹 컨테이너가 실행되지 않았습니다."
    echo "   웹 컨테이너를 먼저 시작하세요: docker compose up -d web"
    exit 1
fi

echo "📦 웹 컨테이너에 cryptography 패키지 설치 중..."
docker compose exec web pip install cryptography>=41.0.0

if [ $? -eq 0 ]; then
    echo "✅ cryptography 패키지 설치 완료"
    echo ""
    echo "🔄 웹 컨테이너 재시작 중..."
    docker compose restart web
    echo "✅ 웹 컨테이너 재시작 완료"
    echo ""
    echo "💡 이제 init_data.py를 다시 실행할 수 있습니다:"
    echo "   docker compose exec web python init_data.py"
else
    echo "❌ cryptography 패키지 설치 실패"
    echo ""
    echo "💡 대안: 웹 컨테이너를 재빌드하세요:"
    echo "   docker compose build web"
    echo "   docker compose restart web"
    exit 1
fi

