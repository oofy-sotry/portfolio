# Keycloak 에러 상세 분석

## 📊 확인된 실제 서버 상태

### 데이터베이스 정보
- **MariaDB 버전**: 10.11.14-MariaDB-ubu2204
- **Keycloak 데이터베이스**: 존재함
- **테이블 개수**: 35개
- **Liquibase 상태**: `DATABASECHANGELOG` 테이블 존재 (이미 일부 changeset 실행됨)

### 존재하는 주요 테이블
- `PROTOCOL_MAPPER` ✅ (이미 존재)
- `DATABASECHANGELOG` ✅ (Liquibase changelog 기록)
- `DATABASECHANGELOGLOCK` ✅ (Liquibase 잠금)
- 기타 32개 테이블

## 🔍 정확한 문제 분석

### 문제 1: CLOB 타입 호환성 문제 (핵심 원인)

**에러 메시지:**
```
ERROR: You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ' NAME VARCHAR(255) NOT NULL)' at line 1 
[Failed SQL: (1064) CREATE TABLE PROTOCOL_MAPPER_CONFIG (PROTOCOL_MAPPER_ID VARCHAR(36) NOT NULL, VALUE CLOB, NAME VARCHAR(255) NOT NULL)]
```

**원인:**
1. Keycloak 24.0의 Liquibase changelog가 `PROTOCOL_MAPPER_CONFIG` 테이블을 생성할 때 `VALUE CLOB` 타입을 사용
2. MariaDB 10.11.14는 `CLOB` 타입을 지원하지 않음
3. MariaDB는 `TEXT`, `MEDIUMTEXT`, `LONGTEXT`만 지원

**영향:**
- `PROTOCOL_MAPPER_CONFIG` 테이블 생성 실패
- Keycloak 시작 불가

### 문제 2: Liquibase Changelog 불일치 (부수적 문제)

**상황:**
- `DATABASECHANGELOG` 테이블이 존재하고 일부 changeset이 이미 실행됨
- `PROTOCOL_MAPPER` 테이블은 이미 존재
- 하지만 `PROTOCOL_MAPPER_CONFIG` 테이블은 생성되지 않음

**원인:**
1. 이전에 Keycloak이 부분적으로 시작되어 일부 테이블 생성
2. `PROTOCOL_MAPPER_CONFIG` 테이블 생성 시 CLOB 에러로 실패
3. Liquibase changelog에는 일부 changeset이 기록되어 있지만, 실제 테이블 상태는 불완전

**영향:**
- Liquibase가 `PROTOCOL_MAPPER` 테이블을 다시 생성하려고 시도 → "already exists" 에러
- 데이터베이스 상태와 changelog 불일치

## 🎯 근본 원인

### 1차 원인: MariaDB와 Keycloak의 타입 호환성 문제

**기술적 세부사항:**
- Keycloak 24.0은 MySQL 8.0+를 공식 지원
- MariaDB는 MySQL과 호환되지만, 일부 타입에서 차이가 있음
- `CLOB` 타입은 Oracle/PostgreSQL 표준이며, MySQL/MariaDB에서는 지원하지 않음
- Keycloak의 일부 버전에서 MariaDB와 완벽하게 호환되지 않을 수 있음

### 2차 원인: 불완전한 데이터베이스 초기화

**발생 과정:**
1. Keycloak 시작 → Liquibase가 데이터베이스 업데이트 시작
2. 일부 테이블 생성 성공 (`PROTOCOL_MAPPER` 등)
3. `PROTOCOL_MAPPER_CONFIG` 테이블 생성 시도 → CLOB 에러 발생
4. Keycloak 시작 실패
5. 데이터베이스는 부분적으로 초기화된 상태로 남음
6. 재시작 시 Liquibase changelog와 실제 테이블 상태 불일치

## 💡 해결 방법

### 방법 1: MySQL로 변경 (가장 확실한 해결책) ⭐

**장점:**
- Keycloak 공식 지원 데이터베이스
- CLOB 타입 문제 완전 해결
- 완벽한 호환성 보장
- 장기적 안정성

**단점:**
- 기존 MariaDB 데이터 마이그레이션 필요
- 설정 변경 필요

**구현:**
```yaml
# docker-compose.yml
db:
  image: mysql:8.0  # MariaDB 대신 MySQL 사용
  # 나머지 설정은 동일
```

### 방법 2: 데이터베이스 완전 초기화 후 Keycloak 버전 조정

**단계:**
1. Keycloak 데이터베이스 완전 삭제
2. Liquibase changelog 완전 제거
3. Keycloak 버전을 22.0 또는 23.0으로 다운그레이드 (MariaDB 호환성 개선)
4. 재시작

**장점:**
- MariaDB 유지 가능
- 기존 설정 유지

**단점:**
- 근본 원인 해결 안 됨
- 재발 가능성

### 방법 3: 데이터베이스 완전 초기화 후 재시작 (임시 해결책)

**단계:**
1. Keycloak 완전 중지
2. 데이터베이스 완전 삭제 및 재생성
3. Liquibase changelog 완전 제거
4. Keycloak 재시작

**장점:**
- 빠른 해결
- 기존 설정 유지

**단점:**
- 근본 원인 해결 안 됨
- 재발 가능성 높음

## 🎯 권장 해결책

### 즉시 해결 (임시)

```bash
# 1. Keycloak 중지
docker compose stop keycloak

# 2. 데이터베이스 완전 초기화
docker compose exec db mysql -u root -ppassword <<EOF
DROP DATABASE IF EXISTS keycloak;
CREATE DATABASE keycloak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

# 3. 사용자 재생성
bash scripts/fix_keycloak_user.sh

# 4. Keycloak 재시작
docker compose up -d keycloak
```

**주의:** 이 방법은 CLOB 문제를 해결하지 못하므로, 여전히 실패할 가능성이 높습니다.

### 근본 해결 (권장)

**MariaDB를 MySQL로 변경:**

1. `docker-compose.yml` 수정:
```yaml
db:
  image: mysql:8.0  # mariadb:10.11 → mysql:8.0
  # 나머지 설정은 동일
```

2. 데이터베이스 마이그레이션 (선택사항):
   - 기존 데이터가 중요하지 않다면 데이터베이스 완전 초기화
   - 기존 데이터가 중요하다면 마이그레이션 도구 사용

3. 서비스 재시작:
```bash
docker compose down -v  # 볼륨도 삭제 (데이터 초기화)
docker compose up -d
```

## 📝 확인 사항

현재 상태에서 다음을 확인할 수 있습니다:

```bash
# PROTOCOL_MAPPER_CONFIG 테이블 존재 여부 확인
docker compose exec db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES LIKE 'PROTOCOL_MAPPER%';"

# Liquibase changelog 상태 확인
docker compose exec db mysql -u root -ppassword -e "USE keycloak; SELECT id, author, filename, exectype FROM DATABASECHANGELOG WHERE id LIKE '%PROTOCOL_MAPPER%';"

# Keycloak 버전 확인
docker compose exec keycloak /opt/keycloak/bin/kc.sh --version
```

## 🔄 다음 단계

1. **즉시**: 데이터베이스 완전 초기화 시도 (임시 해결)
2. **단기**: MariaDB를 MySQL로 변경 (근본 해결)
3. **장기**: Keycloak과 데이터베이스 버전 호환성 정기 확인

## ⚠️ 중요 참고사항

- **MariaDB 10.11.14**는 `CLOB` 타입을 지원하지 않습니다
- **Keycloak 24.0**은 MySQL 8.0+를 공식 지원하며, MariaDB는 제한적 지원입니다
- 데이터베이스를 완전히 초기화해도 CLOB 문제는 해결되지 않습니다
- **MySQL로 변경하는 것이 가장 확실한 해결책**입니다

