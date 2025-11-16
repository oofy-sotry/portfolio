# start_service.sh 사용 가이드

## 개요

`start_service.sh`는 Portfolio 웹사이트의 모든 서비스를 올바른 순서로 시작하는 통합 스크립트입니다.

## 사용 방법

```bash
bash scripts/start_service.sh
```

또는 프로젝트 루트에서:

```bash
./scripts/start_service.sh
```

## 스크립트가 수행하는 작업

### 1. 환경 설정
- `.env` 파일 확인 및 생성 (없는 경우)
- IP 주소 자동 감지

### 2. 기존 서비스 정리
- 실행 중인 서비스 확인
- 기존 서비스 종료 및 정리

### 3. 인프라 서비스 시작
- MySQL 시작
- Elasticsearch 시작
- (Keycloak은 나중에 시작)

### 4. MySQL 준비 대기
- MySQL이 완전히 준비될 때까지 대기 (최대 60초)
- Healthcheck 확인

### 5. Keycloak 데이터베이스 초기화
- 데이터베이스 존재 여부 확인
- 테이블 존재 여부 확인
- **테이블이 있으면 자동으로 데이터베이스 초기화** (완전 삭제 및 재생성)
- Keycloak 사용자 생성/재생성

### 6. Elasticsearch 준비 대기
- Elasticsearch가 준비될 때까지 대기 (최대 120초)
- 실패 시 로그 출력 및 계속 진행 옵션 제공

### 7. Keycloak 시작 전 최종 확인
- Keycloak이 실행 중이면 중지
- 데이터베이스가 완전히 비어있는지 최종 확인
- 테이블이 있으면 다시 초기화

### 8. Keycloak 시작
- Keycloak 서비스 시작
- MySQL 연동 모드로 실행

### 9. Keycloak 준비 대기
- Keycloak이 준비될 때까지 대기 (최대 180초)
- 30초마다 상태 확인
- 실패 시 상세한 진단 정보 제공

### 10. Keycloak 설정
- `setup_keycloak.py` 실행
- Realm, Client, 사용자 생성
- Client Secret 획득 및 `.env` 파일 업데이트

### 11. 웹 애플리케이션 시작
- Flask 웹 애플리케이션 시작
- 준비 대기 (최대 60초)

### 12. Nginx 시작 (선택사항)
- Nginx 서비스 시작 (docker-compose.yml에 정의된 경우)

### 13. 초기 데이터 설정 (선택사항)
- 사용자 확인 후 샘플 데이터 생성

### 14. 최종 확인 및 요약
- 환경 변수 확인
- 서비스 상태 확인
- 접속 URL 및 계정 정보 출력

## 왜 start_service.sh를 사용해야 하나요?

### 장점

1. **자동화**: 모든 단계를 자동으로 수행
2. **의존성 관리**: 서비스 간 의존성을 올바른 순서로 처리
3. **에러 처리**: 각 단계에서 에러 발생 시 진단 정보 제공
4. **데이터베이스 초기화**: Keycloak 데이터베이스를 자동으로 초기화
5. **상태 확인**: 각 서비스가 준비될 때까지 대기

### docker compose up -d와의 차이

**`docker compose up -d`**:
- 모든 서비스를 동시에 시작
- 의존성만 확인 (healthcheck 완료 대기 안 함)
- 데이터베이스 초기화 안 함
- 에러 발생 시 수동으로 확인 필요

**`start_service.sh`**:
- 서비스를 올바른 순서로 시작
- 각 서비스가 준비될 때까지 대기
- 데이터베이스 자동 초기화
- 에러 발생 시 자동 진단 및 해결 방법 제시

## 문제 해결

### Keycloak이 시작되지 않는 경우

스크립트가 자동으로:
1. 데이터베이스 상태 확인
2. 테이블이 있으면 자동 초기화
3. 상세한 로그 출력
4. 해결 방법 제시

### 수동으로 문제 해결이 필요한 경우

```bash
# 1. 데이터베이스 상태 확인
bash scripts/check_keycloak_db.sh

# 2. 데이터베이스 수동 초기화
bash scripts/fix_keycloak_user.sh --reset-db

# 3. Keycloak 재시작
docker compose restart keycloak
```

## 주의사항

⚠️ **데이터베이스 초기화**
- 스크립트는 Keycloak 데이터베이스에 테이블이 있으면 자동으로 초기화합니다
- 이는 모든 Keycloak 설정(Realm, Client, User 등)이 삭제됨을 의미합니다
- 초기화 후 `setup_keycloak.py`가 자동으로 기본 설정을 복원합니다

## FAQ

**Q: start_service.sh를 사용해야 하나요, 아니면 docker compose up -d를 사용해야 하나요?**
A: **start_service.sh를 사용하는 것을 강력히 권장합니다.** 자동화, 에러 처리, 데이터베이스 초기화 등 많은 장점이 있습니다.

**Q: 스크립트 실행 중 에러가 발생하면 어떻게 하나요?**
A: 스크립트가 자동으로 진단 정보와 해결 방법을 제시합니다. 로그를 확인하고 제시된 해결 방법을 따르세요.

**Q: 데이터베이스가 자동으로 초기화되는 것이 걱정됩니다.**
A: 스크립트는 테이블이 있을 때만 초기화합니다. 데이터를 보존하려면 스크립트 실행 전에 백업하세요.

