#!/usr/bin/env python3
"""
Profile 시스템 수정 스크립트
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.profile import Profile

def fix_profile_system():
    """Profile 시스템 수정"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Profile 시스템 수정 시작...")
            
            # 1. 모든 테이블 생성
            print("1️⃣ 모든 테이블 생성 중...")
            db.create_all()
            print("✅ 테이블 생성 완료")
            
            # 2. Profile 테이블 확인
            print("2️⃣ Profile 테이블 확인 중...")
            try:
                result = db.engine.execute("SHOW TABLES LIKE 'profiles'")
                tables = result.fetchall()
                if tables:
                    print("✅ profiles 테이블 존재 확인")
                else:
                    print("❌ profiles 테이블이 존재하지 않음")
            except Exception as e:
                print(f"⚠️ 테이블 확인 중 오류 (무시 가능): {e}")
            
            # 3. 기존 프로필 확인
            print("3️⃣ 기존 프로필 확인 중...")
            existing_profile = Profile.query.filter_by(is_active=True).first()
            
            if existing_profile:
                print(f"✅ 기존 프로필 발견: {existing_profile.name}")
            else:
                print("4️⃣ 새 프로필 생성 중...")
                # 새 프로필 생성
                profile = Profile()
                profile.name = "개발자 이름"
                profile.title = "풀스택 웹 개발자"
                profile.bio = """안녕하세요! 사용자 중심의 웹 애플리케이션 개발을 추구하는 
풀스택 개발자입니다.

Python과 Flask를 기반으로 한 백엔드 개발과 
JavaScript를 활용한 프론트엔드 개발에 경험이 있으며, 
사용자 경험을 중시하는 개발을 지향합니다.

지속적인 학습과 새로운 기술에 대한 도전을 통해 
더 나은 개발자로 성장하고 있습니다."""
                
                # 기술 스택 설정
                profile.skills = {
                    "backend": ["Python", "Flask", "Django", "FastAPI", "MySQL", "PostgreSQL"],
                    "frontend": ["HTML5", "CSS3", "JavaScript", "Bootstrap", "React", "Vue.js"],
                    "devops": ["Docker", "Git", "AWS", "Linux", "CI/CD"],
                    "other": ["RESTful API", "JWT 인증", "데이터베이스 설계", "웹 보안"]
                }
                
                # 경력/프로젝트 설정
                profile.experiences = [
                    {
                        "title": "포트폴리오 웹사이트 개발",
                        "period": "2024 - 현재",
                        "description": "Flask를 사용한 풀스택 웹 애플리케이션 개발. 사용자 인증, 게시판, 검색, 챗봇 기능을 포함한 완전한 웹 서비스 구현.",
                        "technologies": ["Flask", "MySQL", "JavaScript", "Bootstrap", "Docker"]
                    },
                    {
                        "title": "웹 개발 학습 및 프로젝트",
                        "period": "2023 - 2024",
                        "description": "Python 웹 프레임워크 학습 및 다양한 사이드 프로젝트를 통한 실무 역량 개발.",
                        "technologies": ["Python", "Django", "HTML/CSS", "JavaScript"]
                    }
                ]
                
                # 연락처 정보 설정
                profile.contact_info = {
                    "email": "developer@example.com",
                    "github": "github.com/username",
                    "linkedin": "linkedin.com/in/username",
                    "website": "portfolio-website.com"
                }
                
                # 데이터베이스에 저장
                db.session.add(profile)
                db.session.commit()
                print("✅ 새 프로필 생성 완료")
            
            # 5. 최종 확인
            print("5️⃣ 최종 확인 중...")
            final_profile = Profile.get_active_profile()
            print(f"✅ 최종 프로필: {final_profile.name} ({final_profile.title})")
            
            print("\n🎉 Profile 시스템 수정 완료!")
            print("이제 /profile/edit 페이지에 접속해보세요.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Profile 시스템 수정 실패: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    fix_profile_system()
