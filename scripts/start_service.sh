#!/bin/bash

# set -e는 주석 처리 (에러 발생 시에도 계속 진행하여 진단 정보 제공)
# set -e  # 에러 발생 시 스크립트 중단

# 스크립트가 있는 디렉토리 찾기
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 프로젝트 루트 디렉토리 (scripts의 상위 디렉토리)
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# 프로젝트 루트로 이동
cd "${PROJECT_ROOT}" || {
    echo "❌ 프로젝트 루트 디렉토리로 이동할 수 없습니다."
    exit 1
}

echo "🚀 Portfolio 웹사이트 시작 중..."
echo "📁 작업 디렉토리: ${PROJECT_ROOT}"

# 현재 IP 감지
HOST_IP=$(hostname -I | awk '{print $1}')
if [ -z "$HOST_IP" ]; then
    # hostname -I가 실패한 경우 대체 방법
    HOST_IP=$(ip route get 8.8.8.8 2>/dev/null | awk '{print $7; exit}' || echo "localhost")
fi
echo "📍 감지된 IP: ${HOST_IP}"

# 0. .env 파일 확인 및 생성
echo "🔍 환경 설정 파일 확인 중..."
if [ ! -f ".env" ]; then
    echo "📝 .env 파일이 없습니다. 생성 중..."
    if [ -f "scripts/setup_env.sh" ]; then
        bash scripts/setup_env.sh
    else
        # 기본 .env 파일 생성
        cat > .env << EOF
# 자동 생성된 환경 설정
KEYCLOAK_URL=http://${HOST_IP}:8080
KEYCLOAK_REALM=portfolio
KEYCLOAK_CLIENT_ID=portfolio-web
KEYCLOAK_CLIENT_SECRET=temp-secret-will-be-updated

# 데이터베이스 설정
DATABASE_URL=mysql+pymysql://root:password@db:3306/portfolio_db

# Flask 설정
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=production
ELASTICSEARCH_URL=http://elasticsearch:9200
EOF
        echo "✅ 기본 .env 파일 생성 완료"
    fi
else
    echo "✅ .env 파일이 이미 존재합니다."
fi

# 1. 기존 서비스 확인 및 정리
echo ""
echo "🔍 기존 서비스 상태 확인 중..."
RUNNING_SERVICES=$(docker compose ps --services --filter "status=running" 2>/dev/null | wc -l)

if [ "$RUNNING_SERVICES" -gt 0 ]; then
    echo "🧹 실행 중인 서비스 발견. 정리 중..."
    docker compose down
    echo "✅ 기존 서비스 정리 완료"
else
    echo "ℹ️ 실행 중인 서비스가 없습니다."
fi

# 2. 인프라 서비스 시작 (DB, Elasticsearch만 먼저 시작, Keycloak은 나중에)
echo ""
echo "📦 인프라 서비스 시작 중 (DB, Elasticsearch)..."
docker compose up -d db elasticsearch

# 서비스 시작 상태 확인
echo ""
echo "🔍 서비스 시작 상태 확인 중..."
sleep 3
docker compose ps db elasticsearch

# 3. MySQL 준비 대기
echo ""
echo "⏳ MySQL 서비스 준비 대기 중..."
MAX_WAIT=60
WAIT_COUNT=0
while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if docker compose exec -T db mysqladmin ping -h localhost -u root -ppassword --silent 2>/dev/null; then
        echo "✅ MySQL이 준비되었습니다."
        break
    fi
    WAIT_COUNT=$((WAIT_COUNT + 5))
    echo "   대기 중... (${WAIT_COUNT}초 / ${MAX_WAIT}초)"
    sleep 5
done

if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
    echo "❌ MySQL이 준비되지 않았습니다. 타임아웃."
    exit 1
fi

# MySQL 초기화 확인 및 사용자 생성
echo ""
echo "🔍 MySQL 초기화 확인 중..."

# 스크립트 경로 확인 (start_service.sh가 scripts/ 또는 루트에서 실행될 수 있음)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FIX_KEYCLOAK_SCRIPT="$PROJECT_ROOT/scripts/fix_keycloak_user.sh"

# fix_keycloak_user.sh 스크립트 사용 (코드 중복 제거)
if [ -f "$FIX_KEYCLOAK_SCRIPT" ]; then
    # MySQL이 완전히 준비될 때까지 추가 대기
    echo "   MySQL 연결 확인 중..."
    MAX_RETRIES=12
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if docker compose exec -T db mysqladmin ping -h localhost -u root -ppassword --silent 2>/dev/null; then
            echo "   ✅ MySQL 연결 성공"
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "   MySQL 대기 중... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done
    
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ MySQL 연결 실패. MySQL이 준비될 때까지 더 기다려주세요."
        exit 1
    fi
    
    # Keycloak 데이터베이스 존재 여부 및 테이블 확인
    DB_EXISTS=$(docker compose exec -T db mysql -u root -ppassword -e "SHOW DATABASES LIKE 'keycloak';" 2>/dev/null | grep -c "keycloak" || echo "0")
    # 공백 제거 및 정수로 변환
    DB_EXISTS=$(echo "$DB_EXISTS" | tr -d '[:space:]')
    DB_EXISTS=${DB_EXISTS:-0}
    
    if [ "$DB_EXISTS" -gt 0 ] 2>/dev/null; then
        # 데이터베이스가 존재하면 테이블 확인
        HAS_TABLES=$(docker compose exec -T db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES;" 2>/dev/null | grep -v "Tables_in_keycloak" | grep -v "^$" | wc -l)
        # 공백 제거 및 정수로 변환
        HAS_TABLES=$(echo "$HAS_TABLES" | tr -d '[:space:]')
        HAS_TABLES=${HAS_TABLES:-0}
        
        if [ "$HAS_TABLES" -gt 0 ] 2>/dev/null; then
            echo "⚠️  Keycloak 데이터베이스에 기존 테이블이 있습니다 ($HAS_TABLES개). 초기화합니다..."
            # Keycloak이 실행 중이면 먼저 중지
            if docker compose ps keycloak 2>/dev/null | grep -q "Up"; then
                echo "   Keycloak 중지 중..."
                docker compose stop keycloak
                sleep 2
            fi
            # 데이터베이스 초기화 모드로 실행 (데이터베이스 완전 삭제 및 재생성)
            SKIP_RESTART_MSG=true bash "$FIX_KEYCLOAK_SCRIPT" --reset-db
            if [ $? -ne 0 ]; then
                echo "❌ Keycloak 데이터베이스 초기화 실패"
                exit 1
            fi
        else
            echo "✅ Keycloak 데이터베이스가 비어있습니다. 사용자만 생성합니다..."
            # 일반 모드로 실행 (사용자만 생성)
            SKIP_RESTART_MSG=true bash "$FIX_KEYCLOAK_SCRIPT"
            if [ $? -ne 0 ]; then
                echo "❌ Keycloak 사용자 생성 실패"
                exit 1
            fi
        fi
    else
        echo "✅ Keycloak 데이터베이스가 없습니다. 생성합니다..."
        # 일반 모드로 실행 (데이터베이스 및 사용자 생성)
        SKIP_RESTART_MSG=true bash "$FIX_KEYCLOAK_SCRIPT"
        if [ $? -ne 0 ]; then
            echo "❌ Keycloak 사용자 생성 실패"
            exit 1
        fi
    fi
else
    echo "⚠️ fix_keycloak_user.sh를 찾을 수 없습니다. 직접 생성합니다..."
    # fallback: 직접 생성 (스크립트가 없을 경우)
    # MySQL이 완전히 준비될 때까지 추가 대기
    echo "   MySQL 연결 확인 중..."
    MAX_RETRIES=12
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if docker compose exec -T db mysqladmin ping -h localhost -u root -ppassword --silent 2>/dev/null; then
            echo "   ✅ MySQL 연결 성공"
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "   MySQL 대기 중... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done
    
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ MySQL 연결 실패. MySQL이 준비될 때까지 더 기다려주세요."
        exit 1
    fi
    
    # Keycloak 데이터베이스 존재 여부 및 테이블 확인
    DB_EXISTS=$(docker compose exec -T db mysql -u root -ppassword -e "SHOW DATABASES LIKE 'keycloak';" 2>/dev/null | grep -c "keycloak" || echo "0")
    # 공백 제거 및 정수로 변환
    DB_EXISTS=$(echo "$DB_EXISTS" | tr -d '[:space:]')
    DB_EXISTS=${DB_EXISTS:-0}
    
    if [ "$DB_EXISTS" -gt 0 ] 2>/dev/null; then
        # 데이터베이스가 존재하면 테이블 확인
        HAS_TABLES=$(docker compose exec -T db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES;" 2>/dev/null | grep -v "Tables_in_keycloak" | grep -v "^$" | wc -l)
        # 공백 제거 및 정수로 변환
        HAS_TABLES=$(echo "$HAS_TABLES" | tr -d '[:space:]')
        HAS_TABLES=${HAS_TABLES:-0}
        
        if [ "$HAS_TABLES" -gt 0 ] 2>/dev/null; then
            echo "⚠️  Keycloak 데이터베이스에 기존 테이블이 있습니다 ($HAS_TABLES개). 초기화합니다..."
            # Keycloak 중지
            docker compose stop keycloak 2>/dev/null
            sleep 2
            # 데이터베이스 완전 삭제 및 재생성
            docker compose exec -T db mysql -u root -ppassword <<EOF
DROP DATABASE IF EXISTS keycloak;
CREATE DATABASE keycloak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF
        fi
    fi
    
    docker compose exec -T db mysql -u root -ppassword <<EOF
CREATE DATABASE IF NOT EXISTS keycloak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
DROP USER IF EXISTS 'keycloak'@'%';
DROP USER IF EXISTS 'keycloak'@'localhost';
CREATE USER 'keycloak'@'%' IDENTIFIED BY 'keycloak123';
GRANT ALL PRIVILEGES ON keycloak.* TO 'keycloak'@'%';
FLUSH PRIVILEGES;
EOF
    if [ $? -ne 0 ]; then
        echo "❌ Keycloak 사용자 생성 실패"
        exit 1
    fi
fi

# 4. Elasticsearch 준비 대기
echo ""
echo "⏳ Elasticsearch 서비스 준비 대기 중..."
MAX_WAIT=120
WAIT_COUNT=0
ES_READY=false

# Elasticsearch 컨테이너 상태 확인
if ! docker compose ps elasticsearch | grep -q "Up"; then
    echo "⚠️ Elasticsearch 컨테이너가 실행되지 않았습니다."
    echo "📋 Elasticsearch 로그 확인 중..."
    docker compose logs --tail=50 elasticsearch
fi

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    # curl 대신 docker exec로 확인 (Windows 호환성)
    if docker compose exec -T elasticsearch curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1 || \
       curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        echo "✅ Elasticsearch가 준비되었습니다."
        ES_READY=true
        break
    fi
    WAIT_COUNT=$((WAIT_COUNT + 5))
    echo "   대기 중... (${WAIT_COUNT}초 / ${MAX_WAIT}초)"
    sleep 5
done

if [ "$ES_READY" = false ]; then
    echo "⚠️ Elasticsearch가 준비되지 않았습니다."
    echo "📋 Elasticsearch 로그 (마지막 50줄):"
    docker compose logs --tail=50 elasticsearch
    echo ""
    echo "💡 가능한 원인:"
    echo "   - 메모리 부족 (최소 512MB 필요)"
    echo "   - 포트 9200 충돌"
    echo "   - 볼륨 권한 문제"
    echo ""
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 5. Keycloak 시작 전 최종 확인 및 시작 (데이터베이스 초기화 후)
echo ""
echo "🔍 Keycloak 시작 전 최종 확인 중..."

# Keycloak이 실행 중이면 중지 (데이터베이스 초기화를 위해)
if docker compose ps keycloak 2>/dev/null | grep -q "Up"; then
    echo "   Keycloak이 실행 중입니다. 중지합니다..."
    docker compose stop keycloak
    sleep 2
fi

# 데이터베이스가 완전히 비어있는지 최종 확인 (Liquibase changelog 포함)
FINAL_TABLE_COUNT=$(docker compose exec -T db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES;" 2>/dev/null | grep -v "Tables_in_keycloak" | grep -v "^$" | wc -l)
FINAL_DATABASECHANGELOG=$(docker compose exec -T db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES LIKE 'DATABASECHANGELOG%';" 2>/dev/null | grep -v "Tables_in_keycloak" | grep -v "^$" | wc -l)

# 공백 제거 및 정수로 변환
FINAL_TABLE_COUNT=$(echo "$FINAL_TABLE_COUNT" | tr -d '[:space:]')
FINAL_TABLE_COUNT=${FINAL_TABLE_COUNT:-0}
FINAL_DATABASECHANGELOG=$(echo "$FINAL_DATABASECHANGELOG" | tr -d '[:space:]')
FINAL_DATABASECHANGELOG=${FINAL_DATABASECHANGELOG:-0}

if [ "$FINAL_TABLE_COUNT" -gt 0 ] 2>/dev/null || [ "$FINAL_DATABASECHANGELOG" -gt 0 ] 2>/dev/null; then
    echo "⚠️  데이터베이스에 여전히 테이블이 있습니다 (일반 테이블: $FINAL_TABLE_COUNT개, Liquibase: $FINAL_DATABASECHANGELOG개). 강제 초기화합니다..."
    
    # Keycloak 완전 중지
    docker compose stop keycloak 2>/dev/null
    sleep 3
    
    # 데이터베이스 완전 삭제 및 재생성 (가장 확실한 방법)
    echo "   데이터베이스 완전 삭제 중..."
    docker compose exec -T db mysql -u root -ppassword <<EOF
DROP DATABASE IF EXISTS keycloak;
CREATE DATABASE keycloak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF
    
    if [ $? -ne 0 ]; then
        echo "❌ 데이터베이스 강제 초기화 실패"
        exit 1
    fi
    
    # 사용자 재생성
    echo "   사용자 재생성 중..."
    SKIP_RESTART_MSG=true bash "$FIX_KEYCLOAK_SCRIPT"
    if [ $? -ne 0 ]; then
        echo "❌ 사용자 재생성 실패"
        exit 1
    fi
    
    # 최종 확인
    FINAL_CHECK=$(docker compose exec -T db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES;" 2>/dev/null | grep -v "Tables_in_keycloak" | grep -v "^$" | wc -l)
    # 공백 제거 및 정수로 변환
    FINAL_CHECK=$(echo "$FINAL_CHECK" | tr -d '[:space:]')
    FINAL_CHECK=${FINAL_CHECK:-0}
    if [ "$FINAL_CHECK" -gt 0 ] 2>/dev/null; then
        echo "❌ 데이터베이스 초기화 후에도 테이블이 남아있습니다 ($FINAL_CHECK개). 수동으로 확인하세요."
        docker compose exec -T db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES;" 2>&1
        exit 1
    fi
    
    echo "✅ 데이터베이스 강제 초기화 완료"
else
    echo "✅ 데이터베이스가 완전히 비어있습니다."
fi

echo ""
echo "🚀 Keycloak 서비스 시작 중..."
docker compose up -d keycloak

# 6. Keycloak 준비 대기
echo ""
echo "⏳ Keycloak 서비스 준비 대기 중..."
echo "   (MySQL 연동으로 인해 초기 시작에 시간이 걸릴 수 있습니다)"
echo "   (첫 시작 시 데이터베이스 스키마 초기화로 5-10분이 걸릴 수 있습니다)"
MAX_WAIT=600  # 10분으로 증가 (첫 시작 시 스키마 초기화 시간 고려)
WAIT_COUNT=0
KC_READY=false

# Keycloak 컨테이너 상태 확인
if ! docker compose ps keycloak | grep -q "Up"; then
    echo "⚠️ Keycloak 컨테이너가 실행되지 않았습니다."
    echo "📋 Keycloak 로그 확인 중..."
    docker compose logs --tail=50 keycloak
fi

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    # curl로 확인 (Windows에서도 작동)
    if curl -s http://${HOST_IP}:8080/realms/master > /dev/null 2>&1 || \
       curl -s http://localhost:8080/realms/master > /dev/null 2>&1; then
        echo "✅ Keycloak이 준비되었습니다."
        KC_READY=true
        break
    fi
    
    # 로그에서 "Started" 메시지 확인 (더 정확한 준비 상태 확인)
    if docker compose logs keycloak 2>/dev/null | grep -q "Started.*in.*ms"; then
        echo "✅ Keycloak이 시작되었습니다. (로그 확인)"
        # 추가로 5초 대기 후 재확인
        sleep 5
        if curl -s http://${HOST_IP}:8080/realms/master > /dev/null 2>&1 || \
           curl -s http://localhost:8080/realms/master > /dev/null 2>&1; then
            echo "✅ Keycloak이 준비되었습니다."
            KC_READY=true
            break
        fi
    fi
    
    WAIT_COUNT=$((WAIT_COUNT + 10))
    echo "   대기 중... (${WAIT_COUNT}초 / ${MAX_WAIT}초)"
    
    # 30초마다 로그에서 진행 상황 확인
    if [ $((WAIT_COUNT % 30)) -eq 0 ] && [ $WAIT_COUNT -gt 0 ]; then
        echo "   📋 Keycloak 진행 상황 확인 중..."
        # 스키마 초기화 진행 상황 확인
        if docker compose logs keycloak 2>/dev/null | grep -q "Initializing database schema"; then
            echo "   ⏳ 데이터베이스 스키마 초기화 중..."
        fi
        if docker compose logs keycloak 2>/dev/null | grep -q "Updating database"; then
            echo "   ⏳ 데이터베이스 업데이트 중..."
        fi
        docker compose ps keycloak | grep keycloak || true
    fi
    sleep 10
done

if [ "$KC_READY" = false ]; then
    echo "❌ Keycloak이 준비되지 않았습니다."
    echo ""
    echo "📋 Keycloak 로그 (마지막 100줄):"
    docker compose logs --tail=100 keycloak
    echo ""
    echo "📋 MySQL 연결 확인:"
    echo "   - Keycloak 사용자 확인:"
    docker compose exec -T db mysql -u root -ppassword -e "SELECT User, Host FROM mysql.user WHERE User='keycloak';" 2>&1
    echo "   - Keycloak 데이터베이스 확인:"
    docker compose exec -T db mysql -u root -ppassword -e "SHOW DATABASES LIKE 'keycloak';" 2>&1
    echo "   - Keycloak 사용자로 연결 테스트:"
    docker compose exec -T db mysql -u keycloak -pkeycloak123 -e "USE keycloak; SELECT 1;" 2>&1 || echo "   ⚠️ Keycloak 사용자 연결 실패"
    echo ""
    echo "💡 가능한 원인:"
    echo "   - Keycloak 초기화 시간 부족 (첫 시작 시 데이터베이스 스키마 초기화로 5-10분 소요)"
    echo "   - MySQL 연결 실패 (데이터베이스/사용자 확인 필요)"
    echo "   - 포트 8080 충돌"
    echo "   - 메모리 부족"
    echo ""
    echo "🔧 해결 방법:"
    echo "   1. 로그 확인: docker compose logs -f keycloak"
    echo "   2. Keycloak이 계속 실행 중이면 기다려보세요 (스키마 초기화는 시간이 걸립니다)"
    echo "   3. 수동으로 준비 확인: curl http://localhost:8080/realms/master"
    echo "   4. MySQL 확인: docker compose exec db mysql -u root -ppassword -e 'SHOW DATABASES;'"
    echo ""
    echo "⚠️  Keycloak이 아직 초기화 중일 수 있습니다. 로그를 확인하여 진행 상황을 모니터링하세요:"
    echo "   docker compose logs -f keycloak | grep -E '(Started|ERROR|Initializing|Updating)'"
    echo ""
    read -p "계속 진행하시겠습니까? (Keycloak이 준비되지 않아도 다음 단계로 진행) (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    echo "⚠️  Keycloak이 준비되지 않은 상태로 계속 진행합니다..."
fi

# 7. Keycloak 설정 (Client Secret 생성)
echo ""
echo "⚙️ Keycloak 설정 중..."
if python3 setup_keycloak.py; then
    echo "✅ Keycloak 설정 완료"
else
    echo "❌ Keycloak 설정 실패"
    exit 1
fi

# 8. 웹 애플리케이션 시작
echo ""
echo "🌐 웹 애플리케이션 시작 중..."

# cryptography 패키지가 requirements.txt에 있는지 확인
#REQUIREMENTS_FILE="${PROJECT_ROOT}/requirements.txt"
#if [ -f "${REQUIREMENTS_FILE}" ] && grep -q "cryptography" "${REQUIREMENTS_FILE}"; then
#    echo "   cryptography 패키지가 requirements.txt에 있습니다."
#    echo "   웹 컨테이너를 재빌드해야 합니다..."
#    echo "   ⏳ 웹 컨테이너 재빌드 중... (시간이 걸릴 수 있습니다)"
#    docker compose build web
#    if [ $? -ne 0 ]; then
#        echo "⚠️ 웹 컨테이너 재빌드 실패. 기존 이미지로 계속 진행합니다..."
#    else
#        echo "✅ 웹 컨테이너 재빌드 완료"
#    fi
#fi

docker compose up -d web

# 9. 웹 애플리케이션 준비 대기
echo ""
echo "⏳ 웹 애플리케이션 준비 대기 중..."
MAX_WAIT=120  # 2분으로 증가 (cryptography 설치 및 초기화 시간 고려)
WAIT_COUNT=0
WEB_READY=false

# 웹 컨테이너 상태 확인
if ! docker compose ps web | grep -q "Up"; then
    echo "⚠️ 웹 컨테이너가 실행되지 않았습니다."
    echo "📋 웹 컨테이너 로그 확인 중..."
    docker compose logs --tail=50 web
    echo ""
    echo "💡 웹 컨테이너가 시작되지 않았습니다. 로그를 확인하세요:"
    echo "   docker compose logs -f web"
fi

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    # curl로 확인 (Windows에서도 작동)
    if curl -s http://localhost:5000 > /dev/null 2>&1 || \
       curl -s http://127.0.0.1:5000 > /dev/null 2>&1; then
        echo "✅ 웹 애플리케이션이 준비되었습니다."
        WEB_READY=true
        break
    fi
    
    # 컨테이너 내부에서 확인 (더 정확)
    if docker compose exec -T web curl -s http://localhost:5000 > /dev/null 2>&1 2>/dev/null; then
        echo "✅ 웹 애플리케이션이 준비되었습니다. (컨테이너 내부 확인)"
        WEB_READY=true
        break
    fi
    
    WAIT_COUNT=$((WAIT_COUNT + 5))
    echo "   대기 중... (${WAIT_COUNT}초 / ${MAX_WAIT}초)"
    
    # 30초마다 로그 확인
    if [ $((WAIT_COUNT % 30)) -eq 0 ] && [ $WAIT_COUNT -gt 0 ]; then
        echo "   📋 웹 애플리케이션 상태 확인 중..."
        if docker compose ps web | grep -q "Up"; then
            echo "   ✅ 컨테이너 실행 중"
            # 최근 에러 로그 확인
            if docker compose logs web 2>/dev/null | tail -20 | grep -q "ERROR\|Exception\|Traceback"; then
                echo "   ⚠️ 에러 로그 발견. 마지막 10줄:"
                docker compose logs web 2>/dev/null | tail -10
            fi
        else
            echo "   ❌ 컨테이너가 실행되지 않았습니다"
        fi
    fi
    sleep 5
done

if [ "$WEB_READY" = false ]; then
    echo "⚠️ 웹 애플리케이션이 준비되지 않았습니다."
    echo ""
    echo "📋 웹 컨테이너 로그 (마지막 100줄):"
    docker compose logs --tail=100 web
    echo ""
    echo "💡 가능한 원인:"
    echo "   - 웹 애플리케이션 시작 실패"
    echo "   - 데이터베이스 연결 실패 (cryptography 패키지 누락 가능)"
    echo "   - 포트 5000 충돌"
    echo "   - 초기화 스크립트 실패 (init_db.py, download_models.py)"
    echo ""
    echo "🔧 해결 방법:"
    echo "   1. 로그 확인: docker compose logs -f web"
    echo "   2. 컨테이너 재빌드: docker compose build web"
    echo "   3. 컨테이너 재시작: docker compose restart web"
    echo "   4. 상태 확인: bash scripts/check_web_status.sh"
    echo ""
    echo "⚠️ 웹 애플리케이션이 준비되지 않은 상태로 계속 진행합니다..."
fi

# 10. Nginx 시작 (선택사항)
echo ""
echo "🔧 Nginx 서비스 시작 중..."
if docker compose ps nginx > /dev/null 2>&1; then
    docker compose up -d nginx
    echo "✅ Nginx가 시작되었습니다."
else
    echo "ℹ️ Nginx 서비스가 docker-compose.yml에 정의되어 있지 않습니다."
fi

# 11. 초기 데이터 설정 (선택사항)
echo ""
read -p "초기 데이터를 설정하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📊 초기 데이터 설정 중..."
    if docker compose exec -T web python init_data.py 2>/dev/null || python3 init_data.py 2>/dev/null; then
        echo "✅ 초기 데이터 설정 완료"
    else
        echo "⚠️ 초기 데이터 설정 실패 (무시하고 계속 진행)"
    fi
fi

# 12. 환경 변수 확인
echo ""
echo "🔍 환경 변수 확인 중..."
if docker compose exec web env 2>/dev/null | grep KEYCLOAK_CLIENT_SECRET; then
    echo "✅ Keycloak Client Secret이 설정되었습니다."
else
    echo "⚠️ KeyCLOAK_CLIENT_SECRET을 확인할 수 없습니다."
fi

# 13. 서비스 상태 확인
echo ""
echo "📊 서비스 상태 확인 중..."
docker compose ps

# 14. 최종 요약
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 모든 서비스가 시작되었습니다!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Portfolio URL:"
echo "   - 직접 접속: http://${HOST_IP}:5000"
if docker compose ps nginx > /dev/null 2>&1; then
    echo "   - Nginx 프록시: http://${HOST_IP}"
fi
echo ""
echo "🔗 Keycloak 관리 콘솔:"
echo "   - http://${HOST_IP}:8080/admin"
echo ""
echo "👤 테스트 계정:"
echo "   - 관리자: admin / admin123"
echo "   - 일반 사용자: testuser / test123"
echo ""
echo "📊 서비스 모니터링:"
echo "   - 로그 확인: docker compose logs -f [service_name]"
echo "   - 상태 확인: docker compose ps"
echo "   - 리소스 사용량: docker stats"
echo ""
echo "🚀 이제 Portfolio 웹사이트를 사용할 수 있습니다!"
