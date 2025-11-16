# Keycloak 에러 정확한 원인 분석

## 🔍 발견된 에러

### 에러 1: CLOB SQL 구문 오류 (핵심 원인)
```
ERROR: You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ' NAME VARCHAR(255) NOT NULL)' at line 1 
[Failed SQL: (1064) CREATE TABLE PROTOCOL_MAPPER_CONFIG (PROTOCOL_MAPPER_ID VARCHAR(36) NOT NULL, VALUE CLOB, NAME VARCHAR(255) NOT NULL)]
```

### 에러 2: 테이블 이미 존재 (부수적 문제)
```
ERROR: Table 'PROTOCOL_MAPPER' already exists
```

## 🎯 정확한 원인

### 1. **CLOB 타입 호환성 문제 (핵심 원인)**

**문제:**
- Keycloak의 Liquibase changelog가 `CLOB` 타입을 사용합니다
- **MariaDB는 `CLOB` 타입을 지원하지 않습니다**
- MariaDB는 대신 `TEXT`, `MEDIUMTEXT`, `LONGTEXT`를 사용합니다

**영향받는 테이블:**
- `PROTOCOL_MAPPER_CONFIG` 테이블의 `VALUE` 컬럼이 `CLOB` 타입으로 정의됨

**왜 발생하는가:**
1. Keycloak 24.0의 Liquibase changelog (`META-INF/jpa-changelog-1.2.0.Beta1.xml`)가 `CLOB` 타입을 사용
2. MariaDB 10.11이 `CLOB`를 인식하지 못함
3. SQL 구문 오류 발생

### 2. **Liquibase Changelog 불일치 (부수적 문제)**

**문제:**
- Keycloak이 시작할 때 Liquibase가 데이터베이스를 업데이트하려고 시도
- 일부 changeset이 이미 실행되었지만 (`Previously run: 4`), changelog 테이블과 실제 테이블 상태가 불일치
- `PROTOCOL_MAPPER` 테이블이 이미 존재하지만, changelog는 다시 생성하려고 시도

**왜 발생하는가:**
1. 이전에 Keycloak이 부분적으로 시작되어 일부 테이블 생성
2. 에러로 인해 중단됨
3. 데이터베이스 초기화가 완전히 되지 않아 changelog 테이블과 실제 테이블 상태 불일치

## 📊 현재 환경

- **Keycloak 버전**: 24.0 (`quay.io/keycloak/keycloak:24.0`)
- **MariaDB 버전**: 10.11 (`mariadb:10.11`)
- **데이터베이스 타입**: `KC_DB=mysql` (MariaDB는 MySQL 호환)

## 🔬 기술적 세부사항

### CLOB vs TEXT

**CLOB (Character Large Object):**
- Oracle, DB2, PostgreSQL 등에서 사용
- MySQL/MariaDB에서는 지원하지 않음

**MariaDB/MySQL 대안:**
- `TEXT`: 최대 65,535 바이트
- `MEDIUMTEXT`: 최대 16,777,215 바이트
- `LONGTEXT`: 최대 4,294,967,295 바이트

### Keycloak의 데이터베이스 호환성

Keycloak은 공식적으로 다음 데이터베이스를 지원합니다:
- ✅ **MySQL 8.0+** (완전 지원)
- ✅ **PostgreSQL** (완전 지원)
- ✅ **Oracle** (완전 지원)
- ⚠️ **MariaDB** (제한적 지원 - MySQL 호환성에 의존)

**MariaDB와 Keycloak의 호환성 문제:**
- MariaDB는 MySQL과 호환되지만, 일부 타입과 기능에서 차이가 있습니다
- Keycloak의 일부 버전에서 MariaDB와 완벽하게 호환되지 않을 수 있습니다
- 특히 `CLOB` 타입과 같은 비표준 타입에서 문제가 발생할 수 있습니다

## 💡 해결 방법

### 방법 1: MySQL 사용 (권장)

MariaDB 대신 MySQL을 사용하면 Keycloak과 완벽하게 호환됩니다.

**장점:**
- Keycloak 공식 지원 데이터베이스
- CLOB 타입 문제 없음
- 완전한 호환성 보장

**단점:**
- 기존 MariaDB 데이터 마이그레이션 필요

### 방법 2: Keycloak 버전 다운그레이드

Keycloak 22.0 또는 23.0으로 다운그레이드하여 MariaDB 호환성 개선 버전 사용.

**장점:**
- MariaDB 유지 가능
- 기존 데이터 유지

**단점:**
- 최신 기능 사용 불가
- 보안 업데이트 지연

### 방법 3: MariaDB 버전 업그레이드

MariaDB 최신 버전으로 업그레이드하여 호환성 개선.

**장점:**
- 기존 설정 유지

**단점:**
- 문제 해결 보장 없음
- CLOB 타입은 여전히 지원하지 않음

### 방법 4: 데이터베이스 초기화 후 재시작

데이터베이스를 완전히 초기화하고 Keycloak을 재시작.

**장점:**
- 빠른 해결
- 기존 설정 유지

**단점:**
- 근본 원인 해결 안 됨
- 재발 가능성

## 🎯 권장 해결책

**가장 확실한 해결책: MariaDB를 MySQL로 변경**

이유:
1. Keycloak 공식 지원 데이터베이스
2. CLOB 타입 문제 완전 해결
3. 장기적 안정성 보장
4. 최신 Keycloak 버전과 완벽한 호환성

## 📝 확인 사항

다음 명령어로 현재 상태를 확인할 수 있습니다:

```bash
# MariaDB 버전 확인
docker compose exec db mysql -u root -ppassword -e "SELECT VERSION();"

# Keycloak 데이터베이스 테이블 확인
docker compose exec db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES;"

# Liquibase changelog 확인
docker compose exec db mysql -u root -ppassword -e "USE keycloak; SELECT * FROM DATABASECHANGELOG LIMIT 5;"

# Keycloak 버전 확인
docker compose exec keycloak /opt/keycloak/bin/kc.sh --version
```

## 🔄 다음 단계

1. **즉시 해결**: 데이터베이스 완전 초기화 후 재시작
2. **근본 해결**: MariaDB를 MySQL로 변경
3. **장기 해결**: Keycloak과 데이터베이스 버전 호환성 확인 및 업데이트

