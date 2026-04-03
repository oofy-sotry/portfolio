# 로컬 LLM 모델 가이드

## 현재 사용 중인 모델 (A 조합 — 경량)

| 용도 | 모델 | 파라미터 | 디스크 | RAM | CPU 응답 속도 |
|------|------|---------|--------|-----|-------------|
| 임베딩 | `jhgan/ko-sroberta-multitask` | 110M | ~440MB | ~500MB | ~0.1초 |
| 생성 | `skt/kogpt2-base-v2` | 125M | ~500MB | ~600MB | 2~5초 |
| 요약 | `digit82/kobart-summarization` | 124M | ~500MB | ~600MB | 2~5초 |
| **합계** | | **359M** | **~1.4GB** | **~1.7GB** | |

### A 조합 선택 이유

- **메모리**: Docker 환경에서 MySQL + ES + Keycloak + Kibana + Nginx가 ~1.7GB 사용.
  16GB 시스템 기준 모델까지 포함해 총 ~3.4GB로 충분한 여유.
- **속도**: CPU 환경에서 2~5초 응답. 웹 서비스로 실사용 가능한 수준.
- **한글 지원**: 세 모델 모두 한글 학습 데이터로 훈련됨.
- **역할 분담**: 로컬 모델은 기본 답변 담당, 향후 API LLM(Claude/GPT)이 고급 답변 담당.

---

## B 조합 — 고품질 (서버 여유 시 업그레이드)

| 용도 | 모델 | 파라미터 | 디스크 | RAM | CPU 응답 속도 |
|------|------|---------|--------|-----|-------------|
| 임베딩 | `jhgan/ko-sroberta-multitask` | 110M | ~440MB | ~500MB | ~0.1초 |
| 생성 | `skt/ko-gpt-trinity-1.2B-v0.5` | 1.2B | ~4.8GB | ~5.5GB | 30~60초 |
| 요약 | `digit82/kobart-summarization` | 124M | ~500MB | ~600MB | 2~5초 |
| **합계** | | **1.4B** | **~5.7GB** | **~6.6GB** | |

### B 조합 특징

- **생성 품질**: KoGPT2(125M) 대비 약 10배 큰 모델. 문장 완성도와 문맥 이해력이 크게 향상.
- **필요 사양**: 최소 32GB RAM 권장 (Docker 서비스 + 모델 합계 ~8.3GB, 시스템 여유 필요).
- **응답 속도**: CPU에서 30~60초로 느림. GPU(CUDA) 사용 시 3~10초로 개선 가능.
- **전환 방법**: `llm_service.py`에서 `GENERATION_MODEL_NAME`을 변경하면 됨.

### B 조합으로 전환하는 방법

```python
# llm_service.py에서 아래 한 줄만 변경
GENERATION_MODEL_NAME = 'skt/ko-gpt-trinity-1.2B-v0.5'  # A → B
```

### B 조합 필요 사양 정리

| 항목 | 최소 | 권장 |
|------|------|------|
| RAM | 16GB | 32GB |
| 디스크 | 10GB 여유 | 15GB 여유 |
| GPU | 없어도 동작 (느림) | NVIDIA 8GB+ VRAM |
| Docker 메모리 할당 | 12GB | 16GB |

---

## 모델 역할 구조

```
사용자 질문
    │
    ├── [기본 답변] 로컬 모델 (KoGPT2/Trinity)
    │   └── 빠른 응답, 오프라인 가능
    │
    └── [고급 답변] API LLM (Claude/GPT/Gemini) — Phase 5에서 구현
        └── 높은 품질, 인터넷 필요, 비용 발생
```
