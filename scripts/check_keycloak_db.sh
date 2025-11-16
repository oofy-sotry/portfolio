#!/bin/bash

# Keycloak 데이터베이스 상태 확인 스크립트

echo "🔍 Keycloak 데이터베이스 상태 확인 중..."
echo ""

# 1. 데이터베이스 존재 확인
echo "1️⃣ 데이터베이스 존재 여부:"
DB_EXISTS=$(docker compose exec -T db mysql -u root -ppassword -e "SHOW DATABASES LIKE 'keycloak';" 2>/dev/null | grep -c "keycloak" || echo "0")
if [ "$DB_EXISTS" -gt 0 ]; then
    echo "   ✅ keycloak 데이터베이스가 존재합니다."
else
    echo "   ❌ keycloak 데이터베이스가 없습니다."
    exit 0
fi

# 2. 테이블 개수 확인
echo ""
echo "2️⃣ 테이블 개수:"
TABLE_COUNT=$(docker compose exec -T db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES;" 2>/dev/null | grep -v "Tables_in_keycloak" | grep -v "^$" | wc -l)
echo "   테이블 개수: $TABLE_COUNT"

if [ "$TABLE_COUNT" -gt 0 ]; then
    echo "   ⚠️  테이블이 존재합니다. 목록:"
    docker compose exec -T db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES;" 2>/dev/null | grep -v "Tables_in_keycloak" | grep -v "^$" | head -10
    if [ "$TABLE_COUNT" -gt 10 ]; then
        echo "   ... (총 $TABLE_COUNT개)"
    fi
else
    echo "   ✅ 데이터베이스가 비어있습니다."
fi

# 3. Liquibase 변경 로그 확인
echo ""
echo "3️⃣ Liquibase 변경 로그:"
LIQUIBASE_TABLES=$(docker compose exec -T db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES LIKE 'DATABASECHANGELOG%';" 2>/dev/null | grep -v "Tables_in_keycloak" | grep -v "^$" | wc -l)
if [ "$LIQUIBASE_TABLES" -gt 0 ]; then
    echo "   ⚠️  Liquibase 변경 로그 테이블이 존재합니다 ($LIQUIBASE_TABLES개)"
    docker compose exec -T db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES LIKE 'DATABASECHANGELOG%';" 2>/dev/null | grep -v "Tables_in_keycloak" | grep -v "^$"
else
    echo "   ✅ Liquibase 변경 로그 테이블이 없습니다."
fi

# 4. 사용자 확인
echo ""
echo "4️⃣ Keycloak 사용자 확인:"
USER_EXISTS=$(docker compose exec -T db mysql -u root -ppassword -e "SELECT User, Host FROM mysql.user WHERE User='keycloak';" 2>/dev/null | grep -c "keycloak" || echo "0")
if [ "$USER_EXISTS" -gt 0 ]; then
    echo "   ✅ keycloak 사용자가 존재합니다."
    docker compose exec -T db mysql -u root -ppassword -e "SELECT User, Host FROM mysql.user WHERE User='keycloak';" 2>/dev/null | grep "keycloak"
else
    echo "   ❌ keycloak 사용자가 없습니다."
fi

# 5. 연결 테스트
echo ""
echo "5️⃣ 사용자 연결 테스트:"
if docker compose exec -T db mysql -u keycloak -pkeycloak123 -e "USE keycloak; SELECT 1;" 2>&1 | grep -q "1"; then
    echo "   ✅ keycloak 사용자로 연결 성공"
else
    echo "   ❌ keycloak 사용자로 연결 실패"
    docker compose exec -T db mysql -u keycloak -pkeycloak123 -e "USE keycloak; SELECT 1;" 2>&1 | head -3
fi

# 6. Keycloak 컨테이너 상태
echo ""
echo "6️⃣ Keycloak 컨테이너 상태:"
if docker compose ps keycloak 2>/dev/null | grep -q "Up"; then
    echo "   ✅ Keycloak이 실행 중입니다."
    echo "   상태:"
    docker compose ps keycloak 2>/dev/null | grep keycloak
else
    echo "   ⚠️  Keycloak이 실행되지 않았습니다."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 요약:"
echo "   - 데이터베이스 존재: $([ "$DB_EXISTS" -gt 0 ] && echo "예" || echo "아니오")"
echo "   - 테이블 개수: $TABLE_COUNT"
echo "   - Liquibase 로그: $([ "$LIQUIBASE_TABLES" -gt 0 ] && echo "존재" || echo "없음")"
echo "   - 사용자 존재: $([ "$USER_EXISTS" -gt 0 ] && echo "예" || echo "아니오")"
echo ""

if [ "$TABLE_COUNT" -gt 0 ]; then
    echo "⚠️  데이터베이스에 테이블이 있습니다. 초기화가 필요할 수 있습니다."
    echo "   실행: bash scripts/fix_keycloak_user.sh --reset-db"
fi

