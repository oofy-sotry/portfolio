# 웹 애플리케이션 접근 불가 문제 해결

## 증상
- 서비스는 정상적으로 시작되었다고 표시됨
- 브라우저에서 `ERR_CONNECTION_REFUSED` 오류 발생
- `http://192.168.0.22:5000` 접근 불가

## 가능한 원인

### 1. 웹 컨테이너가 실행되지 않음
**확인 방법:**
```bash
docker compose ps web
```

**해결 방법:**
```bash
# 웹 컨테이너 재시작
docker compose restart web

# 로그 확인
docker compose logs -f web
```

### 2. 웹 애플리케이션이 시작 중이거나 에러로 종료됨
**확인 방법:**
```bash
# 웹 컨테이너 로그 확인
docker compose logs web

# 최근 에러 확인
docker compose logs web | grep -i error
```

**가능한 에러:**
- `cryptography` 패키지 누락 → 웹 컨테이너 재빌드 필요
- 데이터베이스 연결 실패
- `init_db.py` 또는 `download_models.py` 실행 실패

**해결 방법:**
```bash
# 1. 웹 컨테이너 재빌드 (cryptography 패키지 설치)
docker compose build web

# 2. 웹 컨테이너 재시작
docker compose restart web

# 3. 로그 확인
docker compose logs -f web
```

### 3. 포트 5000이 바인딩되지 않음
**확인 방법:**
```bash
# 포트 바인딩 확인
docker compose ps web | grep 5000

# 호스트에서 포트 확인
netstat -tlnp | grep 5000  # Linux
netstat -ano | findstr :5000  # Windows
```

**해결 방법:**
```bash
# 포트 충돌 확인 및 해결
# 다른 프로세스가 5000 포트를 사용 중인지 확인
```

### 4. Dockerfile의 CMD 명령어 실패
**확인 방법:**
```bash
# 웹 컨테이너 로그에서 확인
docker compose logs web | grep -E "init_db|download_models|gunicorn"
```

**가능한 문제:**
- `init_db.py` 실행 실패
- `download_models.py` 실행 실패 (시간이 오래 걸릴 수 있음)
- `gunicorn` 시작 실패

**해결 방법:**
```bash
# 수동으로 실행하여 에러 확인
docker compose exec web python init_db.py
docker compose exec web python scripts/download_models.py
docker compose exec web gunicorn --bind 0.0.0.0:5000 --workers 1 run:app
```

### 5. 방화벽 또는 네트워크 문제
**확인 방법:**
```bash
# 로컬에서 접근 테스트
curl http://localhost:5000

# 컨테이너 내부에서 접근 테스트
docker compose exec web curl http://localhost:5000
```

**해결 방법:**
- Windows 방화벽 설정 확인
- Docker Desktop 네트워크 설정 확인
- IP 주소가 올바른지 확인

## 빠른 진단 명령어

```bash
# 1. 웹 컨테이너 상태 확인
docker compose ps web

# 2. 웹 컨테이너 로그 확인
docker compose logs --tail=100 web

# 3. 웹 컨테이너 내부 프로세스 확인
docker compose exec web ps aux

# 4. 포트 5000 리스닝 확인
docker compose exec web netstat -tlnp | grep 5000

# 5. 로컬 연결 테스트
curl http://localhost:5000

# 6. 진단 스크립트 실행
bash scripts/check_web_status.sh
```

## 단계별 해결 방법

### 1단계: 웹 컨테이너 상태 확인
```bash
docker compose ps web
```

**예상 결과:**
- `Up` 상태여야 함
- `PORTS`에 `0.0.0.0:5000->5000/tcp` 표시되어야 함

### 2단계: 웹 컨테이너 로그 확인
```bash
docker compose logs --tail=100 web
```

**확인할 내용:**
- `gunicorn` 시작 메시지
- `ERROR` 또는 `Exception` 메시지
- 데이터베이스 연결 메시지

### 3단계: 웹 컨테이너 재빌드 (cryptography 패키지 설치)
```bash
# requirements.txt에 cryptography가 추가되었으므로 재빌드 필요
docker compose build web
docker compose up -d web
```

### 4단계: 웹 애플리케이션 수동 시작 테스트
```bash
# 컨테이너 내부에서 직접 실행하여 에러 확인
docker compose exec web bash
# 컨테이너 내부에서:
python init_db.py
gunicorn --bind 0.0.0.0:5000 --workers 1 run:app
```

### 5단계: 포트 및 네트워크 확인
```bash
# 호스트에서 포트 확인
netstat -tlnp | grep 5000  # Linux
netstat -ano | findstr :5000  # Windows

# Docker 네트워크 확인
docker network ls
docker network inspect portfolio_website_default
```

## 일반적인 해결 방법

### 방법 1: 웹 컨테이너 재빌드 및 재시작 (권장)
```bash
# 1. 웹 컨테이너 중지
docker compose stop web

# 2. 웹 컨테이너 재빌드 (cryptography 패키지 설치)
docker compose build web

# 3. 웹 컨테이너 시작
docker compose up -d web

# 4. 로그 확인
docker compose logs -f web
```

### 방법 2: 전체 서비스 재시작
```bash
# 모든 서비스 중지
docker compose down

# 모든 서비스 재시작
bash scripts/start_service.sh
```

### 방법 3: 웹 애플리케이션만 수동 시작
```bash
# 웹 컨테이너 내부에서 직접 실행
docker compose exec web bash
# 컨테이너 내부에서:
cd /app
python init_db.py
gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 run:app
```

## 예상 결과

정상 작동 시:
- `docker compose ps web`에서 `Up` 상태
- 로그에 `gunicorn` 시작 메시지
- `curl http://localhost:5000` 성공
- 브라우저에서 접근 가능

## 추가 확인 사항

### IP 주소 확인
```bash
# 현재 IP 주소 확인
hostname -I  # Linux
ipconfig  # Windows

# docker-compose.yml에서 포트 매핑 확인
cat docker-compose.yml | grep -A 5 "web:"
```

### 방화벽 설정
- Windows: 방화벽에서 포트 5000 허용 확인
- Linux: `ufw` 또는 `iptables` 설정 확인

### Docker Desktop 설정
- Docker Desktop > Settings > Resources > Network
- 포트 포워딩 설정 확인

