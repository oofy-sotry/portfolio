#!/usr/bin/env python3
"""
데이터베이스 초기 데이터 설정
"""

from app import create_app, db
from app.models import User, Category, Post
from datetime import datetime

def init_data():
    """초기 데이터 생성"""
    app = create_app()
    
    with app.app_context():
        # 데이터베이스 테이블 생성
        db.create_all()
        
        # 관리자 계정 생성
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            print("✅ 관리자 계정 생성 완료")
        
        # 일반 사용자 계정 생성
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com',
                is_admin=False
            )
            test_user.set_password('test123')
            db.session.add(test_user)
            print("✅ 테스트 사용자 계정 생성 완료")
        
        # 카테고리 생성
        categories_data = [
            {'name': '기술', 'description': '프로그래밍 및 기술 관련 게시글'},
            {'name': '프로젝트', 'description': '개발 프로젝트 관련 게시글'},
            {'name': '일상', 'description': '일상생활 관련 게시글'},
            {'name': '학습', 'description': '학습 및 교육 관련 게시글'},
            {'name': '리뷰', 'description': '제품 및 서비스 리뷰'}
        ]
        
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
        
        db.session.commit()
        print("✅ 카테고리 생성 완료")
        
        # 샘플 게시글 생성
        sample_posts = [
            {
                'title': 'Flask 웹 개발 시작하기',
                'content': '''Flask는 Python으로 웹 애플리케이션을 개발할 때 사용하는 가벼운 웹 프레임워크입니다.

## Flask의 장점
- 간단하고 직관적인 API
- 유연한 구조
- 풍부한 확장 기능
- 활발한 커뮤니티

## 기본 사용법
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
```

Flask를 사용하면 빠르고 효율적으로 웹 애플리케이션을 개발할 수 있습니다.''',
                'tags': 'Python, Flask, 웹개발',
                'category_name': '기술'
            },
            {
                'title': '포트폴리오 웹사이트 프로젝트',
                'content': '''개발자 포트폴리오 웹사이트를 Flask로 개발했습니다.

## 프로젝트 개요
- **기술스택**: Flask, Python, MySQL, Docker
- **주요 기능**: 게시판, 챗봇, 검색, 사용자 인증
- **배포**: Docker Compose를 사용한 컨테이너화

## 구현한 기능들
1. **사용자 인증**: 로그인, 회원가입, 권한 관리
2. **게시판**: CRUD 기능, 댓글, 좋아요
3. **AI 챗봇**: LLM 기반 고급 챗봇
4. **검색**: Elasticsearch 기반 전문 검색
5. **반응형 UI**: Bootstrap을 사용한 모바일 친화적 디자인

## 배운 점
- Flask 프레임워크의 활용
- 데이터베이스 설계 및 ORM 사용
- Docker를 활용한 배포
- AI/ML 모델 통합''',
                'tags': 'Flask, Python, 포트폴리오, 웹개발',
                'category_name': '프로젝트'
            },
            {
                'title': '개발자로서의 성장 과정',
                'content': '''개발자로서 성장해온 과정을 공유합니다.

## 시작점
처음에는 HTML, CSS, JavaScript의 기초부터 시작했습니다. 웹의 기본 구조를 이해하는 것이 중요했죠.

## 중간 과정
- **Python**: 데이터 분석과 웹 개발에 관심을 가지게 되었습니다
- **Flask**: 가벼운 웹 프레임워크로 시작해서 점차 복잡한 애플리케이션을 만들었습니다
- **데이터베이스**: MySQL, PostgreSQL 등을 사용해서 데이터를 체계적으로 관리하는 방법을 배웠습니다

## 현재
- **풀스택 개발**: 프론트엔드와 백엔드를 모두 다룰 수 있게 되었습니다
- **DevOps**: Docker, CI/CD 파이프라인 등을 활용한 배포 자동화
- **AI/ML**: 머신러닝 모델을 웹 애플리케이션에 통합하는 방법을 학습 중입니다

## 앞으로의 목표
- 클라우드 기술 심화 학습
- 마이크로서비스 아키텍처 이해
- 오픈소스 기여 활동''',
                'tags': '개발자, 성장, 학습',
                'category_name': '일상'
            }
        ]
        
        for post_data in sample_posts:
            # 카테고리 찾기
            category = Category.query.filter_by(name=post_data['category_name']).first()
            if category:
                existing_post = Post.query.filter_by(title=post_data['title']).first()
                if not existing_post:
                    post = Post(
                        title=post_data['title'],
                        content=post_data['content'],
                        tags=post_data['tags'],
                        user_id=test_user.id,
                        category_id=category.id,
                        is_published=True
                    )
                    db.session.add(post)
        
        db.session.commit()
        print("✅ 샘플 게시글 생성 완료")
        
        print("\n🎉 초기 데이터 설정 완료!")
        print("📝 관리자 계정: admin / admin123")
        print("👤 테스트 계정: testuser / test123")

if __name__ == '__main__':
    init_data()
