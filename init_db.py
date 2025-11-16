#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
"""

import os
import sys
from app import create_app, db
from app.models import User, Post, Comment, Like, Category

def init_database():
    """데이터베이스 초기화"""
    app = create_app()
    
    with app.app_context():
        try:
            # 데이터베이스 테이블 생성
            db.create_all()
            print("✅ 데이터베이스 테이블이 생성되었습니다.")
            
            # 기본 카테고리 생성
            categories = [
                Category(name='공지사항', description='중요한 공지사항'),
                Category(name='기술 블로그', description='기술 관련 포스팅'),
                Category(name='Q&A', description='질문과 답변')
            ]
            
            for category in categories:
                if not Category.query.filter_by(name=category.name).first():
                    db.session.add(category)
                    print(f"✅ 카테고리 '{category.name}' 생성됨")
            
            db.session.commit()
            print("✅ 기본 데이터가 생성되었습니다.")
            
        except Exception as e:
            print(f"❌ 데이터베이스 초기화 중 오류 발생: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    init_database()
