# 초기 데이터 설정 문제 해결

## 문제 1: 데이터베이스 연결 실패

### 증상
```
❌ 데이터베이스 연결 실패: 'cryptography' package is required for sha256_password or caching_sha2_password auth methods
```

### 원인
- MySQL 8.0은 기본적으로 `caching_sha2_password` 인증 방식을 사용합니다
- `pymysql`이 이 인증 방식을 지원하려면 `cryptography` 패키지가 필요합니다
- `requirements.txt`에 `cryptography` 패키지가 누락되어 있었습니다

### 해결 방법

#### 방법 1: cryptography 패키지 추가 (권장) ✅

`requirements.txt`에 `cryptography>=41.0.0`를 추가하고 웹 컨테이너를 재빌드:

```bash
# 1. requirements.txt 확인 (이미 추가됨)
cat requirements.txt | grep cryptography

# 2. 웹 컨테이너 재빌드
docker compose build web

# 3. 웹 컨테이너 재시작
docker compose restart web

# 4. 초기 데이터 설정 재시도
docker compose exec web python init_data.py
```

#### 방법 2: MySQL 사용자 인증 방식 변경 (대안)

MySQL 사용자의 인증 방식을 `mysql_native_password`로 변경:

```bash
# MySQL에 접속
docker compose exec db mysql -u root -ppassword

# 사용자 인증 방식 변경
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
ALTER USER 'portfolio_user'@'%' IDENTIFIED WITH mysql_native_password BY 'portfolio_password';
FLUSH PRIVILEGES;
```

**주의**: 이 방법은 보안상 권장되지 않습니다. `cryptography` 패키지를 사용하는 것이 더 안전합니다.

## 문제 2: 로컬 모델 경고

### 증상
```
⚠️ 로컬 임베딩 모델을 찾을 수 없습니다. 기본 모델 사용...
⚠️ 로컬 생성 모델을 찾을 수 없습니다. 기본 모델 사용...
⚠️ 로컬 요약 모델을 찾을 수 없습니다. 기본 모델 사용...
```

### 원인
- 로컬 모델 파일이 `/app/models` 디렉토리에 없습니다
- 이는 정상적인 상황이며, 기본 모델을 사용한다는 경고입니다

### 해결 방법

#### 옵션 1: 경고 무시 (권장)
- 기본 모델을 사용하므로 기능상 문제가 없습니다
- 경고는 무시하고 계속 진행해도 됩니다

#### 옵션 2: 로컬 모델 다운로드
로컬 모델을 사용하려면:

```bash
# 모델 다운로드 스크립트 실행
docker compose exec web python scripts/download_models.py
```

또는 수동으로 모델을 다운로드:

```bash
# models 디렉토리 확인
ls -la models/

# 모델이 없으면 다운로드
# (스크립트에 따라 다를 수 있음)
```

## 확인 사항

### cryptography 패키지 설치 확인
```bash
# 웹 컨테이너에서 확인
docker compose exec web pip list | grep cryptography
```

### 데이터베이스 연결 테스트
```bash
# 웹 컨테이너에서 직접 테스트
docker compose exec web python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.engine.connect()
        print('✅ 데이터베이스 연결 성공')
    except Exception as e:
        print(f'❌ 데이터베이스 연결 실패: {e}')
"
```

### 초기 데이터 설정 재시도
```bash
# 웹 컨테이너에서 실행
docker compose exec web python init_data.py
```

## 예상 결과

수정 후:
- ✅ 데이터베이스 연결 성공
- ✅ 초기 데이터 설정 완료
- ⚠️ 로컬 모델 경고 (정상, 무시 가능)

