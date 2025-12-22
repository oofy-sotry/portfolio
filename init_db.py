#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
"""

import os
import sys
from app import create_app, db
from app.models import User, Post, Comment, Like, Category, FAQ
from app.services.elasticsearch_service import ElasticsearchService

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

            # 기본 FAQ 데이터 삽입
            faq_seed = [
                ("자기소개", "안녕하세요! 저는 풀스택 개발자입니다. Flask, Python, JavaScript 등을 사용하여 웹 애플리케이션을 개발합니다."),
                ("기술스택", "주요 기술스택: Python, Flask, JavaScript, HTML/CSS, MySQL, Docker, Git"),
                ("프로젝트", "이 포트폴리오 사이트는 Flask를 사용하여 개발한 풀스택 웹 애플리케이션입니다."),
                ("연락처", "이메일이나 연락처 정보는 연락처 페이지에서 확인하실 수 있습니다."),
                ("경력", "웹 개발 경험과 다양한 프로젝트를 통해 실무 역량을 쌓아왔습니다."),
                ("학습", "지속적인 학습을 통해 최신 기술 트렌드를 따라가고 있습니다.")
            ]

            es = ElasticsearchService()
            es.create_index()

            for question, answer in faq_seed:
                existing = FAQ.query.filter_by(question=question).first()
                if existing:
                    # 이미 존재하면 ES만 동기화
                    es.index_document(f"faq-{existing.id}", {
                        "doc_type": "faq",
                        "title": existing.question,
                        "content": existing.answer,
                        "category": existing.category,
                        "created_at": existing.created_at.isoformat() if existing.created_at else None,
                        "faq_id": existing.id,
                    })
                    continue

                faq = FAQ(question=question, answer=answer, category=None, is_active=True)
                db.session.add(faq)
                db.session.flush()  # id 확보
                es.index_document(f"faq-{faq.id}", {
                    "doc_type": "faq",
                    "title": faq.question,
                    "content": faq.answer,
                    "category": faq.category,
                    "created_at": faq.created_at.isoformat() if faq.created_at else None,
                    "faq_id": faq.id,
                })

            db.session.commit()
            print("✅ 기본 FAQ가 DB 및 Elasticsearch에 등록되었습니다.")
            
        except Exception as e:
            print(f"❌ 데이터베이스 초기화 중 오류 발생: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    init_database()
