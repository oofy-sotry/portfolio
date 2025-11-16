# 사용자별 기능 개발 로드맵

## 개요

현재 Portfolio 웹사이트는 단일 프로필 시스템으로 작동하고 있습니다. 이 문서는 사용자별(로그인별) 기능을 구현하기 위한 로드맵을 제시합니다.

## 현재 상태

### 현재 구현된 기능

1. **인증 시스템**
   - Keycloak OAuth 2.0 / OpenID Connect 인증
   - 로컬 사용자 인증 (username/password)
   - 사용자별 세션 관리
   - `User` 모델: `id`, `username`, `email`, `password_hash`, `is_admin`

2. **프로필 시스템**
   - **단일 프로필 시스템**: 모든 사용자가 동일한 프로필을 공유
   - `Profile` 모델: `name`, `title`, `bio`, `skills`, `experiences`, `contact_info`
   - 프로필 관리 페이지: `/profile/`
   - 프로필 편집 페이지: `/profile/edit`
   - 자기소개 페이지: `/about` (모든 사용자에게 동일한 내용 표시)

3. **챗봇 시스템**
   - 기본 FAQ 챗봇: `/chatbot/`
   - AI 기반 챗봇: `/chatbot/advanced`
   - **현재 상태**: 모든 사용자에게 동일한 응답 제공
   - 프로필 정보를 참조하지 않음

## 개발 목표

### 목표 1: 사용자별 프로필 시스템

각 사용자가 자신만의 프로필을 가지도록 변경합니다.

#### 필요한 변경사항

1. **데이터베이스 모델 수정**
   ```python
   # app/models/profile.py
   class Profile(db.Model):
       # 기존 필드 유지
       user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
       # user_id를 통해 사용자와 1:1 관계 설정
   ```

2. **User 모델에 관계 추가**
   ```python
   # app/models/user.py
   class User(UserMixin, db.Model):
       # 기존 필드 유지
       profile = db.relationship('Profile', backref='user', uselist=False)
   ```

3. **프로필 관리 로직 변경**
   - `Profile.get_active_profile()` → `Profile.get_user_profile(user_id)`
   - 현재 로그인한 사용자의 프로필만 반환
   - 프로필이 없으면 자동 생성

4. **라우트 수정**
   ```python
   # app/routes/profile.py
   @profile_bp.route('/')
   @login_required
   def manage():
       profile = Profile.get_user_profile(current_user.id)
       return render_template('profile/manage.html', profile=profile)
   ```

#### 구현 단계

- [ ] **1단계**: 데이터베이스 마이그레이션
  - `Profile` 모델에 `user_id` 필드 추가
  - 기존 프로필 데이터 마이그레이션 (기본 사용자에게 할당)
  - `unique=True` 제약 조건 추가

- [ ] **2단계**: 모델 메서드 수정
  - `Profile.get_user_profile(user_id)` 메서드 추가
  - `Profile.get_active_profile()` 메서드 제거 또는 deprecated 처리
  - 프로필 자동 생성 로직 추가

- [ ] **3단계**: 라우트 수정
  - 모든 프로필 관련 라우트에서 `current_user.id` 사용
  - 권한 검사 추가 (자신의 프로필만 수정 가능)

- [ ] **4단계**: 템플릿 수정
  - 프로필 관리 페이지에서 사용자 정보 표시
  - 프로필 미리보기에서 사용자별 프로필 표시

### 목표 2: 사용자별 자기소개 페이지

각 사용자가 자신만의 자기소개 페이지를 가지도록 변경합니다.

#### 필요한 변경사항

1. **라우트 수정**
   ```python
   # app/routes/main.py
   @main_bp.route('/about')
   @main_bp.route('/about/<username>')
   def about(username=None):
       if username:
           # 특정 사용자의 프로필 표시
           user = User.query.filter_by(username=username).first_or_404()
           profile = Profile.get_user_profile(user.id)
       else:
           # 현재 로그인한 사용자의 프로필 표시
           if current_user.is_authenticated:
               profile = Profile.get_user_profile(current_user.id)
           else:
               # 기본 프로필 또는 404
               profile = Profile.get_default_profile()
       
       return render_template('main/about.html', profile=profile, user=user if username else current_user)
   ```

2. **템플릿 수정**
   - `app/templates/main/about.html`에서 사용자 정보 표시
   - 사용자명, 프로필 이미지, 개인 정보 표시

#### 구현 단계

- [ ] **1단계**: 라우트 수정
  - `/about` → 현재 로그인한 사용자의 프로필
  - `/about/<username>` → 특정 사용자의 프로필
  - 비로그인 사용자 처리

- [ ] **2단계**: 템플릿 수정
  - 사용자별 프로필 정보 표시
  - 프로필이 없는 경우 처리

- [ ] **3단계**: 네비게이션 수정
  - 메뉴에서 자기소개 링크를 사용자별로 변경
  - 다른 사용자의 프로필 링크 생성

### 목표 3: 사용자별 챗봇 응답

각 사용자의 프로필 정보를 기반으로 챗봇이 개인화된 응답을 제공하도록 변경합니다.

#### 필요한 변경사항

1. **챗봇 컨텍스트 추가**
   ```python
   # app/routes/chatbot.py
   @chatbot_bp.route('/ai-chat', methods=['POST'])
   @login_required
   def ai_chat():
       # 현재 사용자의 프로필 정보 가져오기
       profile = Profile.get_user_profile(current_user.id)
       
       # 프로필 정보를 컨텍스트로 추가
       context = f"""
       사용자 정보:
       - 이름: {profile.name}
       - 직책: {profile.title}
       - 소개: {profile.bio}
       - 기술 스택: {', '.join(profile.get_all_skills())}
       - 경력: {len(profile.experiences)}개
       """
       
       # LLM 서비스에 컨텍스트 전달
       prompt = f"{context}\n\n사용자 질문: {user_message}"
       response = llm_service.generate_response(prompt, mode=mode)
   ```

2. **프로필 기반 FAQ 응답**
   ```python
   def get_personalized_faq_response(message, profile):
       """프로필 정보를 기반으로 FAQ 응답 생성"""
       message_lower = message.lower()
       
       # 프로필 정보 기반 응답
       if '자기소개' in message_lower or '소개' in message_lower:
           return f"안녕하세요! 저는 {profile.name}입니다. {profile.bio}"
       
       if '기술' in message_lower or '스택' in message_lower:
           skills = profile.get_all_skills()
           return f"제 주요 기술 스택은 {', '.join(skills)}입니다."
       
       # 기존 FAQ 로직
       return get_faq_response(message)
   ```

#### 구현 단계

- [ ] **1단계**: 챗봇 라우트에 인증 추가
  - `/chatbot/ai-chat` 엔드포인트에 `@login_required` 데코레이터 추가
  - 비로그인 사용자 처리

- [ ] **2단계**: 프로필 정보 컨텍스트 추가
  - 현재 사용자의 프로필 정보를 챗봇 컨텍스트에 포함
  - LLM 프롬프트에 프로필 정보 추가

- [ ] **3단계**: 개인화된 FAQ 응답
  - 프로필 정보를 기반으로 FAQ 응답 생성
  - 기술 스택, 경력, 프로젝트 정보 활용

- [ ] **4단계**: 챗봇 UI 개선
  - 사용자별 챗봇 히스토리 저장 (선택사항)
  - 프로필 정보 표시

## 데이터베이스 마이그레이션 계획

### 마이그레이션 스크립트

```python
# migrations/versions/xxxx_add_user_id_to_profile.py
def upgrade():
    # 1. user_id 컬럼 추가 (nullable=True로 먼저 추가)
    op.add_column('profiles', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # 2. 기본 사용자에게 기존 프로필 할당
    # (또는 관리자 사용자에게 할당)
    op.execute("""
        UPDATE profiles 
        SET user_id = (SELECT id FROM users WHERE is_admin = 1 LIMIT 1)
        WHERE user_id IS NULL
    """)
    
    # 3. user_id를 nullable=False로 변경
    op.alter_column('profiles', 'user_id', nullable=False)
    
    # 4. 외래 키 제약 조건 추가
    op.create_foreign_key('fk_profile_user', 'profiles', 'users', ['user_id'], ['id'])
    
    # 5. unique 제약 조건 추가
    op.create_unique_constraint('uq_profile_user', 'profiles', ['user_id'])
    
    # 6. is_active 컬럼 제거 (선택사항, user_id로 대체)
    # op.drop_column('profiles', 'is_active')

def downgrade():
    # 롤백 로직
    op.drop_constraint('uq_profile_user', 'profiles')
    op.drop_constraint('fk_profile_user', 'profiles')
    op.drop_column('profiles', 'user_id')
```

## API 변경사항

### 프로필 API

**현재:**
```python
GET /profile/  # 현재 로그인한 사용자의 프로필 (단일 프로필)
```

**변경 후:**
```python
GET /profile/  # 현재 로그인한 사용자의 프로필
GET /profile/<username>  # 특정 사용자의 프로필 (읽기 전용)
PUT /profile/  # 현재 로그인한 사용자의 프로필 수정
```

### 자기소개 API

**현재:**
```python
GET /about  # 단일 프로필 표시
```

**변경 후:**
```python
GET /about  # 현재 로그인한 사용자의 프로필 (또는 기본 프로필)
GET /about/<username>  # 특정 사용자의 프로필
```

### 챗봇 API

**현재:**
```python
POST /chatbot/ai-chat  # 공통 응답
```

**변경 후:**
```python
POST /chatbot/ai-chat  # 현재 로그인한 사용자의 프로필 기반 개인화 응답
# @login_required 추가 필요
```

## 보안 고려사항

1. **프로필 접근 제어**
   - 자신의 프로필만 수정 가능
   - 다른 사용자의 프로필은 읽기 전용
   - 관리자는 모든 프로필 수정 가능

2. **자기소개 페이지 접근 제어**
   - 모든 사용자의 자기소개 페이지는 공개 (읽기 전용)
   - 프로필이 없는 사용자의 경우 기본 프로필 또는 404

3. **챗봇 개인정보 보호**
   - 챗봇 응답에 민감한 정보 포함 방지
   - 프로필 정보는 컨텍스트로만 사용, 직접 노출 금지

## 테스트 계획

### 단위 테스트

- [ ] `Profile.get_user_profile(user_id)` 메서드 테스트
- [ ] 프로필 자동 생성 로직 테스트
- [ ] 사용자별 프로필 접근 권한 테스트

### 통합 테스트

- [ ] 사용자별 자기소개 페이지 접근 테스트
- [ ] 사용자별 챗봇 응답 테스트
- [ ] 프로필 수정 권한 테스트

### 사용자 시나리오 테스트

1. **시나리오 1: 새 사용자 가입**
   - 사용자 가입 → 프로필 자동 생성 → 자기소개 페이지 접근 → 챗봇 사용

2. **시나리오 2: 기존 사용자 프로필 수정**
   - 로그인 → 프로필 수정 → 자기소개 페이지 확인 → 챗봇 응답 확인

3. **시나리오 3: 다른 사용자 프로필 보기**
   - 로그인 → 다른 사용자의 자기소개 페이지 접근 → 읽기 전용 확인

## 우선순위

### Phase 1: 핵심 기능 (높은 우선순위)
1. ✅ 사용자별 프로필 시스템 구현
2. ✅ 자기소개 페이지 사용자별 접근
3. ✅ 프로필 수정 권한 제어

### Phase 2: 개선 기능 (중간 우선순위)
4. ✅ 사용자별 챗봇 응답
5. ✅ 프로필 공개/비공개 설정 (선택사항)
6. ✅ 프로필 검색 기능 (선택사항)

### Phase 3: 고급 기능 (낮은 우선순위)
7. ⬜ 사용자별 챗봇 히스토리
8. ⬜ 프로필 통계 및 분석
9. ⬜ 프로필 템플릿 시스템

## 참고사항

- 현재 프로필 시스템은 단일 프로필을 사용하므로, 마이그레이션 시 기존 프로필 데이터를 처리해야 합니다.
- 모든 사용자가 프로필을 가질 필요는 없습니다. 프로필이 없는 경우 기본 프로필 또는 빈 프로필을 표시할 수 있습니다.
- 관리자는 모든 사용자의 프로필을 관리할 수 있도록 권한을 부여할 수 있습니다.

