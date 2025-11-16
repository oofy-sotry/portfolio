# 문제 해결 가이드

## 데이터베이스 변경 이력 (MariaDB → MySQL)

### 변경 배경

이 프로젝트는 원래 **MariaDB 10.11**을 사용했습니다. 하지만 Keycloak 24.0과의 호환성 문제로 인해 **MySQL 8.0**으로 변경되었습니다.

### 변경 이유

#### 1. CLOB 타입 호환성 문제 (핵심 원인)

**문제:**
- Keycloak 24.0의 Liquibase changelog가 `PROTOCOL_MAPPER_CONFIG` 테이블을 생성할 때 `VALUE CLOB` 타입을 사용
- **MariaDB 10.11.14는 `CLOB` 타입을 지원하지 않음**
- MariaDB는 `TEXT`, `MEDIUMTEXT`, `LONGTEXT`만 지원

**에러 메시지:**
```
ERROR: You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ' NAME VARCHAR(255) NOT NULL)' at line 1 
[Failed SQL: (1064) CREATE TABLE PROTOCOL_MAPPER_CONFIG (PROTOCOL_MAPPER_ID VARCHAR(36) NOT NULL, VALUE CLOB, NAME VARCHAR(255) NOT NULL)]
```

#### 2. Keycloak 공식 지원 데이터베이스

- Keycloak은 공식적으로 **MySQL 8.0+**를 완전 지원
- MariaDB는 MySQL 호환성을 기반으로 하지만, 일부 타입과 기능에서 차이가 있음
- Keycloak 24.0은 MySQL과의 완벽한 호환성을 보장

#### 3. 해결 방법

**변경 사항:**
- `docker-compose.yml`: `mariadb:10.11` → `mysql:8.0`
- `init_mariadb.sql` → `init_mysql.sql`
- 모든 스크립트 및 문서에서 MySQL로 업데이트

**결과:**
- ✅ CLOB 타입 오류 완전 해결
- ✅ Keycloak 정상 시작
- ✅ 모든 서비스 정상 작동

### 참고사항

- **MariaDB는 여전히 우수한 데이터베이스**이며, 다른 애플리케이션에서는 문제없이 사용 가능
- 이 변경은 **Keycloak 24.0과의 특정 호환성 문제**로 인한 것입니다
- Keycloak의 이전 버전(22.0, 23.0)에서는 MariaDB와 더 나은 호환성을 제공할 수 있습니다

### ⚠️ 중요: 데이터 호환성 문제

**MariaDB에서 MySQL로 변경 시 발생하는 문제:**

MariaDB의 데이터 파일(`ibdata1`)은 MySQL 8.0과 호환되지 않습니다. 다음과 같은 에러가 발생할 수 있습니다:

```
ERROR [MY-012224] [InnoDB] Tablespace flags are invalid in datafile: ./ibdata1, Space ID:0, Flags: 21
ERROR [MY-012237] [InnoDB] Corrupted page [page id: space=0, page number=0] of datafile './ibdata1'
ERROR [MY-012930] [InnoDB] Plugin initialization aborted with error Data structure corruption
ERROR [MY-010020] [Server] Data Dictionary initialization failed
```

**해결 방법:**

기존 MariaDB 볼륨을 완전히 삭제하고 새로 시작해야 합니다:

```bash
# 1. 모든 서비스 중지 및 볼륨 삭제 (⚠️ 모든 데이터가 삭제됩니다!)
docker compose down -v

# 2. MySQL로 재시작
docker compose up -d db

# 3. MySQL이 완전히 시작될 때까지 대기 (약 30초)
# 4. 나머지 서비스 시작
bash scripts/start_service.sh
```

**데이터 백업이 필요한 경우:**

```bash
# 1. MariaDB 데이터 덤프 (변경 전에 실행)
docker compose exec db mysqldump -u root -ppassword --all-databases > mariadb_backup.sql

# 2. 볼륨 삭제 및 MySQL로 재시작
docker compose down -v
docker compose up -d db

# 3. MySQL이 시작된 후 데이터 복원 (스키마 호환성 확인 필요)
docker compose exec -T db mysql -u root -ppassword < mariadb_backup.sql
```

**주의사항:**
- MariaDB와 MySQL은 대부분 호환되지만, 일부 데이터 타입과 기능에서 차이가 있을 수 있습니다
- 중요한 데이터가 있다면 반드시 백업 후 마이그레이션을 진행하세요

## Elasticsearch가 시작되지 않는 경우

### 증상
- Elasticsearch가 60초 이상 준비되지 않음
- `curl http://localhost:9200` 실패

### 원인 및 해결 방법

#### 1. 메모리 부족
**증상**: Elasticsearch 로그에 "heap size" 또는 "memory" 관련 오류

**해결**:
```bash
# 현재 메모리 확인
docker stats elasticsearch

# docker-compose.yml에서 메모리 설정 확인
# ES_JAVA_OPTS=-Xms512m -Xmx512m (최소 512MB 필요)
```

**Windows에서 해결**:
- Docker Desktop 설정에서 메모리 할당량 증가 (최소 2GB 권장)
- Docker Desktop > Settings > Resources > Memory

#### 2. 포트 충돌
**증상**: "port 9200 is already in use" 오류

**해결**:
```bash
# 포트 사용 확인 (Windows)
netstat -ano | findstr :9200

# 포트 사용 확인 (Linux/Mac)
lsof -i :9200

# 충돌하는 프로세스 종료
```

#### 3. 볼륨 권한 문제
**증상**: Elasticsearch 로그에 "permission denied" 오류

**해결**:
```bash
# 볼륨 삭제 후 재생성
docker compose down -v
docker compose up -d elasticsearch
```

#### 4. 로그 확인
```bash
# Elasticsearch 로그 확인
docker compose logs -f elasticsearch

# 마지막 100줄만 확인
docker compose logs --tail=100 elasticsearch
```

## Keycloak이 시작되지 않는 경우

### 증상
- Keycloak이 90초 이상 준비되지 않음
- `curl http://localhost:8080/realms/master` 실패

### 원인 및 해결 방법

#### 1. MySQL 연결 실패
**증상**: Keycloak 로그에 "database connection" 또는 "JDBC" 관련 오류

**해결**:
```bash
# MySQL이 실행 중인지 확인
docker compose ps db

# MySQL 연결 테스트
docker compose exec db mysql -u keycloak -pkeycloak123 -e "SHOW DATABASES;"

# keycloak 데이터베이스가 존재하는지 확인
docker compose exec db mysql -u root -ppassword -e "SHOW DATABASES LIKE 'keycloak';"

# keycloak 사용자가 존재하는지 확인
docker compose exec db mysql -u root -ppassword -e "SELECT User, Host FROM mysql.user WHERE User='keycloak';"
```

**데이터베이스 재생성**:
```bash
# 기존 데이터베이스 삭제 후 재생성
docker compose down
docker volume rm portfolio_website_db_data
docker compose up -d db
# DB가 완전히 시작될 때까지 대기 (약 30초)
docker compose up -d keycloak
```

**MariaDB에서 MySQL로 변경한 경우 (데이터 호환성 문제)**:
```bash
# ⚠️ 주의: MariaDB 볼륨은 MySQL과 호환되지 않습니다!
# 반드시 볼륨을 삭제하고 새로 시작해야 합니다

# 1. 모든 서비스 중지 및 볼륨 삭제
docker compose down -v

# 2. MySQL로 재시작
docker compose up -d db

# 3. MySQL이 완전히 시작될 때까지 대기 (약 30초)
# 4. 나머지 서비스 시작
bash scripts/start_service.sh
```

#### 2. Keycloak 초기화 시간 부족
**증상**: 프로덕션 모드(`start`)는 초기화에 더 오래 걸림

**해결**:
- 대기 시간을 180초로 증가 (이미 적용됨)
- 로그를 확인하여 실제 진행 상황 확인

#### 3. 포트 충돌
**증상**: "port 8080 is already in use" 오류

**해결**:
```bash
# 포트 사용 확인 (Windows)
netstat -ano | findstr :8080

# 포트 사용 확인 (Linux/Mac)
lsof -i :8080
```

#### 4. 로그 확인
```bash
# Keycloak 로그 확인
docker compose logs -f keycloak

# 마지막 100줄만 확인
docker compose logs --tail=100 keycloak

# 특정 오류 검색
docker compose logs keycloak | grep -i error
```

## 일반적인 문제 해결

### 서비스 상태 확인
```bash
# 모든 서비스 상태 확인
docker compose ps

# 특정 서비스 상태 확인
docker compose ps keycloak
docker compose ps elasticsearch
docker compose ps db
```

### 서비스 재시작
```bash
# 특정 서비스만 재시작
docker compose restart keycloak
docker compose restart elasticsearch

# 모든 서비스 재시작
docker compose restart
```

### 완전히 재시작 (데이터 유지)
```bash
# 서비스 중지
docker compose down

# 서비스 시작
docker compose up -d
```

### 완전히 재시작 (데이터 삭제)
```bash
# ⚠️ 주의: 모든 데이터가 삭제됩니다!
docker compose down -v
docker compose up -d
```

### 리소스 확인
```bash
# 컨테이너 리소스 사용량 확인
docker stats

# 특정 컨테이너만 확인
docker stats keycloak elasticsearch db
```

## Windows 특화 문제

### curl 명령어 없음
**해결**: 
- PowerShell에서 `Invoke-WebRequest` 사용
- 또는 Git Bash 사용
- 또는 Docker 컨테이너 내부에서 확인:
  ```bash
  docker compose exec keycloak curl http://localhost:8080/realms/master
  ```

### IP 주소 감지 실패
**증상**: `hostname -I`가 작동하지 않음

**해결**: 스크립트에 대체 방법이 포함되어 있음
- `ip route get 8.8.8.8` 사용
- 또는 수동으로 `.env` 파일에 IP 설정

### 경로 문제
**증상**: 스크립트 실행 시 경로 오류

**해결**:
```bash
# Git Bash 사용
bash scripts/start_service.sh

# 또는 PowerShell에서
bash.exe scripts/start_service.sh
```

## 로그 분석 팁

### Keycloak 로그에서 확인할 내용
- "Database connection" 관련 메시지
- "Started" 메시지 (시작 완료)
- "ERROR" 또는 "WARN" 메시지

### Elasticsearch 로그에서 확인할 내용
- "started" 메시지 (시작 완료)
- "heap size" 관련 메시지 (메모리 문제)
- "permission denied" (권한 문제)

## 빠른 진단 명령어

```bash
# 모든 서비스 상태 및 로그 한 번에 확인
docker compose ps && echo "=== Keycloak Logs ===" && docker compose logs --tail=20 keycloak && echo "=== Elasticsearch Logs ===" && docker compose logs --tail=20 elasticsearch

# MySQL 연결 테스트
docker compose exec db mysql -u root -ppassword -e "SELECT 1;"

# Elasticsearch 헬스 체크
docker compose exec elasticsearch curl -s http://localhost:9200/_cluster/health

# Keycloak 헬스 체크
curl -s http://localhost:8080/realms/master
```

