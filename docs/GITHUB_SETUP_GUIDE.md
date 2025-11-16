# GitHub 저장소 설정 가이드

## 개요

이 가이드는 로컬 `portfolio_website` 폴더를 GitHub 저장소 `https://github.com/oofy-sotry/portfolio.git`에 업로드하는 방법을 설명합니다.

## 사전 준비

### 1. Git 설치 확인

Git이 설치되어 있는지 확인:

```bash
git --version
```

**Git이 설치되어 있지 않은 경우:**

- **Windows**: [Git for Windows](https://git-scm.com/download/win) 다운로드 및 설치
- 설치 후 Git Bash 또는 PowerShell을 재시작

### 2. GitHub 계정 확인

- GitHub 계정이 있어야 합니다: `oofy-sotry`
- 저장소가 생성되어 있어야 합니다: `https://github.com/oofy-sotry/portfolio.git`

## 방법 1: Git 명령어 사용 (권장)

### 단계별 가이드

#### 1단계: 프로젝트 디렉토리로 이동

```bash
cd C:\Users\oofys\Desktop\portfolio\portfolio_website
```

#### 2단계: Git 저장소 초기화 (아직 초기화되지 않은 경우)

```bash
git init
```

#### 3단계: .gitignore 파일 생성 (선택사항, 권장)

프로젝트 루트에 `.gitignore` 파일을 생성하여 불필요한 파일을 제외합니다:

```bash
# .gitignore 파일 생성
```

`.gitignore` 파일 내용 예시:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Flask
instance/
.webassets-cache

# 환경 변수
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Docker
*.log

# 데이터베이스
*.db
*.sqlite

# 업로드된 파일 (선택사항)
app/static/uploads/

# 모델 캐시 (선택사항)
models/
*.pth
*.bin

# 임시 파일
*.tmp
*.bak
```

#### 4단계: 모든 파일 추가

```bash
git add .
```

또는 특정 파일만 추가:

```bash
git add *.py
git add *.md
git add *.yml
git add *.sql
git add *.sh
# 등등
```

#### 5단계: 첫 커밋 생성

```bash
git commit -m "Initial commit: Portfolio website"
```

#### 6단계: 원격 저장소 추가

```bash
git remote add origin https://github.com/oofy-sotry/portfolio.git
```

이미 원격 저장소가 있는 경우:

```bash
git remote set-url origin https://github.com/oofy-sotry/portfolio.git
```

#### 7단계: 브랜치 이름 확인 및 설정

```bash
# 현재 브랜치 확인
git branch

# main 브랜치로 이름 변경 (필요한 경우)
git branch -M main
```

#### 8단계: GitHub에 푸시

```bash
git push -u origin main
```

또는 `master` 브랜치를 사용하는 경우:

```bash
git push -u origin master
```

#### 9단계: 인증

GitHub에 푸시할 때 인증이 필요합니다:

**옵션 A: Personal Access Token 사용 (권장)**

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" 클릭
3. 권한 선택: `repo` (전체 저장소 접근)
4. 토큰 생성 및 복사
5. 푸시 시 비밀번호 대신 토큰 사용

**옵션 B: GitHub CLI 사용**

```bash
# GitHub CLI 설치 후
gh auth login
```

**옵션 C: SSH 키 사용**

1. SSH 키 생성 및 GitHub에 추가
2. 원격 저장소 URL을 SSH 형식으로 변경:
   ```bash
   git remote set-url origin git@github.com:oofy-sotry/portfolio.git
   ```

## 방법 2: GitHub Desktop 사용

### 단계별 가이드

1. **GitHub Desktop 설치**
   - [GitHub Desktop](https://desktop.github.com/) 다운로드 및 설치

2. **저장소 추가**
   - File → Add Local Repository
   - `C:\Users\oofys\Desktop\portfolio\portfolio_website` 선택

3. **커밋 생성**
   - 변경사항 확인
   - 커밋 메시지 입력: "Initial commit: Portfolio website"
   - "Commit to main" 클릭

4. **원격 저장소 연결**
   - Repository → Repository Settings → Remote
   - 원격 URL 입력: `https://github.com/oofy-sotry/portfolio.git`

5. **푸시**
   - Repository → Push origin
   - 또는 상단의 "Publish branch" 버튼 클릭

## 방법 3: VS Code 사용

### 단계별 가이드

1. **VS Code에서 프로젝트 열기**
   - File → Open Folder
   - `C:\Users\oofys\Desktop\portfolio\portfolio_website` 선택

2. **소스 제어 패널 열기**
   - 왼쪽 사이드바의 소스 제어 아이콘 클릭 (또는 `Ctrl+Shift+G`)

3. **변경사항 스테이징**
   - "+" 버튼을 클릭하여 모든 파일 추가
   - 또는 개별 파일의 "+" 버튼 클릭

4. **커밋**
   - 커밋 메시지 입력: "Initial commit: Portfolio website"
   - "✓ Commit" 버튼 클릭

5. **원격 저장소 추가**
   - 소스 제어 패널에서 "..." 메뉴 클릭
   - "Remote" → "Add Remote"
   - 이름: `origin`
   - URL: `https://github.com/oofy-sotry/portfolio.git`

6. **푸시**
   - 소스 제어 패널에서 "..." 메뉴 클릭
   - "Push" 선택
   - 또는 "Sync Changes" 버튼 클릭

## 문제 해결

### 문제 1: "fatal: not a git repository"

**원인**: Git 저장소가 초기화되지 않음

**해결**:
```bash
git init
```

### 문제 2: "fatal: remote origin already exists"

**원인**: 이미 원격 저장소가 설정되어 있음

**해결**:
```bash
# 기존 원격 저장소 제거
git remote remove origin

# 새로 추가
git remote add origin https://github.com/oofy-sotry/portfolio.git
```

또는 기존 원격 저장소 URL 변경:

```bash
git remote set-url origin https://github.com/oofy-sotry/portfolio.git
```

### 문제 3: "Permission denied (publickey)"

**원인**: SSH 키가 설정되지 않았거나 GitHub에 등록되지 않음

**해결**:
- Personal Access Token 사용 (HTTPS)
- 또는 SSH 키 생성 및 GitHub에 추가

### 문제 4: "error: failed to push some refs"

**원인**: 원격 저장소에 이미 커밋이 있음

**해결**:
```bash
# 원격 저장소의 변경사항 가져오기
git pull origin main --allow-unrelated-histories

# 충돌 해결 후 다시 푸시
git push -u origin main
```

또는 강제 푸시 (⚠️ 주의: 원격 저장소의 내용이 덮어씌워집니다):

```bash
git push -u origin main --force
```

### 문제 5: 큰 파일 업로드 실패

**원인**: GitHub는 100MB 이상의 파일을 허용하지 않음

**해결**:
- `.gitignore`에 큰 파일 추가
- Git LFS 사용 (Large File Storage)

```bash
# Git LFS 설치 후
git lfs install
git lfs track "*.pth"
git lfs track "*.bin"
git add .gitattributes
```

## .gitignore 권장 사항

다음 파일들은 일반적으로 GitHub에 업로드하지 않습니다:

- 환경 변수 파일 (`.env`)
- 가상 환경 (`venv/`, `env/`)
- 캐시 파일 (`__pycache__/`)
- IDE 설정 (`.vscode/`, `.idea/`)
- 로그 파일 (`*.log`)
- 데이터베이스 파일 (`*.db`, `*.sqlite`)
- 업로드된 사용자 파일 (`app/static/uploads/`)
- 큰 모델 파일 (`models/*.pth`, `models/*.bin`)

## 다음 단계

### 1. README.md 파일 추가

프로젝트 루트에 `README.md` 파일을 생성하여 프로젝트 설명을 추가하세요:

```markdown
# Portfolio Website

포트폴리오 웹사이트 프로젝트입니다.

## 기술 스택

- Flask (Python)
- MySQL 8.0
- Keycloak 24.0
- Elasticsearch 8.11.0
- Docker Compose

## 시작하기

자세한 내용은 [docs/START_SERVICE_GUIDE.md](docs/START_SERVICE_GUIDE.md)를 참고하세요.

## 문서

- [서비스 아키텍처](docs/SERVICE_ARCHITECTURE.md)
- [문제 해결 가이드](docs/TROUBLESHOOTING.md)
- [사용자 기능 로드맵](docs/USER_FEATURES_ROADMAP.md)
```

### 2. 라이선스 추가

프로젝트 루트에 `LICENSE` 파일을 추가하세요 (선택사항).

### 3. GitHub Actions 설정 (선택사항)

CI/CD 파이프라인을 설정하려면 `.github/workflows/` 디렉토리를 생성하세요.

## 참고 자료

- [Git 공식 문서](https://git-scm.com/doc)
- [GitHub 문서](https://docs.github.com/)
- [GitHub Desktop 가이드](https://docs.github.com/en/desktop)

