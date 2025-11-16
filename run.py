#!/usr/bin/env python3
"""
Flask 애플리케이션 실행 스크립트
"""

from app import create_app, db
from app.models import User, Post, Comment, Like, Category

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Flask shell 컨텍스트 설정"""
    return {
        'db': db,
        'User': User,
        'Post': Post,
        'Comment': Comment,
        'Like': Like,
        'Category': Category
    }

@app.cli.command()
def init_db():
    """데이터베이스 초기화"""
    db.create_all()
    print("데이터베이스가 초기화되었습니다.")

@app.cli.command()
def create_admin():
    """관리자 계정 생성"""
    username = input("관리자 사용자명: ")
    email = input("관리자 이메일: ")
    password = input("관리자 비밀번호: ")
    
    admin = User(
        username=username,
        email=email,
        is_admin=True
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    print(f"관리자 계정 '{username}'이 생성되었습니다.")

@app.cli.command()
def create_sample_data():
    """샘플 데이터 생성"""
    # 카테고리 생성
    categories = [
        Category(name='공지사항', description='중요한 공지사항'),
        Category(name='기술 블로그', description='기술 관련 포스팅'),
        Category(name='Q&A', description='질문과 답변')
    ]
    
    for category in categories:
        if not Category.query.filter_by(name=category.name).first():
            db.session.add(category)
    
    db.session.commit()
    print("샘플 데이터가 생성되었습니다.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
