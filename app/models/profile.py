from datetime import datetime
from app import db
import json

class Profile(db.Model):
    """프로필 정보 모델"""
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="개발자 이름")
    title = db.Column(db.String(200), nullable=False, default="풀스택 웹 개발자")
    bio = db.Column(db.Text, default="안녕하세요! 사용자 중심의 웹 애플리케이션 개발을 추구하는 풀스택 개발자입니다.")
    profile_image_url = db.Column(db.String(500))  # 프로필 이미지 URL (하위 호환성)
    profile_image_filename = db.Column(db.String(255))  # 업로드된 이미지 파일명
    
    # JSON 필드로 유연한 데이터 저장
    skills = db.Column(db.JSON)  # 기술 스택 정보
    experiences = db.Column(db.JSON)  # 경력/프로젝트 정보
    contact_info = db.Column(db.JSON)  # 연락처 정보
    
    # 메타 정보
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Profile, self).__init__(**kwargs)
        # 기본값 설정
        if not self.skills:
            self.skills = {
                "backend": ["Python", "Flask", "Django", "FastAPI", "MySQL", "PostgreSQL"],
                "frontend": ["HTML5", "CSS3", "JavaScript", "Bootstrap", "React", "Vue.js"],
                "devops": ["Docker", "Git", "AWS", "Linux", "CI/CD"],
                "other": ["RESTful API", "JWT 인증", "데이터베이스 설계", "웹 보안"]
            }
        
        if not self.experiences:
            self.experiences = [
                {
                    "title": "포트폴리오 웹사이트 개발",
                    "period": "2024 - 현재",
                    "description": "Flask를 사용한 풀스택 웹 애플리케이션 개발. 사용자 인증, 게시판, 검색, 챗봇 기능을 포함한 완전한 웹 서비스 구현.",
                    "technologies": ["Flask", "MySQL", "JavaScript", "Bootstrap"]
                },
                {
                    "title": "웹 개발 학습 및 프로젝트",
                    "period": "2023 - 2024",
                    "description": "Python 웹 프레임워크 학습 및 다양한 사이드 프로젝트를 통한 실무 역량 개발.",
                    "technologies": ["Python", "Django", "HTML/CSS"]
                }
            ]
        
        if not self.contact_info:
            self.contact_info = {
                "email": "developer@example.com",
                "github": "github.com/username",
                "linkedin": "linkedin.com/in/username",
                "website": "portfolio-website.com"
            }
    
    def get_skills_by_category(self, category):
        """카테고리별 기술 스택 반환"""
        return self.skills.get(category, [])
    
    def add_experience(self, title, period, description, technologies):
        """경력/프로젝트 추가"""
        if not self.experiences:
            self.experiences = []
        
        self.experiences.append({
            "title": title,
            "period": period,
            "description": description,
            "technologies": technologies
        })
    
    def update_contact(self, **kwargs):
        """연락처 정보 업데이트"""
        if not self.contact_info:
            self.contact_info = {}
        
        for key, value in kwargs.items():
            self.contact_info[key] = value
    
    def get_profile_image_url(self):
        """프로필 이미지 URL 반환 (로컬 파일 우선)"""
        if self.profile_image_filename and self.profile_image_filename.strip():
            return f"/static/uploads/profile_images/{self.profile_image_filename}"
        elif self.profile_image_url and self.profile_image_url.strip():
            return self.profile_image_url
        return None
    
    def has_profile_image(self):
        """프로필 이미지 존재 여부"""
        return bool(
            (self.profile_image_filename and self.profile_image_filename.strip()) or 
            (self.profile_image_url and self.profile_image_url.strip())
        )
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'bio': self.bio,
            'profile_image_url': self.profile_image_url,
            'skills': self.skills,
            'experiences': self.experiences,
            'contact_info': self.contact_info,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_active_profile():
        """활성 프로필 반환 (단일 프로필 시스템)"""
        profile = Profile.query.filter_by(is_active=True).first()
        if not profile:
            # 프로필이 없으면 기본 프로필 생성
            profile = Profile()
            db.session.add(profile)
            db.session.commit()
        return profile
    
    def __repr__(self):
        return f'<Profile {self.name}>'

