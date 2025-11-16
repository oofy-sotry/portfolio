# Keycloak CLOB 타입 오류 단계별 분석

## 문제 상황

```
ERROR: You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ' NAME VARCHAR(255) NOT NULL)' at line 1 
[Failed SQL: (1064) CREATE TABLE PROTOCOL_MAPPER_CONFIG (PROTOCOL_MAPPER_ID VARCHAR(36) NOT NULL, VALUE CLOB, NAME VARCHAR(255) NOT NULL)]
```

## 단계별 문제 분석

### 1단계: 오류 원인 파악

**문제**: Keycloak이 MariaDB에서 `CLOB` 타입을 사용하려고 시도
- MariaDB는 `CLOB` 타입을 지원하지 않음
- MariaDB에서는 `TEXT`, `MEDIUMTEXT`, `LONGTEXT`를 사용해야 함
- Keycloak의 Liquibase 마이그레이션 스크립트가 MariaDB를 완전히 지원하지 않음

**영향받는 테이블**: `PROTOCOL_MAPPER_CONFIG`
- `VALUE CLOB` → MariaDB에서 오류 발생

### 2단계: Keycloak 버전 확인

**현재 설정**: Keycloak 23.0
- Keycloak 23.0도 여전히 MariaDB에서 CLOB 타입 문제가 발생할 수 있음
- 이는 Keycloak의 내부 마이그레이션 스크립트 문제

**확인 방법**:
```bash
docker compose images keycloak
# 또는
docker images | grep keycloak
```

### 3단계: 데이터베이스 상태 확인

**확인 사항**:
1. 데이터베이스가 완전히 초기화되었는지
2. 이전 테이블이 남아있는지
3. Liquibase 변경 로그가 남아있는지

**확인 명령어**:
```bash
# 데이터베이스 존재 확인
docker compose exec db mysql -u root -ppassword -e "SHOW DATABASES LIKE 'keycloak';"

# 테이블 확인
docker compose exec db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES;"

# Liquibase 변경 로그 확인
docker compose exec db mysql -u root -ppassword -e "USE keycloak; SHOW TABLES LIKE 'DATABASECHANGELOG%';"
```

### 4단계: 해결 방법 선택

#### 방법 1: Keycloak 최신 버전 사용 (권장)

Keycloak 24.0 이상에서는 MariaDB 호환성이 개선되었을 수 있습니다.

```yaml
keycloak:
  image: quay.io/keycloak/keycloak:24.0
  # 또는
  image: quay.io/keycloak/keycloak:latest
```

#### 방법 2: MariaDB 대신 MySQL 사용

MySQL은 Keycloak과 더 나은 호환성을 제공합니다.

```yaml
db:
  image: mysql:8.0
  # MariaDB 대신 MySQL 사용
```

#### 방법 3: 데이터베이스 완전 초기화

데이터베이스를 완전히 삭제하고 재생성:

```bash
# 1. 모든 서비스 중지
docker compose down

# 2. Keycloak 데이터베이스 볼륨 삭제 (주의: 모든 데이터 삭제)
docker volume rm portfolio_website_db_data

# 3. 서비스 재시작
docker compose up -d
```

#### 방법 4: Keycloak을 개발 모드로 실행 (임시 해결)

개발 모드는 메모리 기반 데이터베이스를 사용하므로 CLOB 문제가 발생하지 않습니다.

```yaml
keycloak:
  command: ["start-dev"]  # 프로덕션 모드 대신 개발 모드
```

**주의**: 개발 모드는 프로덕션 환경에 적합하지 않습니다.

## 권장 해결 순서

1. **데이터베이스 완전 초기화** (가장 확실한 방법)
   ```bash
   docker compose stop keycloak
   bash scripts/fix_keycloak_user.sh --reset-db
   docker compose pull keycloak  # 최신 이미지 다운로드
   docker compose up -d keycloak
   ```

2. **Keycloak 최신 버전 확인 및 업그레이드**
   - Keycloak 24.0 이상 사용
   - 또는 `latest` 태그 사용

3. **MariaDB 대신 MySQL 사용 고려**
   - MySQL은 Keycloak과 더 나은 호환성 제공

4. **로그 확인**
   ```bash
   docker compose logs -f keycloak
   ```

## 현재 상태 점검 체크리스트

- [ ] Keycloak 이미지 버전 확인
- [ ] 데이터베이스가 완전히 비어있는지 확인
- [ ] Keycloak이 최신 버전인지 확인
- [ ] MariaDB 버전 확인 (10.11 이상 권장)
- [ ] 데이터베이스 초기화 스크립트가 실행되었는지 확인

## 다음 단계

1. 현재 Keycloak 버전 확인
2. 데이터베이스 상태 확인
3. 위의 해결 방법 중 하나 선택하여 적용
4. 로그 모니터링

## 진단 스크립트 사용

데이터베이스 상태를 확인하려면:

```bash
bash scripts/check_keycloak_db.sh
```

이 스크립트는 다음을 확인합니다:
- 데이터베이스 존재 여부
- 테이블 개수 및 목록
- Liquibase 변경 로그
- 사용자 존재 여부
- 연결 테스트
- Keycloak 컨테이너 상태

