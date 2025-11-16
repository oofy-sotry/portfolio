# Keycloak 데이터베이스 호환성 문제 해결

## ⚠️ 중요: MariaDB에서 MySQL로 마이그레이션 완료

이 프로젝트는 **MariaDB 10.11에서 MySQL 8.0으로 마이그레이션**되었습니다.

## 문제 (이전 상태)

Keycloak 24.0을 MariaDB 10.11과 함께 사용할 때 다음과 같은 오류가 발생했습니다:

1. **CLOB 타입 오류**: `You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ' NAME VARCHAR(255) NOT NULL)'`
2. **테이블이 이미 존재**: `Table 'PROTOCOL_MAPPER' already exists`

## 원인

- Keycloak 24.0의 Liquibase changelog가 `CLOB` 타입을 사용
- **MariaDB 10.11은 `CLOB` 타입을 지원하지 않음** (MySQL만 지원)
- 데이터베이스 초기화가 제대로 되지 않아 이전 테이블이 남아있음
- Liquibase 변경 로그가 제대로 초기화되지 않음

## 해결 방법

### 최종 해결책: MySQL 8.0으로 마이그레이션

**변경 사항:**
- `docker-compose.yml`: `mariadb:10.11` → `mysql:8.0`
- `init_mariadb.sql` → `init_mysql.sql`
- 모든 스크립트 및 문서에서 MySQL로 업데이트

**결과:**
- ✅ CLOB 타입 오류 완전 해결
- ✅ Keycloak 정상 시작
- ✅ 모든 서비스 정상 작동

## 해결 방법

### 자동 해결 (권장)

`start_service.sh` 스크립트를 실행하면 자동으로 데이터베이스를 초기화합니다:

```bash
bash scripts/start_service.sh
```

스크립트는 다음을 자동으로 수행합니다:
1. Keycloak 데이터베이스에 테이블이 있는지 확인
2. 테이블이 있으면 데이터베이스를 완전히 삭제하고 재생성
3. Keycloak 사용자 생성/재생성
4. Keycloak 시작

### 수동 해결

데이터베이스를 수동으로 초기화하려면:

```bash
# Keycloak 중지
docker compose stop keycloak

# 데이터베이스 초기화 스크립트 실행
bash scripts/fix_keycloak_user.sh --reset-db

# Keycloak 재시작
docker compose up -d keycloak
```

또는 직접 MySQL에 접속하여:

```bash
docker compose exec db mysql -u root -ppassword <<EOF
DROP DATABASE IF EXISTS keycloak;
CREATE DATABASE keycloak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
DROP USER IF EXISTS 'keycloak'@'%';
CREATE USER 'keycloak'@'%' IDENTIFIED BY 'keycloak123';
GRANT ALL PRIVILEGES ON keycloak.* TO 'keycloak'@'%';
FLUSH PRIVILEGES;
EOF

docker compose up -d keycloak
```

## 주의사항

⚠️ **데이터베이스를 초기화하면 모든 Keycloak 설정(Realm, Client, User 등)이 삭제됩니다!**

프로덕션 환경에서는:
1. 데이터베이스 백업을 먼저 수행
2. 초기화 후 `setup_keycloak.py`를 다시 실행하여 기본 설정 복원

## 현재 상태

- ✅ **데이터베이스**: MySQL 8.0
- ✅ **Keycloak 버전**: 24.0
- ✅ **모드**: 프로덕션 모드 (`start`)
- ✅ **데이터 영속성**: MySQL에 저장

## 추가 정보

- Keycloak 24.0은 MySQL 8.0과 완벽한 호환성을 제공합니다
- MariaDB는 MySQL 호환성을 기반으로 하지만, 일부 타입(`CLOB`)에서 차이가 있습니다
- Keycloak 공식 문서에서 MySQL 8.0+를 권장합니다

## 참고 문서

- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 데이터베이스 변경 이력 및 문제 해결
- [SERVICE_ARCHITECTURE.md](./SERVICE_ARCHITECTURE.md) - 전체 서비스 아키텍처

