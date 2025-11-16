#!/usr/bin/env python3
"""
프로필 데이터 초기화 스크립트
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.profile import Profile

def init_profile_data():
    """프로필 데이터 초기화"""
    app = create_app()
    
    with app.app_context():
        try:
            # 기존 프로필 확인
            existing_profile = Profile.query.filter_by(is_active=True).first()
            
            if existing_profile:
                print("✅ 이미 활성 프로필이 존재합니다.")
                print(f"   - 이름: {existing_profile.name}")
                print(f"   - 타이틀: {existing_profile.title}")
                return
            
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
            
            print("✅ 프로필 데이터가 성공적으로 초기화되었습니다!")
            print(f"   - 이름: {profile.name}")
            print(f"   - 타이틀: {profile.title}")
            print(f"   - 기술 스택: {len(profile.skills['backend']) + len(profile.skills['frontend']) + len(profile.skills['devops']) + len(profile.skills['other'])}개")
            print(f"   - 경력/프로젝트: {len(profile.experiences)}개")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 프로필 데이터 초기화 실패: {e}")
            raise

def reset_profile_data():
    """프로필 데이터 리셋"""
    app = create_app()
    
    with app.app_context():
        try:
            # 기존 프로필 삭제
            Profile.query.delete()
            db.session.commit()
            
            print("✅ 기존 프로필 데이터가 삭제되었습니다.")
            
            # 새 프로필 생성
            init_profile_data()
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 프로필 데이터 리셋 실패: {e}")
            raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="프로필 데이터 관리")
    parser.add_argument("--reset", action="store_true", help="기존 데이터를 삭제하고 새로 생성")
    
    args = parser.parse_args()
    
    if args.reset:
        reset_profile_data()
    else:
        init_profile_data()
