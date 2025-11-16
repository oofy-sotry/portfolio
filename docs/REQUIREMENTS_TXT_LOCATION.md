# requirements.txt 파일 참조 위치

## 개요

이 문서는 프로젝트에서 `requirements.txt` 파일이 어디서 참조되는지 설명합니다.

## 파일 위치

`requirements.txt`는 **프로젝트 루트 디렉토리**에 위치합니다:
```
portfolio_website/
├── requirements.txt  ← 여기
├── docker-compose.yml
├── Dockerfile
├── scripts/
│   └── start_service.sh
└── ...
```

## 참조 위치

### 1. Dockerfile (라인 15, 18)

```15:18:Dockerfile
# Python 의존성 파일 복사
COPY requirements.txt .

# Python 의존성 설치 (CPU 전용 PyTorch)
RUN pip install --no-cache-dir -r requirements.txt && \
```

**설명:**
- Docker 빌드 컨텍스트는 `docker-compose.yml`의 `build: .`로 지정된 디렉토리(프로젝트 루트)입니다.
- `COPY requirements.txt .`는 프로젝트 루트의 `requirements.txt`를 컨테이너의 `/app/requirements.txt`로 복사합니다.
- 빌드 시 프로젝트 루트에서 실행되므로 상대 경로 `requirements.txt`가 정확히 참조됩니다.

### 2. docker-compose.yml (간접 참조)

```3:3:docker-compose.yml
    build: .
```

**설명:**
- `build: .`는 현재 디렉토리(프로젝트 루트)를 빌드 컨텍스트로 사용합니다.
- Dockerfile이 이 컨텍스트에서 `requirements.txt`를 찾습니다.
- `docker compose build web` 명령은 프로젝트 루트에서 실행해야 합니다.

### 3. start_service.sh (라인 458-459)

```457:465:scripts/start_service.sh
# cryptography 패키지가 requirements.txt에 있는지 확인
REQUIREMENTS_FILE="${PROJECT_ROOT}/requirements.txt"
if [ -f "${REQUIREMENTS_FILE}" ] && grep -q "cryptography" "${REQUIREMENTS_FILE}"; then
    echo "   cryptography 패키지가 requirements.txt에 있습니다."
    echo "   웹 컨테이너를 재빌드해야 합니다..."
    echo "   ⏳ 웹 컨테이너 재빌드 중... (시간이 걸릴 수 있습니다)"
    docker compose build web
    if [ $? -ne 0 ]; then
        echo "⚠️ 웹 컨테이너 재빌드 실패. 기존 이미지로 계속 진행합니다..."
    else
        echo "✅ 웹 컨테이너 재빌드 완료"
```

**설명:**
- 스크립트 시작 부분(라인 6-15)에서 프로젝트 루트를 자동으로 찾아 `PROJECT_ROOT` 변수에 저장합니다.
- `REQUIREMENTS_FILE="${PROJECT_ROOT}/requirements.txt"`로 절대 경로를 사용합니다.
- 스크립트가 어디서 실행되든 항상 올바른 `requirements.txt`를 참조합니다.

## 스크립트 실행 위치 처리

### 이전 문제점

이전에는 `start_service.sh`에서 상대 경로 `requirements.txt`를 사용했기 때문에:
- `scripts/` 디렉토리에서 실행하면 `requirements.txt`를 찾을 수 없었습니다.
- 프로젝트 루트에서만 실행해야 했습니다.

### 현재 해결 방법

```6:15:scripts/start_service.sh
# 스크립트가 있는 디렉토리 찾기
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 프로젝트 루트 디렉토리 (scripts의 상위 디렉토리)
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# 프로젝트 루트로 이동
cd "${PROJECT_ROOT}" || {
    echo "❌ 프로젝트 루트 디렉토리로 이동할 수 없습니다."
    exit 1
}
```

**장점:**
- 스크립트가 어디서 실행되든 자동으로 프로젝트 루트를 찾습니다.
- 절대 경로를 사용하여 경로 문제를 방지합니다.
- `docker compose` 명령도 프로젝트 루트에서 실행됩니다.

## 실행 방법

### 올바른 실행 방법

어디서든 실행 가능:
```bash
# 프로젝트 루트에서
bash scripts/start_service.sh

# scripts 디렉토리에서
cd scripts
bash start_service.sh

# 다른 디렉토리에서
bash /path/to/portfolio_website/scripts/start_service.sh
```

### Docker Compose 빌드

프로젝트 루트에서 실행:
```bash
# 프로젝트 루트로 이동
cd /path/to/portfolio_website

# 웹 컨테이너 빌드
docker compose build web
```

## 요약

| 파일 | 참조 방식 | 위치 |
|------|----------|------|
| `Dockerfile` | 상대 경로 `requirements.txt` | 프로젝트 루트 기준 |
| `docker-compose.yml` | `build: .` (간접) | 프로젝트 루트 기준 |
| `start_service.sh` | 절대 경로 `${PROJECT_ROOT}/requirements.txt` | 자동 감지 |

**결론:** 모든 참조는 프로젝트 루트의 `requirements.txt`를 가리키며, `start_service.sh`는 실행 위치와 무관하게 올바른 파일을 찾습니다.

