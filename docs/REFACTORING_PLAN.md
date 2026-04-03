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

### 1-3. README.md 업데이트 ✅ (2026-04-03)
- [x] 삭제된 문서 참조 제거
- [x] 현재 프로젝트 구조에 맞게 업데이트

---

## Phase 2: 사용자별 프로필 시스템

> 로드맵 목표 1 — 단일 프로필 → 사용자별 1:1 프로필

### 2-1. Profile 모델에 user_id 추가 ✅ (2026-04-03)
- [x] `Profile` 모델에 `user_id` 컬럼 추가 (User와 1:1 관계)
- [x] `User` 모델에 `profile` 관계 추가 (`uselist=False`)
- [x] `get_active_profile()` → `get_user_profile(user_id)` 전환

### 2-2. 프로필 라우트 수정 ✅ (2026-04-03)
- [x] `profile.py` 라우트에서 `current_user.id` 기반으로 변경 (9곳)
- [x] 회원가입 시 User + Profile 동시 생성
- [x] Keycloak 로그인 시에도 Profile 자동 생성

### 2-3. About 페이지 사용자별 분리 ✅ (2026-04-03)
- [x] `/about` → 로그인 사용자 프로필 표시
- [x] `/about/<username>` → 특정 사용자 프로필 표시 (읽기 전용)

---

## Phase 3: ES 검색 안정화

> 게시판 키워드 검색이 안정적으로 동작하도록

### 3-1. Elasticsearch 서비스 점검 ✅ (2026-04-03)
- [x] `get_suggestions()` — completion suggester → match_phrase_prefix로 변경
- [x] `get_popular_searches()` — 하드코딩 → ES aggregation 기반
- [x] 게시글/FAQ 작성/수정/삭제 시 ES 인덱스 자동 동기화 확인 (이미 동작)

### 3-2. 검색 API 연결 ✅ (2026-04-03)
- [x] `/search/api/suggestions` — 검색 페이지 자동완성 (300ms debounce)
- [x] `/search/api/related` — 게시글 상세 페이지 관련 글 사이드바
- [x] `/search/api/popular` — 검색 페이지 인기 검색어 (ES tags aggregation)
- [x] 검색 결과 클릭 시 게시글 상세로 이동, FAQ 배지 표시

### 3-3. search.py 모듈 레벨 인스턴스 제거 ✅ (2026-04-03)
- [x] `LLMService()` 모듈 레벨 인스턴스 → 요청 시 lazy 로딩으로 변경
- [x] `ElasticsearchService()` 모듈 레벨 인스턴스 → 헬퍼 함수로 변경

---

## Phase 3.5: 한글 임베딩 모델 교체

> 현재 영어 전용 모델 → 한글 지원 모델로 교체

### 3.5-1. 현재 모델 문제점
- `distilgpt2` (생성): 영어 전용 82M, 한글 이해 불가
- `facebook/bart-large-cnn` (요약): 영어 뉴스 전용, 한글 불가
- `all-MiniLM-L6-v2` (임베딩): 영어 중심, 한글 유사도 부정확

### 3.5-2. 임베딩 모델 교체
- [ ] `all-MiniLM-L6-v2` → 한글 임베딩 모델 (예: `jhgan/ko-sroberta-multitask`)
- [ ] `llm_service.py` 모델 경로 업데이트
- [ ] 생성/요약 모델(`distilgpt2`, `bart-large-cnn`) 제거 (Phase 4에서 API LLM이 대체)
- [ ] 모델 미로드 시 fallback 응답 개선

---

## Phase 4: RAG 파이프라인 구축

> 현재는 "ES 키워드 검색 + LLM 프롬프트 붙여넣기" 수준.
> 진짜 RAG(Retrieval-Augmented Generation)를 구현한다.

### 4-1. 문서 임베딩 & 벡터 저장
- [ ] 게시글/FAQ를 임베딩 벡터로 변환하는 파이프라인
- [ ] ES에 `dense_vector` 필드 추가 또는 벡터 DB 도입
- [ ] 게시글 작성/수정/삭제 시 임베딩 자동 동기화

### 4-2. 게시판 시맨틱 검색 (`/search/semantic`)
- [ ] 검색 쿼리를 임베딩으로 변환
- [ ] 벡터 유사도 기반 관련 게시글 검색 (cosine similarity)
- [ ] ES 키워드 검색 + 벡터 검색 결합 (hybrid search)

### 4-3. 게시판 AI 검색 (`/search/ai`)
- [ ] RAG: 벡터 검색으로 관련 문서 검색 → LLM이 요약/답변 생성
- [ ] 기존 키워드 기반 컨텍스트 → 벡터 기반 컨텍스트로 전환

### 4-4. 챗봇 RAG 적용
- [ ] FAQ 모드: FAQ 임베딩 매칭 → 정확한 FAQ 직접 응답
- [ ] 문서 기반 모드: 벡터 검색으로 관련 문서 → LLM 컨텍스트 → 답변 생성
- [ ] 일반 답변 (concise, 100자) / 심화 답변 (detailed, 300자) 유지

---

## Phase 5: API LLM 연동

> 로컬 생성/요약 모델을 외부 API로 대체

### 5-1. API LLM 서비스 구현
- [ ] `api_llm_service.py`에 Claude API 연동
- [ ] GPT API 연동
- [ ] Gemini API 연동
- [ ] LLM 서비스 선택 로직 (환경변수로 전환)

### 5-2. 챗봇 개인화
- [ ] 챗봇 라우트에 `@login_required` 추가
- [ ] 현재 사용자 프로필 정보를 LLM 컨텍스트에 포함
- [ ] 프로필 기반 FAQ 응답 생성

---

## Phase 6: UI/UX 개선

### 6-1. 프론트엔드 정리
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
