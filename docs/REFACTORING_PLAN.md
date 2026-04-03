# 리팩토링 계획

## 개요

프로젝트의 미완성 코드, 구버전 잔재, 구조적 문제를 정리하고
로드맵(사용자별 프로필, ES 검색, 개인화 챗봇)을 구현하기 위한 리팩토링 계획.

---

## Phase 1: 기반 정리

> 이후 작업의 토대가 되는 정리 작업

### 1-1. docker-compose.llm.yml 삭제 ✅ (2026-04-03)
- [x] `docker-compose.llm.yml` 삭제
  - MariaDB 10.11 기반의 구버전 설정 (현재 MySQL 8.0 사용)
  - Keycloak 설정 누락
  - GPU LLM 컨테이너 방식은 사용하지 않음 (향후 API 방식으로 전환)

### 1-2. 검색 기능 정상화 ✅ (2026-04-03)
- [x] `search/advanced.html` 템플릿 생성
- [x] `base.html` 네비게이션에 검색 링크 추가
- [x] Blueprint url_prefix 중복 라우트 경로 수정 (`/search/search` → `/search`)

### 1-3. README.md 업데이트
- [ ] 삭제된 문서 참조 제거 (KEYCLOAK_MARIADB_FIX.md, WEB_ACCESS_TROUBLESHOOTING.md 등)
- [ ] 현재 프로젝트 구조에 맞게 업데이트

---

## Phase 2: 사용자별 프로필 시스템

> 로드맵 목표 1 — 단일 프로필 → 사용자별 1:1 프로필

### 2-1. Profile 모델에 user_id 추가
- [ ] `Profile` 모델에 `user_id` 컬럼 추가 (User와 1:1 관계)
- [ ] `User` 모델에 `profile` 관계 추가 (`backref`)
- [ ] `get_active_profile()` → `get_user_profile(user_id)` 전환
- [ ] 기존 프로필 데이터 마이그레이션 처리

### 2-2. 프로필 라우트 수정
- [ ] `profile.py` 라우트에서 `current_user.id` 기반으로 변경
- [ ] 프로필 CRUD에 권한 검사 추가 (본인만 수정 가능)
- [ ] 프로필 미존재 시 자동 생성 로직

### 2-3. About 페이지 사용자별 분리
- [ ] `/about` → 로그인 사용자 프로필 표시
- [ ] `/about/<username>` → 특정 사용자 프로필 표시 (읽기 전용)
- [ ] `about.html` 템플릿 수정

---

## Phase 3: 검색 시스템 고도화

> ES 검색이 실제로 동작하도록 완성

### 3-1. Elasticsearch 서비스 점검
- [ ] `elasticsearch_service.py`의 인덱스 매핑 검증
- [ ] 게시글 작성/수정/삭제 시 ES 인덱스 자동 동기화 확인
- [ ] `get_suggestions()` — completion suggester 매핑 추가 필요
- [ ] `get_popular_searches()` — 현재 하드코딩된 샘플 데이터 → 실제 검색 로그 기반으로 전환

### 3-2. 검색 API 엔드포인트 정리
- [ ] `/api/search/suggestions` — 프론트엔드 자동완성 연결
- [ ] `/api/search/related` — 게시글 상세 페이지에서 관련 글 표시
- [ ] `/api/search/popular` — 검색 페이지에서 인기 검색어 표시
- [ ] `/search/ai`, `/search/semantic` — 사용 여부 결정 후 구현 또는 삭제

---

## Phase 3.5: 로컬 모델 교체

> 현재 영어 전용 모델 → 한글 지원 모델로 교체

### 3.5-1. 현재 모델 문제점
- `distilgpt2` (생성): 영어 전용 82M 모델, 한글 이해 불가
- `facebook/bart-large-cnn` (요약): 영어 뉴스 전용, 한글 불가, 406M으로 무거움
- `all-MiniLM-L6-v2` (임베딩): 영어 중심, 한글 유사도 부정확

### 3.5-2. 임베딩 모델 교체
- [ ] `all-MiniLM-L6-v2` → 한글 지원 임베딩 모델로 변경 (예: `jhgan/ko-sroberta-multitask`)
- [ ] `llm_service.py` 모델 경로 업데이트
- [ ] `download_models.py` 스크립트 업데이트
- [ ] ES 검색 유사도 테스트

### 3.5-3. 생성/요약 모델 정리
- [ ] `distilgpt2`, `bart-large-cnn` 제거 (Phase 4에서 API LLM이 대체)
- [ ] `llm_service.py`에서 생성/요약은 API 호출로 전환할 준비
- [ ] 모델 미로드 시 fallback 응답 개선

---

## Phase 4: LLM 서비스 확장

> api_llm_service.py에 외부 API 연동 (생성/요약을 API LLM으로 대체)

### 4-1. API LLM 서비스 구현
- [ ] `api_llm_service.py`에 Claude API 연동
- [ ] GPT API 연동
- [ ] Gemini API 연동
- [ ] LLM 서비스 선택 로직 (환경변수 또는 설정으로 전환)

### 4-2. 챗봇 개인화
- [ ] 챗봇 라우트에 `@login_required` 추가
- [ ] 현재 사용자의 프로필 정보를 LLM 컨텍스트에 포함
- [ ] 프로필 기반 FAQ 응답 생성

---

## Phase 5: UI/UX 개선

### 5-1. 프론트엔드 정리
- [ ] 검색 결과 UI 개선
- [ ] 챗봇 UI 개선
- [ ] 반응형 디자인 점검

---

## 완료된 작업

- [x] 미사용 코드/중복 파일/불필요한 문서 정리 (2026-04-03)
  - 중복 스크립트 6개 삭제
  - 구버전 마이그레이션 문서 10개 삭제
  - 미사용 import 정리 (auth.py, main.py, search.py)
  - main.py의 /search 라우트 충돌 제거
