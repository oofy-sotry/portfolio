# Elasticsearch 자동완성(Autocomplete) 구현 가이드

## 개요

Elasticsearch에서 자동완성을 구현하는 3가지 방법을 비교하고,
현재 프로젝트의 매핑 기준으로 각 방법의 전환 방법을 정리한다.

**현재 프로젝트 상태**: `match_phrase_prefix` 사용 중 (`get_suggestions()`)

---

## 1. match_phrase_prefix (현재 사용 중)

### 동작 원리

일반 `match_phrase` 쿼리와 동일하되, **마지막 텀(term)에 대해 prefix 매칭**을 수행한다.

1. 입력 텍스트를 analyzer로 분석하여 토큰 목록 생성
2. 마지막 토큰을 제외한 나머지 토큰은 정확한 phrase 매칭
3. 마지막 토큰은 해당 prefix로 시작하는 모든 텀을 inverted index에서 탐색 (prefix expansion)
4. 확장된 텀들과 나머지 토큰이 순서대로 나타나는 문서를 반환

예: `"Flask 게시"` 입력 시 → `Flask` → `게시*` (게시판, 게시글, ...) 순서로 매칭

### 인덱스 매핑

별도 매핑 불필요. 기존 `text` 필드에서 바로 사용 가능.

```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "standard"
      }
    }
  }
}
```

### 쿼리 예시

```json
{
  "query": {
    "match_phrase_prefix": {
      "title": {
        "query": "Flask 게시",
        "max_expansions": 10,
        "slop": 0
      }
    }
  },
  "_source": ["title"],
  "size": 5
}
```

**주요 파라미터:**

| 파라미터 | 설명 | 기본값 |
|---|---|---|
| `query` | 검색할 텍스트 | (필수) |
| `max_expansions` | 마지막 텀의 prefix 확장 최대 수 | 50 |
| `slop` | 토큰 간 허용 위치 간격 | 0 |
| `analyzer` | 쿼리 분석에 사용할 analyzer | 필드의 search_analyzer |

### 장점

- **즉시 사용 가능**: 기존 `text` 필드에 매핑 변경 없이 적용
- **구현이 단순**: 쿼리만 변경하면 됨
- **phrase 순서 보장**: 토큰 순서가 보장되어 의미 있는 결과 반환

### 단점

- **성능 이슈**: prefix가 짧을수록(예: 단일 문자) inverted index 순회 비용 증가
- **max_expansions 한계**: shard 단위 적용, 확장 순서가 예측 어려움
- **스코어링 부정확**: prefix 확장된 텀들의 스코어링이 완전 일치보다 부정확

### 적합한 사용 사례

- 빠른 프로토타이핑 / POC
- 소규모 인덱스 (수만~수십만 문서)
- 기존 매핑을 변경할 수 없는 상황

---

## 2. Completion Suggester

### 동작 원리

**FST(Finite State Transducer)** 기반의 인메모리 자료구조를 사용한다.
일반 검색 쿼리와는 완전히 다른 경로로 동작한다.

1. `completion` 타입 필드에 문서를 인덱싱하면 FST로 컴파일되어 **메모리에 상주**
2. 검색 시 `_search` API의 `suggest` 파라미터 사용
3. FST를 통해 prefix를 탐색하므로 검색 속도가 인덱스 크기와 **무관**
4. 결과는 사전 정의한 `weight`(가중치)에 따라 정렬

> FST는 trie와 유사하지만 메모리 효율이 훨씬 높은 자료구조

### 인덱스 매핑

기존 매핑에 `completion` 타입 필드를 **추가**해야 한다. (재인덱싱 필수)

```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "standard"
      },
      "title_suggest": {
        "type": "completion",
        "analyzer": "standard",
        "preserve_separators": true,
        "max_input_length": 50
      },
      "content": {
        "type": "text",
        "analyzer": "standard"
      },
      "tags": {
        "type": "keyword"
      }
    }
  }
}
```

**매핑 옵션:**

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `analyzer` | 인덱싱 시 analyzer | `simple` |
| `search_analyzer` | 검색 시 analyzer | `analyzer` 값 |
| `preserve_separators` | 구분자 보존 여부 | `true` |
| `max_input_length` | 입력 최대 길이 | 50 |

**인덱싱 시 input/weight 지정:**

```json
{
  "title": "Flask로 포트폴리오 만들기",
  "title_suggest": {
    "input": ["Flask로 포트폴리오 만들기", "포트폴리오 만들기"],
    "weight": 10
  }
}
```

### 쿼리 예시

```json
{
  "suggest": {
    "title-suggestion": {
      "prefix": "Flask",
      "completion": {
        "field": "title_suggest",
        "size": 5,
        "skip_duplicates": true,
        "fuzzy": {
          "fuzziness": "AUTO",
          "min_length": 3,
          "prefix_length": 1
        }
      }
    }
  }
}
```

**Context Suggester (카테고리 필터링):**

```json
{
  "mappings": {
    "properties": {
      "title_suggest": {
        "type": "completion",
        "contexts": [
          {
            "name": "category",
            "type": "category",
            "path": "tags"
          }
        ]
      }
    }
  }
}
```

### 장점

- **극한의 속도**: FST 메모리 상주로 ~1ms 이하 응답. 인덱스 크기 무관
- **Fuzzy 내장**: 오타 허용 자동완성 지원
- **Context 필터링**: 카테고리/지리 기반 필터링
- **가중치 정렬**: `weight` 필드로 인기도/중요도 기반 정렬

### 단점

- **메모리 사용량 높음**: FST 전체가 힙 메모리에 로드
- **별도 필드 필요**: `completion` 타입 전용 필드 + 재인덱싱
- **일반 쿼리와 통합 불가**: `bool` 쿼리 내부에서 사용 불가, 필터/집계 결합 제한적
- **prefix 매칭만 가능**: 중간 단어 매칭은 `input` 배열에 별도 등록 필요
- **응답 형태 다름**: `hits`가 아닌 `suggest` 형태로 반환 → 클라이언트 코드 수정 필요

### 적합한 사용 사례

- 검색창 자동완성 드롭다운 (네이버/구글 스타일)
- 제품명, 도시명, 사용자 이름 등 정의된 제안어 목록
- 극도로 빠른 응답이 필요한 경우 (SLA < 5ms)
- 인기 검색어 기반 자동완성 (weight 활용)

---

## 3. search_as_you_type 필드 타입

### 동작 원리

Elasticsearch 7.2에서 도입된 전용 필드 타입.
하나의 필드를 매핑하면 **여러 서브필드를 자동 생성**하여 n-gram/shingle 기반 매칭을 지원한다.

`title` 필드 매핑 시 자동 생성되는 서브필드:

| 서브필드 | 역할 |
|---|---|
| `title` | 루트 필드 (일반 text 분석) |
| `title._2gram` | 2개 토큰 shingle로 인덱싱 |
| `title._3gram` | 3개 토큰 shingle로 인덱싱 |
| `title._index_prefix` | 마지막 토큰의 edge n-gram (min 1, max 19) |

쿼리 시 `multi_match` + `bool_prefix`를 사용하면 ES가 자동으로 적절한 서브필드를 선택한다.
**인덱싱 시점에 prefix와 shingle을 미리 생성**하므로 런타임 expansion 비용이 없다.

### 인덱스 매핑

`title` 필드 타입을 `search_as_you_type`으로 변경한다. (재인덱싱 필수)

```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "search_as_you_type",
        "analyzer": "standard",
        "max_shingle_size": 3
      },
      "content": {
        "type": "text",
        "analyzer": "standard"
      },
      "tags": {
        "type": "keyword"
      }
    }
  }
}
```

**매핑 옵션:**

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `analyzer` | 텍스트 분석기 | `standard` |
| `max_shingle_size` | 최대 shingle 크기 (2~4) | 3 |

### 쿼리 예시

**권장: multi_match + bool_prefix**

```json
{
  "query": {
    "multi_match": {
      "query": "Flask 게시",
      "type": "bool_prefix",
      "fields": [
        "title",
        "title._2gram",
        "title._3gram"
      ]
    }
  }
}
```

`bool_prefix`는 내부적으로 마지막 텀을 `prefix` 쿼리로, 나머지를 `term` 쿼리로 변환한다.
순서 무관 매칭을 하되, 순서가 맞으면 더 높은 점수를 부여한다.

### 장점

- **인덱스 타임 최적화**: 런타임 expansion 비용 없음
- **일반 검색 API 사용**: `_search` API의 `query` 내에서 사용 → `bool`, `filter`, `aggs` 결합 자유
- **단어 순서 유연**: 순서 무관 매칭 + 순서 일치 시 가산점
- **설정 간편**: 필드 타입만 지정하면 서브필드 자동 생성
- **기존 쿼리 호환**: 루트 필드가 일반 `text`와 동일하게 동작 → 기존 `multi_match` 검색도 그대로 작동

### 단점

- **디스크 증가**: shingle + edge n-gram 서브필드로 약 2~4배 증가
- **인덱싱 속도 감소**: 약 20~40% 느림
- **Completion Suggester만큼 빠르지 않음**: 여전히 inverted index 기반
- **가중치 제어 한계**: 명시적 `weight` 지정 불가 (BM25 스코어 의존)
- **매핑 변경 필요**: 재인덱싱 필수

### 적합한 사용 사례

- 일반 검색과 자동완성을 하나의 쿼리로 통합하고 싶을 때
- 필터, 집계를 자동완성에 함께 적용해야 할 때
- `match_phrase_prefix`의 성능 한계를 넘어야 할 때

---

## 비교 요약

| 항목 | match_phrase_prefix | Completion Suggester | search_as_you_type |
|---|---|---|---|
| **쿼리 속도** | 느림 (수십~수백 ms) | 가장 빠름 (~1 ms) | 중간 (수~수십 ms) |
| **메모리 사용** | 추가 없음 | 높음 (FST 힙 상주) | 추가 없음 |
| **디스크 사용** | 추가 없음 | 추가 있음 (FST) | 2~4배 증가 |
| **매핑 변경** | 불필요 | 별도 `completion` 필드 필요 | `search_as_you_type` 변경 필요 |
| **재인덱싱** | 불필요 | 필요 | 필요 |
| **일반 쿼리 통합** | 가능 (query DSL) | 불가 (suggest API) | 가능 (query DSL) |
| **필터/집계 결합** | 가능 | 제한적 | 가능 |
| **Fuzzy 지원** | 미지원 | 내장 지원 | `fuzziness` 파라미터 가능 |
| **가중치 제어** | BM25 스코어 | 명시적 weight | BM25 스코어 |
| **도입 난이도** | 매우 쉬움 | 중간 | 쉬움 |
| **대규모 인덱스** | 부적합 | 적합 | 적합 |

---

## 현재 프로젝트 기준 전환 가이드

### 현재 매핑

```json
{
  "title":   { "type": "text",    "analyzer": "standard" },
  "content": { "type": "text",    "analyzer": "standard" },
  "tags":    { "type": "keyword" }
}
```

### 방법 A → B (Completion Suggester)

1. 새 인덱스를 `title_suggest: { type: completion }` 매핑으로 생성
2. `_reindex` API로 데이터 복사 + `title` 값을 `title_suggest`에도 복사
3. 인덱스 alias 전환
4. 클라이언트 코드를 `suggest` API 호출로 변경

### 방법 A → C (search_as_you_type)

1. 새 인덱스를 `title: { type: search_as_you_type }` 매핑으로 생성
2. `_reindex` API로 데이터 복사 (필드명 동일 → 스크립트 불필요)
3. 인덱스 alias 전환
4. 자동완성 쿼리를 `multi_match` + `bool_prefix`로 변경
5. **기존 일반 검색 쿼리는 수정 불필요** (루트 필드가 text와 동일하게 동작)

---

## 권장 사항

| 상황 | 권장 방법 |
|---|---|
| 현재 프로젝트 (소규모, 빠른 개발) | `match_phrase_prefix` (현재) |
| 성능 개선 필요 시 | `search_as_you_type` (전환 비용 최소) |
| 극한 속도 + 인기 검색어 가중치 | Completion Suggester |

현재 프로젝트는 소규모 포트폴리오 사이트이므로 `match_phrase_prefix`로 충분하다.
향후 문서 수가 크게 증가하거나 응답 속도가 문제될 경우 `search_as_you_type`으로의 전환을 권장한다.
