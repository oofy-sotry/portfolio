#!/bin/bash

# Keycloak 사용자 및 데이터베이스 수동 생성/수정 스크립트
# MySQL이 이미 실행 중일 때 사용
# 
# 사용법:
#   bash fix_keycloak_user.sh              # 사용자만 생성/수정
#   bash fix_keycloak_user.sh --reset-db   # 데이터베이스 초기화 (모든 테이블 삭제)

RESET_DB=false
if [ "$1" = "--reset-db" ]; then
    RESET_DB=true
fi

echo "🔧 Keycloak 사용자 및 데이터베이스 생성/수정 중..."

if [ "$RESET_DB" = true ]; then
    echo "⚠️  데이터베이스 초기화 모드: 데이터베이스를 완전히 삭제하고 재생성합니다..."
    
    # Keycloak이 실행 중이면 먼저 중지 (데이터베이스 삭제를 위해)
    if docker compose ps keycloak 2>/dev/null | grep -q "Up"; then
        echo "   Keycloak이 실행 중입니다. 데이터베이스 초기화를 위해 중지합니다..."
        docker compose stop keycloak
        sleep 3
    fi
    
    # 데이터베이스 완전 삭제 및 재생성 (가장 확실한 방법)
    echo "   데이터베이스 삭제 및 재생성 중..."
    
    # 데이터베이스 삭제 및 재생성
    docker compose exec -T db mysql -u root -ppassword <<EOF
-- Keycloak 데이터베이스 완전 삭제
DROP DATABASE IF EXISTS keycloak;

-- 새로 생성
CREATE DATABASE keycloak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 확인
SHOW DATABASES LIKE 'keycloak';
EOF
    
    if [ $? -eq 0 ]; then
        echo "✅ Keycloak 데이터베이스 초기화 완료"
        echo "   데이터베이스가 완전히 삭제되고 재생성되었습니다."
        echo "   Liquibase 변경 로그도 모두 제거되었습니다."
    else
        echo "❌ 데이터베이스 초기화 실패"
        echo "   수동으로 다음 명령어를 실행해보세요:"
        echo "   docker compose exec db mysql -u root -ppassword -e 'DROP DATABASE IF EXISTS keycloak; CREATE DATABASE keycloak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'"
        exit 1
    fi
fi

docker compose exec -T db mysql -u root -ppassword <<EOF
-- Keycloak 데이터베이스 생성 (없는 경우)
CREATE DATABASE IF NOT EXISTS keycloak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 기존 사용자 삭제 (있다면)
DROP USER IF EXISTS 'keycloak'@'%';
DROP USER IF EXISTS 'keycloak'@'localhost';

-- Keycloak 사용자 생성 (비밀번호 명시)
CREATE USER 'keycloak'@'%' IDENTIFIED BY 'keycloak123';

-- 모든 호스트에서 접근 가능하도록 권한 부여
GRANT ALL PRIVILEGES ON keycloak.* TO 'keycloak'@'%';

-- 권한 새로고침
FLUSH PRIVILEGES;

-- 확인
SELECT User, Host FROM mysql.user WHERE User='keycloak';
SHOW DATABASES LIKE 'keycloak';
EOF

if [ $? -eq 0 ]; then
    echo "✅ Keycloak 사용자 및 데이터베이스 생성/수정 완료"
    echo ""
    echo "📋 생성된 내용:"
    echo "   - 데이터베이스: keycloak"
    echo "   - 사용자: keycloak"
    echo "   - 비밀번호: keycloak123"
    echo "   - 호스트: % (모든 호스트)"
    echo ""
    echo "🔍 연결 테스트 중..."
    if docker compose exec -T db mysql -u keycloak -pkeycloak123 -e "USE keycloak; SELECT 1;" 2>&1 | grep -q "1"; then
        echo "✅ Keycloak 사용자 연결 테스트 성공!"
    else
        echo "⚠️ 연결 테스트 실패. 권한을 다시 확인합니다..."
        docker compose exec -T db mysql -u root -ppassword <<EOF
GRANT ALL PRIVILEGES ON keycloak.* TO 'keycloak'@'%';
FLUSH PRIVILEGES;
EOF
    fi
    if [ "${SKIP_RESTART_MSG:-false}" != "true" ]; then
        echo ""
        echo "🚀 이제 Keycloak을 재시작하세요:"
        echo "   docker compose restart keycloak"
    fi
else
    echo "❌ Keycloak 사용자 및 데이터베이스 생성 실패"
    exit 1
fi

