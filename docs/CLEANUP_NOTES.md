# 코드 정리 노트

## 개요

이 문서는 프로젝트에서 사용되지 않거나 중복되는 부분을 정리한 내용입니다.

## 사용되지 않는 파일/기능

### 1. `scripts/update_keycloak_client.sh`
- **상태**: 사용되지 않음
- **이유**: `setup_keycloak.py`가 이미 모든 Keycloak 설정을 처리함
- **권장 조치**: 
  - 삭제하거나
  - 수동으로 Keycloak Client 설정을 업데이트할 때만 사용하는 유틸리티로 유지

### 2. `docker-compose.yml`의 Keycloak DB 설정
- **위치**: `db` 서비스의 환경 변수
- **내용**: 
  ```yaml
  - MYSQL_DATABASE_KEYCLOAK=keycloak
  - MYSQL_USER_KEYCLOAK=keycloak
  - MYSQL_PASSWORD_KEYCLOAK=keycloak123
  ```
- **상태**: 사용되지 않음
- **이유**: Keycloak이 `start-dev` 모드로 실행되어 메모리 기반 H2 데이터베이스를 사용함
- **권장 조치**: 
  - 주석 처리하거나
  - 프로덕션 환경에서 Keycloak을 DB와 연동할 때 사용할 수 있도록 유지
# 상태 변경경  
- **상태**: ✅ 사용 중
- **이유**: Keycloak이 프로덕션 모드(`start`)로 실행되어 MySQL 데이터베이스를 사용함
- **권장 조치**: 유지 (Keycloak이 MySQL과 연동됨)

### 3. `init_mysql.sql`의 Keycloak DB 생성
- **위치**: `init_mysql.sql` 파일
- **내용**: Keycloak 데이터베이스 및 사용자 생성
- **상태**: ✅ 사용 중
- **이유**: Keycloak이 MySQL 데이터베이스를 사용함
- **권장 조치**: 
  - 유지 (Keycloak이 MySQL과 연동됨)

## 중복 기능

### 1. 환경 설정 파일 생성
- **파일들**: 
  - `scripts/setup_env.sh`
  - `scripts/start_service.sh` (내장된 .env 생성 로직)
- **상태**: 중복
- **권장 조치**: 
  - `start_service.sh`가 `setup_env.sh`를 호출하도록 이미 구현되어 있음
  - 두 파일 모두 유지 (start_service.sh는 fallback으로 사용)

### 2. 데이터베이스 초기화
- **파일들**: 
  - `init_db.py`
  - `init_data.py`
  - `run.py`의 `init_db` 명령어
- **상태**: 각각 다른 목적
- **설명**: 
  - `init_db.py`: 기본 테이블 및 카테고리 생성
  - `init_data.py`: 샘플 데이터 생성
  - `run.py`: Flask CLI 명령어
- **권장 조치**: 모두 유지 (각각 다른 목적)

## 개선 사항

### 1. Keycloak 데이터베이스 설정
✅ **완료**: Keycloak이 MySQL 8.0과 연동되도록 설정되었습니다.
- 프로덕션 모드(`start`)로 실행
- MySQL 8.0 데이터베이스 사용
- 데이터 영속성 보장
- MariaDB에서 MySQL로 마이그레이션 완료 (CLOB 타입 호환성 문제 해결)

### 2. 환경 변수 관리
- `.env` 파일이 여러 곳에서 생성/수정됨
- `setup_keycloak.py`가 `.env` 파일을 직접 수정함
- 권장: 환경 변수 관리를 중앙화

### 3. 스크립트 통합
- 여러 스크립트가 유사한 기능을 수행함
- 권장: 공통 기능을 함수로 추출하여 재사용

## 정리 권장 사항

### 즉시 정리 가능
1. `scripts/update_keycloak_client.sh` 삭제 또는 문서화
2. `docker-compose.yml`의 Keycloak DB 환경 변수는 사용 중 (유지)
3. `init_mysql.sql`의 Keycloak DB 생성 부분은 사용 중 (유지)

### 향후 개선
1. Keycloak 프로덕션 모드 설정 추가
2. 환경 변수 관리 중앙화
3. 스크립트 통합 및 모듈화

