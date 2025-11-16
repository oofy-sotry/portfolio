#!/bin/bash

# ⚠️ 주의: 이 스크립트는 현재 사용되지 않습니다.
# setup_keycloak.py가 이미 모든 Keycloak 설정을 처리합니다.
# 수동으로 Keycloak Client 설정을 업데이트할 때만 사용하세요.

# 현재 시스템의 IP 주소 자동 감지
HOST_IP=$(hostname -I | awk '{print $1}')
PORTFOLIO_URL="http://${HOST_IP}:5000"
KEYCLOAK_URL="http://${HOST_IP}:8080"

echo "🔧 Keycloak Client 설정 업데이트"
echo "📍 감지된 IP: ${HOST_IP}"
echo "🌐 Portfolio URL: ${PORTFOLIO_URL}"
echo "🔗 Keycloak URL: ${KEYCLOAK_URL}"

# Keycloak 관리자 인증
echo "🔐 Keycloak 관리자 인증 중..."
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin --password admin123

if [ $? -ne 0 ]; then
    echo "❌ Keycloak 관리자 인증 실패"
    exit 1
fi

echo "✅ Keycloak 관리자 인증 성공"

# Client 설정 업데이트
echo "⚙️ portfolio-web 클라이언트 설정 업데이트 중..."

# Valid Redirect URIs 업데이트
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh update clients/$(docker compose exec keycloak /opt/keycloak/bin/kcadm.sh get clients -r portfolio --fields id,clientId | grep -A1 '"clientId" : "portfolio-web"' | grep '"id"' | cut -d'"' -f4) -r portfolio -s "redirectUris=[\"${PORTFOLIO_URL}/auth/keycloak-callback\"]"

# Web Origins 업데이트
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh update clients/$(docker compose exec keycloak /opt/keycloak/bin/kcadm.sh get clients -r portfolio --fields id,clientId | grep -A1 '"clientId" : "portfolio-web"' | grep '"id"' | cut -d'"' -f4) -r portfolio -s "webOrigins=[\"${PORTFOLIO_URL}\"]"

# Root URL 업데이트
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh update clients/$(docker compose exec keycloak /opt/keycloak/bin/kcadm.sh get clients -r portfolio --fields id,clientId | grep -A1 '"clientId" : "portfolio-web"' | grep '"id"' | cut -d'"' -f4) -r portfolio -s "rootUrl=${PORTFOLIO_URL}"

echo "✅ Keycloak Client 설정 업데이트 완료!"
echo ""
echo "📋 설정된 값들:"
echo "   - Valid Redirect URIs: ${PORTFOLIO_URL}/auth/keycloak-callback"
echo "   - Web Origins: ${PORTFOLIO_URL}"
echo "   - Root URL: ${PORTFOLIO_URL}"
echo ""
echo "🚀 이제 Keycloak 로그인을 테스트해보세요!"

