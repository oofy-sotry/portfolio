# 리팩토링 계획

## 개요

프로젝트의 미완성 코드, 구버전 잔재, 구조적 문제를 정리하고
로드맵(사용자별 프로필, ES 검색, 개인화 챗봇)을 구현하기 위한 리팩토링 계획.

---

## Phase 1: 기반 정리

> 이후 작업의 토대가 되는 정리 작업

### 1-1. docker-compose.llm.yml 삭제 ✅- [x] `docker-compose.llm.yml` 삭제
  - MariaDB 10.11 기반의 구버전 설정 (현재 MySQL 8.0 사용)
  - Keycloak 설정 누락
  - GPU LLM 컨테이너 방식은 사용하지 않음 (향후 API 방식으로 전환)

### 1-2. 검색 기능 정상화 ✅- [x] `search/advanced.html` 템플릿 생성
- [x] `base.html` 네비게이션에 검색 링크 추가
- [x] Blueprint url_prefix 중복 라우트 경로 수정 (`/search/search` → `/search`)

### 1-3. README.md 업데이트 ✅- [x] 삭제된 문서 참조 제거
- [x] 현재 프로젝트 구조에 맞게 업데이트

---

## Phase 2: 사용자별 프로필 시스템

> 로드맵 목표 1 — 단일 프로필 → 사용자별 1:1 프로필

### 2-1. Profile 모델에 user_id 추가 ✅- [x] `Profile` 모델에 `user_id` 컬럼 추가 (User와 1:1 관계)
- [x] `User` 모델에 `profile` 관계 추가 (`uselist=False`)
- [x] `get_active_profile()` → `get_user_profile(user_id)` 전환

### 2-2. 프로필 라우트 수정 ✅- [x] `profile.py` 라우트에서 `current_user.id` 기반으로 변경 (9곳)
- [x] 회원가입 시 User + Profile 동시 생성
- [x] Keycloak 로그인 시에도 Profile 자동 생성

### 2-3. About 페이지 사용자별 분리 ✅- [x] `/about` → 로그인 사용자 프로필 표시
- [x] `/about/<username>` → 특정 사용자 프로필 표시 (읽기 전용)

---

## Phase 3: ES 검색 안정화

> 게시판 키워드 검색이 안정적으로 동작하도록

### 3-1. Elasticsearch 서비스 점검 ✅- [x] `get_suggestions()` — completion suggester → match_phrase_prefix로 변경
- [x] `get_popular_searches()` — 하드코딩 → ES aggregation 기반
- [x] 게시글/FAQ 작성/수정/삭제 시 ES 인덱스 자동 동기화 확인 (이미 동작)

### 3-2. 검색 API 연결 ✅- [x] `/search/api/suggestions` — 검색 페이지 자동완성 (300ms debounce)
- [x] `/search/api/related` — 게시글 상세 페이지 관련 글 사이드바
- [x] `/search/api/popular` — 검색 페이지 인기 검색어 (ES tags aggregation)
- [x] 검색 결과 클릭 시 게시글 상세로 이동, FAQ 배지 표시

### 3-3. search.py 모듈 레벨 인스턴스 제거 ✅- [x] `LLMService()` 모듈 레벨 인스턴스 → 요청 시 lazy 로딩으로 변경
- [x] `ElasticsearchService()` 모듈 레벨 인스턴스 → 헬퍼 함수로 변경

---

## Phase 3.5: 한글 임베딩 모델 교체

> 현재 영어 전용 모델 → 한글 지원 모델로 교체

### 3.5-1. 모델 교체 완료 ✅
| 용도 | 이전 (영어) | 이후 (한글) |
|------|-----------|-----------|
| 임베딩 | all-MiniLM-L6-v2 | jhgan/ko-sroberta-multitask |
| 생성 | distilgpt2 | skt/kogpt2-base-v2 |
| 요약 | facebook/bart-large-cnn | digit82/kobart-summarization |

- [x] 임베딩 모델 한글 교체
- [x] 생성 모델 한글 교체 (KoGPT2 — 기본 답변용)
- [x] 요약 모델 한글 교체 (KoBART)
- [x] 미사용 get_similarity_score() 제거
- [x] 모델 선택 가이드 문서(MODEL_GUIDE.md) 작성 (A/B 조합)

---

## Phase 4: RAG 파이프라인 구축

> 현재는 "ES 키워드 검색 + LLM 프롬프트 붙여넣기" 수준.
> 진짜 RAG(Retrieval-Augmented Generation)를 구현한다.

### 4-1. 문서 임베딩 & 벡터 저장 ✅- [x] ChromaDB Docker 서비스 추가 (docker-compose.yml)
- [x] VectorStore 서비스 클래스 생성 (app/services/vector_store.py)
- [x] 게시글 작성/수정/삭제 시 ChromaDB 자동 동기화 (indexing_utils.py)
- [x] FAQ 생성/수정/삭제 시 ChromaDB 자동 동기화

### 4-2. 게시판 시맨틱 검색 ✅- [x] `/search/semantic` — ChromaDB cosine similarity 기반 벡터 검색
- [x] ChromaDB 실패 시 ES 키워드 검색 폴백

### 4-3. 게시판 AI 검색 (RAG) ✅- [x] `/search/ai` — ChromaDB 벡터 검색(Retrieval) → LLM 답변 생성(Generation)
- [x] ChromaDB 실패 시 ES 폴백

### 4-4. 챗봇 RAG 적용 ✅- [x] search 모드: ChromaDB 벡터 검색 → LLM 컨텍스트 → 답변 생성
- [x] faq 모드: ES 기반 FAQ 매칭 유지 (정확한 키워드 매칭에 적합)
- [x] 일반 답변 (concise, 100자) / 심화 답변 (detailed, 300자) 유지

---

## Phase 5: API LLM 연동

> 로컬 모델(기본 답변)은 유지하고, API LLM(고급 답변)을 추가

### 5-1. API LLM 서비스 구현 ✅
- [x] `api_llm_service.py` 공통 인터페이스(dispatch 패턴)로 재설계
- [x] Claude API 연동 (claude-sonnet-4, Anthropic Messages API)
- [x] ChatGPT API 연동 (gpt-4o-mini, OpenAI Chat Completions API)
- [x] Gemini API 연동 (gemini-2.0-flash, Google Generative Language API)
- [x] 기본 답변(로컬 KoGPT2) / 고급 답변(API LLM) 선택 로직
- [x] 고급 챗봇 UI에 AI 제공자 선택 드롭다운 추가

### 5-2. 챗봇 개인화 (포트폴리오 어시스턴트)

> 챗봇은 사용자 본인이 아닌 **제3자 어시스턴트** 역할.
> 사용자 프로필을 알고 있지만, 사용자로서 대답하지 않는다.

- [ ] 챗봇 라우트에 `@login_required` 추가
- [ ] 사용자 프로필 정보를 LLM 시스템 프롬프트에 컨텍스트로 주입
- [ ] 시스템 프롬프트에 "사용자의 포트폴리오 어시스턴트" 역할 명시
- [ ] 프로필 기반 질문 응답 (기술 스택 조회, 프로필 조언 등)

---

## Phase 6: UI/UX 개선

### 6-1. 프론트엔드 정리
- [ ] 검색 결과 UI 개선
- [ ] 챗봇 UI 개선
- [ ] 반응형 디자인 점검

---

## 완료된 작업

- [x] 미사용 코드/중복 파일/불필요한 문서 정리  - 중복 스크립트 6개 삭제
  - 구버전 마이그레이션 문서 10개 삭제
  - 미사용 import 정리 (auth.py, main.py, search.py)
  - main.py의 /search 라우트 충돌 제거
