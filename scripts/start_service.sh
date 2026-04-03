#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}" || { echo "❌ 프로젝트 루트로 이동 실패"; exit 1; }

echo "🚀 Portfolio 웹사이트 시작 중..."

# IP 감지
HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$HOST_IP" ]; then
    HOST_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "localhost")
fi
echo "📍 IP: ${HOST_IP}"

# .env 파일 생성
if [ ! -f ".env" ]; then
    echo "📝 .env 파일 생성 중..."
    cat > .env << EOF
KEYCLOAK_URL=http://${HOST_IP}:8080
KEYCLOAK_REALM=portfolio
KEYCLOAK_CLIENT_ID=portfolio-web
KEYCLOAK_CLIENT_SECRET=temp-secret-will-be-updated
DATABASE_URL=mysql+pymysql://root:password@db:3306/portfolio_db
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=production
ELASTICSEARCH_URL=http://elasticsearch:9200
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000
EOF
    echo "✅ .env 생성 완료"
fi

# 기존 서비스 정리
echo ""
echo "🧹 기존 서비스 정리 중..."
docker compose down 2>/dev/null

# 인프라 시작 (DB, Elasticsearch)
echo ""
echo "📦 인프라 서비스 시작 (DB, Elasticsearch, ChromaDB)..."
docker compose up -d db elasticsearch chromadb

# MySQL 대기
echo ""
echo "⏳ MySQL 대기 중..."
for i in $(seq 1 12); do
    if docker compose exec -T db mysqladmin ping -h localhost -u root -ppassword --silent 2>/dev/null; then
        echo "✅ MySQL 준비 완료"
        break
    fi
    echo "   대기 중... ($((i*5))초)"
    sleep 5
done

# Keycloak DB 초기화
echo ""
echo "🔧 Keycloak 데이터베이스 설정 중..."
docker compose exec -T db mysql -u root -ppassword <<EOF
CREATE DATABASE IF NOT EXISTS keycloak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
DROP USER IF EXISTS 'keycloak'@'%';
CREATE USER 'keycloak'@'%' IDENTIFIED BY 'keycloak123';
GRANT ALL PRIVILEGES ON keycloak.* TO 'keycloak'@'%';
FLUSH PRIVILEGES;
EOF
echo "✅ Keycloak DB 설정 완료"

# Elasticsearch 대기
echo ""
echo "⏳ Elasticsearch 대기 중..."
for i in $(seq 1 24); do
    if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        echo "✅ Elasticsearch 준비 완료"
        break
    fi
    echo "   대기 중... ($((i*5))초)"
    sleep 5
done

# Keycloak 시작
echo ""
echo "🚀 Keycloak 시작 중..."
docker compose up -d keycloak

echo "⏳ Keycloak 대기 중 (첫 시작 시 5-10분 소요)..."
for i in $(seq 1 60); do
    if curl -s http://${HOST_IP}:8080/realms/master > /dev/null 2>&1 || \
       curl -s http://localhost:8080/realms/master > /dev/null 2>&1; then
        echo "✅ Keycloak 준비 완료"
        break
    fi
    if [ $((i % 6)) -eq 0 ]; then
        echo "   대기 중... ($((i*10))초)"
    fi
    sleep 10
done

# Keycloak 설정
echo ""
echo "⚙️ Keycloak 설정 중..."
if python3 setup_keycloak.py; then
    echo "✅ Keycloak 설정 완료"
else
    echo "⚠️ Keycloak 설정 실패"
fi

# 웹 애플리케이션 시작
echo ""
echo "🌐 웹 애플리케이션 시작 중..."
docker compose up -d web

echo "⏳ 웹 애플리케이션 대기 중..."
for i in $(seq 1 24); do
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        echo "✅ 웹 애플리케이션 준비 완료"
        break
    fi
    echo "   대기 중... ($((i*5))초)"
    sleep 5
done

# Nginx 시작
echo ""
echo "🔧 Nginx 시작 중..."
docker compose up -d nginx kibana
echo "✅ Nginx, Kibana 시작 완료"

# 최종 요약
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 모든 서비스가 시작되었습니다!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Portfolio: http://${HOST_IP}:5000"
echo "🔗 Keycloak:  http://${HOST_IP}:8080/admin"
echo "📊 Kibana:    http://${HOST_IP}:5601"
echo ""
echo "👤 관리자: admin / admin123"
echo ""
docker compose ps
