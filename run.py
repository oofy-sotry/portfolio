#!/usr/bin/env python3
"""
Flask 애플리케이션 실행 스크립트
"""

from app import create_app, db
from app.models import User, Post, Comment, Like, Category
from app.models.profile import Profile

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
        'Category': Category,
        'Profile': Profile
    }

@app.cli.command()
def init_db():
    """데이터베이스 초기화"""
    db.create_all()
    print("데이터베이스가 초기화되었습니다.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
