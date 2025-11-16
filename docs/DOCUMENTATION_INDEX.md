# 문서 인덱스

## 개요

이 문서는 Portfolio 웹사이트 프로젝트의 모든 문서를 정리한 인덱스입니다.

## 주요 문서

### 1. 서비스 아키텍처 및 시작 가이드

- **[SERVICE_ARCHITECTURE.md](./SERVICE_ARCHITECTURE.md)**
  - 전체 서비스 구조 설명
  - 서비스 구성 요소 (Web, MySQL, Elasticsearch, Keycloak, Nginx)
  - 데이터 흐름 및 네트워크 구성
  - 환경 변수 및 보안 고려사항

- **[START_SERVICE_GUIDE.md](./START_SERVICE_GUIDE.md)**
  - `start_service.sh` 스크립트 사용 가이드
  - 서비스 시작 프로세스 상세 설명
  - `docker compose up -d`와의 차이점
  - 문제 해결 방법

### 2. 문제 해결 가이드

- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**
  - 일반적인 문제 해결 가이드
  - 데이터베이스 변경 이력 (MariaDB → MySQL)
  - Elasticsearch, Keycloak, 웹 애플리케이션 문제 해결

- **[KEYCLOAK_MARIADB_FIX.md](./KEYCLOAK_MARIADB_FIX.md)**
  - Keycloak 데이터베이스 호환성 문제 해결
  - MariaDB에서 MySQL로 마이그레이션 배경
  - CLOB 타입 오류 해결 방법

- **[WEB_ACCESS_TROUBLESHOOTING.md](./WEB_ACCESS_TROUBLESHOOTING.md)**
  - 웹 애플리케이션 접근 문제 해결
  - 컨테이너 상태 확인 방법
  - 로그 분석 가이드

- **[INIT_DATA_TROUBLESHOOTING.md](./INIT_DATA_TROUBLESHOOTING.md)**
  - 초기 데이터 설정 문제 해결
  - `cryptography` 패키지 설치 문제
  - 데이터베이스 연결 문제

### 3. 기술 문서

- **[KEYCLOAK_ERROR_ROOT_CAUSE.md](./KEYCLOAK_ERROR_ROOT_CAUSE.md)**
  - Keycloak 오류의 근본 원인 분석
  - CLOB 타입 호환성 문제 상세 설명

- **[KEYCLOAK_ERROR_DETAILED_ANALYSIS.md](./KEYCLOAK_ERROR_DETAILED_ANALYSIS.md)**
  - Keycloak 오류 상세 분석
  - 로그 기반 문제 진단

- **[KEYCLOAK_CLOB_ERROR_ANALYSIS.md](./KEYCLOAK_CLOB_ERROR_ANALYSIS.md)**
  - CLOB 타입 오류 분석
  - MariaDB vs MySQL 호환성 비교

- **[REQUIREMENTS_TXT_LOCATION.md](./REQUIREMENTS_TXT_LOCATION.md)**
  - `requirements.txt` 파일 참조 위치 설명
  - Dockerfile, docker-compose.yml, start_service.sh에서의 참조 방식

### 4. 개발 로드맵

- **[USER_FEATURES_ROADMAP.md](./USER_FEATURES_ROADMAP.md)** ⭐ **새로 추가**
  - 사용자별 기능 개발 로드맵
  - 사용자별 프로필 시스템 구현 계획
  - 사용자별 자기소개 페이지 구현 계획
  - 사용자별 챗봇 응답 구현 계획
  - 데이터베이스 마이그레이션 계획
  - 보안 고려사항 및 테스트 계획

### 5. 프로젝트 관리

- **[CLEANUP_NOTES.md](./CLEANUP_NOTES.md)**
  - 사용되지 않는 파일/기능 정리
  - 중복 기능 식별
  - 개선 사항 및 정리 권장 사항

## 문서 읽기 순서

### 처음 시작하는 경우

1. [SERVICE_ARCHITECTURE.md](./SERVICE_ARCHITECTURE.md) - 전체 구조 이해
2. [START_SERVICE_GUIDE.md](./START_SERVICE_GUIDE.md) - 서비스 시작 방법
3. [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 문제 해결 방법

### 문제가 발생한 경우

1. [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 일반적인 문제 해결
2. 특정 서비스 문제:
   - Keycloak: [KEYCLOAK_MARIADB_FIX.md](./KEYCLOAK_MARIADB_FIX.md)
   - 웹 애플리케이션: [WEB_ACCESS_TROUBLESHOOTING.md](./WEB_ACCESS_TROUBLESHOOTING.md)
   - 초기 데이터: [INIT_DATA_TROUBLESHOOTING.md](./INIT_DATA_TROUBLESHOOTING.md)

### 개발을 시작하는 경우

1. [SERVICE_ARCHITECTURE.md](./SERVICE_ARCHITECTURE.md) - 아키텍처 이해
2. [USER_FEATURES_ROADMAP.md](./USER_FEATURES_ROADMAP.md) - 개발 로드맵 확인
3. [CLEANUP_NOTES.md](./CLEANUP_NOTES.md) - 프로젝트 구조 이해

## 문서 업데이트 이력

### 2024-11-15
- ✅ [USER_FEATURES_ROADMAP.md](./USER_FEATURES_ROADMAP.md) 추가
- ✅ [KEYCLOAK_MARIADB_FIX.md](./KEYCLOAK_MARIADB_FIX.md) MySQL 마이그레이션 반영
- ✅ [CLEANUP_NOTES.md](./CLEANUP_NOTES.md) MySQL 반영
- ✅ [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) 생성

### 이전 업데이트
- MariaDB → MySQL 마이그레이션 관련 문서 업데이트
- Keycloak 24.0 관련 문서 업데이트
- `cryptography` 패키지 문제 해결 문서 추가

## 문서 작성 가이드

새로운 문서를 작성할 때:

1. **명확한 제목**: 문서의 목적을 명확히 표현
2. **목차**: 긴 문서는 목차 포함
3. **코드 예제**: 가능한 경우 실제 코드 예제 포함
4. **문제 해결**: 문제가 있다면 해결 방법 제시
5. **참고 링크**: 관련 문서로의 링크 포함

## 피드백

문서에 대한 피드백이나 개선 사항이 있으면 이슈를 생성하거나 직접 수정해주세요.

