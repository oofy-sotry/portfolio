# 개발자 포트폴리오 웹사이트

Flask를 사용한 풀스택 웹 애플리케이션으로, 개인 포트폴리오를 위한 웹사이트입니다.

## 주요 기능

- **사용자 인증**: 로그인/회원가입, JWT 기반 인증
- **게시판**: CRUD 기능, 댓글, 좋아요, 카테고리별 분류
- **검색**: 키워드 및 태그 기반 검색
- **챗봇**: FAQ 챗봇 (OpenAI API 연동 가능)
- **반응형 디자인**: Bootstrap 기반 모바일 친화적 UI

## 기술 스택

- **Backend**: Python 3.11, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: MySQL 8.0
- **Search Engine**: Elasticsearch 8.11.0
- **Authentication**: Keycloak 24.0 (OAuth 2.0 / OpenID Connect)
- **Deployment**: Docker, Docker Compose, Nginx
- **AI/ML**: Transformers, Sentence Transformers (챗봇 기능)

## 프로젝트 구조

```
portfolio_website/
├── app/
│   ├── models/          # 데이터베이스 모델
│   ├── routes/           # 라우트 핸들러
│   ├── templates/        # HTML 템플릿
│   └── static/          # CSS, JS, 이미지
├── config/              # 설정 파일
├── docs/                # 문서
├── scripts/             # 유틸리티 스크립트
├── docker-compose.yml   # Docker Compose 설정
├── Dockerfile          # Docker 이미지 설정
├── requirements.txt    # Python 의존성
└── run.py             # 애플리케이션 실행
```

## 설치 및 실행

### 1. 로컬 개발 환경

```bash
# 저장소 클론
git clone <repository-url>
cd portfolio_website

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp env.example .env
# .env 파일을 편집하여 설정값 입력

# 데이터베이스 초기화
flask init-db

# 애플리케이션 실행
python run.py
```

### 2. Docker를 사용한 실행 (권장)

**자동 시작 스크립트 사용 (권장):**

```bash
# 모든 서비스를 올바른 순서로 자동 시작
bash scripts/start_service.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
- MySQL, Elasticsearch, Keycloak 시작 및 준비 대기
- 데이터베이스 초기화
- Keycloak 설정 (Realm, Client, 사용자 생성)
- 웹 애플리케이션 시작
- Nginx 시작

**수동 실행:**

```bash
# Docker Compose로 전체 스택 실행
docker compose up -d

# 로그 확인
docker compose logs -f

# 서비스 중지
docker compose down
```

자세한 내용은 [docs/START_SERVICE_GUIDE.md](docs/START_SERVICE_GUIDE.md)를 참고하세요.

## 데이터베이스 설정

### MySQL 8.0 설정

데이터베이스는 `init_mysql.sql` 스크립트로 자동 생성됩니다. 수동으로 설정하려면:

```sql
CREATE DATABASE portfolio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE keycloak CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'portfolio_user'@'%' IDENTIFIED BY 'portfolio_password';
CREATE USER 'keycloak'@'%' IDENTIFIED BY 'keycloak123';
GRANT ALL PRIVILEGES ON portfolio_db.* TO 'portfolio_user'@'%';
GRANT ALL PRIVILEGES ON keycloak.* TO 'keycloak'@'%';
FLUSH PRIVILEGES;
```

**참고**: 이 프로젝트는 MariaDB에서 MySQL 8.0으로 마이그레이션되었습니다. 자세한 내용은 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)를 참고하세요.

### 데이터베이스 마이그레이션

```bash
# 마이그레이션 파일 생성
flask db migrate -m "Initial migration"

# 마이그레이션 실행
flask db upgrade
```

## 환경 변수

`.env` 파일은 `start_service.sh` 스크립트가 자동으로 생성합니다. 수동으로 설정하려면:

```env
# Flask 설정
FLASK_APP=app
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-in-production

# 데이터베이스
DATABASE_URL=mysql+pymysql://root:password@db:3306/portfolio_db

# Keycloak 설정
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=portfolio
KEYCLOAK_CLIENT_ID=portfolio-web
KEYCLOAK_CLIENT_SECRET=auto-generated-by-setup-keycloak

# Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200

# OpenAI API (선택사항)
OPENAI_API_KEY=your-openai-api-key
```

자세한 내용은 [docs/SERVICE_ARCHITECTURE.md](docs/SERVICE_ARCHITECTURE.md)를 참고하세요.

## 주요 기능

### 1. 사용자 인증
- Keycloak OAuth 2.0 / OpenID Connect 인증
- 로컬 사용자 인증 (username/password)
- 프로필 관리

### 2. 게시판 시스템
- 게시글 CRUD
- 댓글/대댓글
- 좋아요 기능
- 카테고리별 분류

### 3. 검색 기능
- Elasticsearch 기반 전문 검색
- 키워드 검색
- 태그 기반 검색
- 정렬 옵션

### 4. 챗봇
- FAQ 자동 응답
- AI 기반 챗봇 (LLM 모델 연동)
- OpenAI API 연동 (선택사항)
- 실시간 채팅 UI

### 5. 프로필 관리
- 자기소개 페이지
- 기술 스택 관리
- 경력/프로젝트 관리
- 프로필 이미지 업로드

## API 엔드포인트

### 인증
- `POST /auth/login` - 로그인
- `POST /auth/register` - 회원가입
- `GET /auth/logout` - 로그아웃

### 게시판
- `GET /board/` - 게시글 목록
- `GET /board/<id>` - 게시글 상세
- `POST /board/write` - 게시글 작성
- `POST /board/<id>/like` - 좋아요 토글
- `POST /board/<id>/comment` - 댓글 작성

### 챗봇
- `POST /chatbot/send` - 메시지 전송

## 배포

### Docker를 사용한 배포

**자동 배포 (권장):**

```bash
bash scripts/start_service.sh
```

**수동 배포:**

1. **Docker 이미지 빌드**
```bash
docker compose build
```

2. **Docker Compose로 실행**
```bash
docker compose up -d
```

3. **서비스 상태 확인**
```bash
docker compose ps
docker compose logs -f
```

### 접속 정보

서비스 시작 후 다음 URL로 접속할 수 있습니다:

- **웹 애플리케이션**: http://localhost:5000
- **Keycloak 관리 콘솔**: http://localhost:8080/admin
- **Elasticsearch**: http://localhost:9200

**기본 계정:**
- Keycloak 관리자: `admin` / `admin123`
- 테스트 사용자: `testuser` / `test123`

### 클라우드 배포

- **AWS**: EC2 + RDS + S3
- **Google Cloud**: Compute Engine + Cloud SQL
- **Azure**: App Service + Database

자세한 배포 가이드는 [docs/SERVICE_ARCHITECTURE.md](docs/SERVICE_ARCHITECTURE.md)를 참고하세요.

## 문서

프로젝트의 상세한 문서는 `docs/` 디렉토리에 있습니다:

- **[문서 인덱스](docs/DOCUMENTATION_INDEX.md)** - 모든 문서 목록
- **[서비스 아키텍처](docs/SERVICE_ARCHITECTURE.md)** - 전체 서비스 구조
- **[시작 가이드](docs/START_SERVICE_GUIDE.md)** - 서비스 시작 방법
- **[문제 해결 가이드](docs/TROUBLESHOOTING.md)** - 일반적인 문제 해결
- **[사용자 기능 로드맵](docs/USER_FEATURES_ROADMAP.md)** - 개발 로드맵

## 개발 가이드

### 코드 스타일
- PEP 8 준수
- Type hints 사용
- Docstring 작성

### 테스트
```bash
# 테스트 실행
python -m pytest

# 커버리지 리포트
python -m pytest --cov=app
```

### 데이터베이스 마이그레이션
```bash
# 마이그레이션 생성
flask db migrate -m "Description"

# 마이그레이션 적용
flask db upgrade

# 마이그레이션 되돌리기
flask db downgrade
```

## 문제 해결

문제가 발생하면 다음 문서를 참고하세요:

- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - 일반적인 문제 해결
- [KEYCLOAK_MARIADB_FIX.md](docs/KEYCLOAK_MARIADB_FIX.md) - Keycloak 문제 해결
- [WEB_ACCESS_TROUBLESHOOTING.md](docs/WEB_ACCESS_TROUBLESHOOTING.md) - 웹 접근 문제 해결

## 라이선스

이 프로젝트의 라이선스는 [LICENSE](LICENSE) 파일을 참고하세요.
