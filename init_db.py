#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
"""

import sys
from app import create_app, db
from app.models import User, Category, FAQ
from app.models.profile import Profile
from app.services.elasticsearch_service import ElasticsearchService


def init_database():
    """데이터베이스 초기화"""
    app = create_app()

    with app.app_context():
        try:
            db.create_all()
            print("✅ 데이터베이스 테이블 생성 완료")

            # 기본 카테고리 생성
            default_categories = [
                Category(name='공지사항', description='중요한 공지사항'),
                Category(name='기술 블로그', description='기술 관련 포스팅'),
                Category(name='Q&A', description='질문과 답변'),
            ]

            for category in default_categories:
                if not Category.query.filter_by(name=category.name).first():
                    db.session.add(category)
                    print(f"  카테고리 '{category.name}' 생성")

            # 관리자 계정 생성
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', email='admin@example.com', is_admin=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.flush()

                profile = Profile(user_id=admin.id, name='admin')
                db.session.add(profile)
                print("  관리자 계정 생성 (admin / admin123)")

            db.session.commit()

            # Elasticsearch 인덱스 생성
            try:
                es = ElasticsearchService()
                es.create_index()
            except Exception as e:
                print(f"⚠️ Elasticsearch 인덱스 생성 실패 (나중에 재시도): {e}")

            # 기본 FAQ 데이터
            faq_data = [
                ("자기소개", "안녕하세요! 풀스택 개발자입니다."),
                ("기술스택", "Python, Flask, JavaScript, MySQL, Docker, Elasticsearch"),
                ("연락처", "연락처 페이지에서 확인하실 수 있습니다."),
            ]

            for question, answer in faq_data:
                if not FAQ.query.filter_by(question=question).first():
                    faq = FAQ(question=question, answer=answer, is_active=True)
                    db.session.add(faq)

            db.session.commit()

            # FAQ를 Elasticsearch에 인덱싱
            try:
                from app.utils.indexing_utils import index_faq_to_es
                for faq in FAQ.query.filter_by(is_active=True).all():
                    index_faq_to_es(faq)
                print("✅ FAQ Elasticsearch 인덱싱 완료")
            except Exception as e:
                print(f"⚠️ FAQ ES 인덱싱 실패 (나중에 재시도): {e}")

            print("✅ 초기 데이터 설정 완료")

        except Exception as e:
            print(f"❌ 데이터베이스 초기화 오류: {e}")
            db.session.rollback()
            sys.exit(1)


if __name__ == '__main__':
    init_database()
