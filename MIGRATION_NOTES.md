# MariaDB에서 MySQL로 마이그레이션 완료

## 변경 사항 요약

### 1. Docker Compose 설정
- **변경 전**: `mariadb:10.11`
- **변경 후**: `mysql:8.0`
- **파일**: `docker-compose.yml`

### 2. 초기화 스크립트
- **변경 전**: `init_mariadb.sql`
- **변경 후**: `init_mysql.sql`
- **내용**: 동일 (MySQL과 MariaDB 모두 동일한 SQL 구문 사용)

### 3. 스크립트 업데이트
- `scripts/start_service.sh`: MariaDB 언급을 MySQL로 변경
- `scripts/fix_keycloak_user.sh`: 주석 업데이트

### 4. 문서 업데이트
- `docs/SERVICE_ARCHITECTURE.md`: MySQL 8.0으로 업데이트
- `docs/START_SERVICE_GUIDE.md`: MySQL 언급으로 변경
- `docs/TROUBLESHOOTING.md`: MySQL로 업데이트
- `docs/CLEANUP_NOTES.md`: MySQL로 업데이트

## 마이그레이션 이유

Keycloak 24.0과 MariaDB 10.11.14 간의 호환성 문제:
- **CLOB 타입 오류**: Keycloak이 `CLOB` 타입을 사용하지만 MariaDB는 이를 지원하지 않음
- **해결책**: MySQL 8.0은 Keycloak의 공식 지원 데이터베이스로 완벽한 호환성 제공

## 마이그레이션 후 조치사항

### 1. 기존 데이터 마이그레이션 (선택사항)

기존 MariaDB 데이터가 중요한 경우:

```bash
# 1. MariaDB 데이터 덤프
docker compose exec db mysqldump -u root -ppassword --all-databases > mariadb_backup.sql

# 2. MySQL로 마이그레이션
# MySQL 컨테이너에서 덤프 파일 복원
docker compose exec -T db mysql -u root -ppassword < mariadb_backup.sql
```

### 2. 데이터베이스 완전 초기화 (권장)

기존 데이터가 중요하지 않은 경우:

```bash
# 1. 모든 서비스 중지 및 볼륨 삭제
docker compose down -v

# 2. MySQL로 재시작
docker compose up -d

# 3. start_service.sh 실행
bash scripts/start_service.sh
```

## 주의사항

1. **볼륨 삭제**: `docker compose down -v`를 실행하면 모든 데이터가 삭제됩니다
2. **백업**: 중요한 데이터가 있다면 반드시 백업하세요
3. **환경 변수**: `.env` 파일의 데이터베이스 연결 문자열은 변경할 필요 없습니다 (동일한 포트와 사용자명 사용)

## 검증

마이그레이션 후 다음 명령어로 확인:

```bash
# MySQL 버전 확인
docker compose exec db mysql -u root -ppassword -e "SELECT VERSION();"

# 데이터베이스 목록 확인
docker compose exec db mysql -u root -ppassword -e "SHOW DATABASES;"

# Keycloak 연결 테스트
docker compose exec db mysql -u keycloak -pkeycloak123 -e "USE keycloak; SELECT 1;"
```

## 예상 결과

- ✅ Keycloak이 정상적으로 시작됨
- ✅ CLOB 타입 오류 해결
- ✅ 모든 서비스 정상 작동

