# Portfolio 웹사이트 서비스 아키텍처 문서

## 개요

이 문서는 Portfolio 웹사이트의 전체 서비스 구조와 시작 프로세스를 설명합니다.

## 서비스 구성

### 1. 웹 애플리케이션 (web)
- **기술 스택**: Flask (Python 3.11)
- **포트**: 5000
- **기능**: 
  - 사용자 인증 및 인가 (Keycloak 연동)
  - 게시판 CRUD 기능
  - 검색 기능 (Elasticsearch 연동)
  - 챗봇 기능 (LLM 모델 연동)
  - 프로필 관리
- **의존성**: 
  - MySQL (데이터베이스)
  - Elasticsearch (검색 엔진)
  - Keycloak (인증 서버)

### 2. 데이터베이스 (db)
- **기술 스택**: MySQL 8.0
- **포트**: 3306
- **데이터베이스**:
  - `portfolio_db`: 메인 애플리케이션 데이터베이스
  - `keycloak`: Keycloak 데이터베이스
- **초기화**: `init_mysql.sql` 스크립트로 데이터베이스 및 사용자 생성

### 3. 검색 엔진 (elasticsearch)
- **기술 스택**: Elasticsearch 8.11.0
- **포트**: 9200
- **기능**: 게시글 및 콘텐츠 전문 검색
- **설정**: 단일 노드 모드, 보안 비활성화 (개발 환경)

### 4. 인증 서버 (keycloak)
- **기술 스택**: Keycloak 24.0
- **포트**: 8080
- **기능**: 
  - OAuth 2.0 / OpenID Connect 인증
  - 사용자 관리
  - Realm 및 Client 관리
- **모드**: 프로덕션 모드 (start)
- **데이터베이스**: MySQL (keycloak 데이터베이스)
- **관리자 계정**: admin / admin123
- **의존성**: MySQL (healthcheck 완료 후 시작)

### 5. 리버스 프록시 (nginx)
- **기술 스택**: Nginx Alpine
- **포트**: 80, 443
- **기능**: 
  - 웹 애플리케이션 프록시
  - 정적 파일 서빙
  - SSL/TLS 종료 (프로덕션 환경)
- **의존성**: web, keycloak

## 서비스 시작 프로세스

### 단계별 시작 순서

1. **환경 설정**
   - `.env` 파일 생성 (없는 경우)
   - IP 주소 자동 감지
   - Keycloak URL 설정

2. **기존 서비스 정리**
   - 실행 중인 Docker Compose 서비스 확인
   - 기존 서비스 종료 및 정리

3. **인프라 서비스 시작**
   - MySQL 시작
   - Elasticsearch 시작
   - Keycloak 시작
   - 각 서비스가 준비될 때까지 대기

4. **데이터베이스 초기화**
   - MySQL이 준비될 때까지 대기
   - 데이터베이스 및 사용자 생성 (`init_mysql.sql`)
   - 애플리케이션 데이터베이스 테이블 생성 (`init_db.py`)
   - 기본 카테고리 생성

5. **Keycloak 설정**
   - Keycloak이 준비될 때까지 대기
   - Portfolio Realm 생성
   - Portfolio Client 생성 및 Client Secret 획득
   - 테스트 사용자 생성 (admin, testuser)
   - `.env` 파일에 Client Secret 업데이트

6. **Elasticsearch 준비 확인**
   - Elasticsearch가 준비될 때까지 대기
   - 인덱스 생성 (필요한 경우)

7. **웹 애플리케이션 시작**
   - 환경 변수 로드 (`.env` 파일)
   - 데이터베이스 연결 확인
   - Flask 애플리케이션 시작 (Gunicorn)
   - 모델 다운로드 (필요한 경우)

8. **초기 데이터 설정** (선택사항)
   - 샘플 게시글 생성
   - 추가 카테고리 생성

9. **리버스 프록시 시작**
   - Nginx 시작
   - 프록시 설정 확인

10. **서비스 상태 확인**
    - 모든 서비스 상태 확인
    - 접속 URL 출력

## 데이터 흐름

### 사용자 인증 흐름
1. 사용자가 웹 애플리케이션에 로그인 요청
2. 웹 애플리케이션이 Keycloak으로 리다이렉트
3. Keycloak에서 사용자 인증
4. Keycloak이 인증 토큰 발급
5. 웹 애플리케이션이 토큰 검증 및 사용자 정보 저장

### 검색 흐름
1. 사용자가 검색어 입력
2. 웹 애플리케이션이 Elasticsearch에 검색 요청
3. Elasticsearch가 인덱스에서 검색 수행
4. 결과를 웹 애플리케이션으로 반환
5. 웹 애플리케이션이 결과를 사용자에게 표시

### 게시글 작성 흐름
1. 사용자가 게시글 작성
2. 웹 애플리케이션이 MySQL에 저장
3. 동시에 Elasticsearch 인덱스에 추가 (검색 가능하도록)
4. 사용자에게 성공 메시지 표시

## 환경 변수

### 필수 환경 변수
- `KEYCLOAK_URL`: Keycloak 서버 URL
- `KEYCLOAK_REALM`: Keycloak Realm 이름 (portfolio)
- `KEYCLOAK_CLIENT_ID`: Keycloak Client ID (portfolio-web)
- `KEYCLOAK_CLIENT_SECRET`: Keycloak Client Secret (자동 생성)
- `DATABASE_URL`: MySQL 연결 문자열
- `SECRET_KEY`: Flask 세션 암호화 키
- `ELASTICSEARCH_URL`: Elasticsearch 서버 URL

### 선택적 환경 변수
- `OPENAI_API_KEY`: OpenAI API 키 (챗봇 기능)
- `HUGGINGFACE_API_KEY`: HuggingFace API 키 (LLM 모델)
- `FLASK_ENV`: Flask 환경 (development/production)

## 네트워크 구성

```
인터넷
  │
  ├─ Nginx (80, 443)
  │   ├─ Web Application (5000)
  │   └─ Keycloak (8080)
  │
  ├─ MySQL (3306)
  │
  └─ Elasticsearch (9200)
```

## 볼륨 및 데이터 영속성

- `db_data`: MySQL 데이터 영속성
  - `portfolio_db`: 메인 애플리케이션 데이터베이스
  - `keycloak`: Keycloak 인증 서버 데이터베이스
- `es_data`: Elasticsearch 인덱스 데이터 영속성
- `huggingface_cache`: HuggingFace 모델 캐시

## 보안 고려사항

1. **현재 설정**:
   - Keycloak: 프로덕션 모드 (start) - MySQL 사용
   - Elasticsearch: 보안 비활성화 (개발 환경)
   - HTTP 사용
   - 데이터 영속성: MySQL에 저장

2. **프로덕션 환경 추가 권장사항**:
   - Elasticsearch: 보안 활성화 필요
   - HTTPS 사용 (SSL 인증서 설정)
   - 강력한 비밀번호 사용 (현재 기본 비밀번호 변경 권장)
   - 환경 변수 보안 관리
   - Keycloak: HTTPS 강제 설정

## 문제 해결

### 서비스가 시작되지 않는 경우
1. 포트 충돌 확인 (5000, 3306, 8080, 9200)
2. Docker 리소스 확인 (메모리, 디스크)
3. 로그 확인: `docker compose logs [service_name]`

### 데이터베이스 연결 실패
1. MySQL이 완전히 시작되었는지 확인
2. 연결 문자열 확인
3. 사용자 권한 확인

### Keycloak 설정 실패
1. Keycloak이 완전히 시작되었는지 확인 (최대 60초 대기)
2. 관리자 계정 확인 (admin / admin123)
3. 네트워크 연결 확인

### Elasticsearch 연결 실패
1. Elasticsearch가 완전히 시작되었는지 확인
2. 메모리 설정 확인 (최소 512MB 필요)
3. 포트 충돌 확인

## 모니터링

### 서비스 상태 확인
```bash
docker compose ps
```

### 로그 확인
```bash
# 전체 로그
docker compose logs -f

# 특정 서비스 로그
docker compose logs -f web
docker compose logs -f keycloak
docker compose logs -f db
docker compose logs -f elasticsearch
```

### 리소스 사용량 확인
```bash
docker stats
```

## 확장 가능성

### 수평 확장
- 웹 애플리케이션: 여러 인스턴스 실행 가능 (로드 밸런서 필요)
- Elasticsearch: 클러스터 모드로 확장 가능
- MySQL: 마스터-슬레이브 복제 구성 가능

### 수직 확장
- 각 서비스의 리소스 할당량 증가
- Elasticsearch 힙 메모리 증가
- MySQL 버퍼 풀 크기 증가

