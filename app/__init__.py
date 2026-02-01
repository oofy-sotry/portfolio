from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 전역 객체들
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    """Flask 애플리케이션 팩토리"""
    app = Flask(__name__)
    
    # 설정
    # 보안: 프로덕션 환경에서는 SECRET_KEY가 반드시 설정되어야 함
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        import sys
        # 개발 환경에서만 기본값 사용 (환경 변수로 구분)
        if os.getenv('FLASK_ENV') != 'production' and os.getenv('ENVIRONMENT') != 'production':
            secret_key = 'dev-secret-key-change-in-production'
            print("⚠️ 경고: SECRET_KEY가 설정되지 않아 개발용 기본값을 사용합니다.")
            print("   프로덕션 환경에서는 반드시 SECRET_KEY 환경 변수를 설정하세요.")
        else:
            print("❌ 오류: 프로덕션 환경에서 SECRET_KEY가 설정되지 않았습니다.")
            sys.exit(1)
    app.config['SECRET_KEY'] = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/portfolio_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 확장 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app)
    
    # 로그인 설정
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '로그인이 필요합니다.'
    login_manager.login_message_category = 'info'
    
    # user_loader 함수 설정
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # 블루프린트 등록
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.board import board_bp
    from app.routes.chatbot import chatbot_bp
    from app.routes.search import search_bp
    from app.routes.profile import profile_bp
    from app.routes.faq_admin import faq_admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(board_bp, url_prefix='/board')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(profile_bp)
    app.register_blueprint(faq_admin_bp)
    
    # 데이터베이스 연결 테스트 및 마이그레이션
    with app.app_context():
        try:
            db.create_all()
            print("✅ 데이터베이스 연결 성공")
            
            # 마이그레이션: is_keycloak_user 컬럼 추가 (기존 데이터베이스용)
            try:
                from sqlalchemy import text, inspect
                from sqlalchemy.exc import OperationalError
                
                # users 테이블이 존재하는지 확인
                inspector = inspect(db.engine)
                if 'users' in inspector.get_table_names():
                    # 컬럼 존재 여부 확인
                    columns = [col['name'] for col in inspector.get_columns('users')]
                    
                    if 'is_keycloak_user' not in columns:
                        print("📝 마이그레이션: is_keycloak_user 컬럼 추가 중...")
                        db.session.execute(text("""
                            ALTER TABLE users 
                            ADD COLUMN is_keycloak_user BOOLEAN DEFAULT FALSE 
                            AFTER is_admin
                        """))
                        db.session.commit()
                        print("✅ 마이그레이션 완료: is_keycloak_user 컬럼이 추가되었습니다.")
                    else:
                        print("ℹ️ is_keycloak_user 컬럼이 이미 존재합니다.")
                    
                    # password_hash를 NULL 허용으로 변경 (필요한 경우)
                    password_hash_col = next((col for col in inspector.get_columns('users') if col['name'] == 'password_hash'), None)
                    if password_hash_col and not password_hash_col['nullable']:
                        print("📝 마이그레이션: password_hash 컬럼을 NULL 허용으로 변경 중...")
                        db.session.execute(text("""
                            ALTER TABLE users 
                            MODIFY COLUMN password_hash VARCHAR(128) NULL
                        """))
                        db.session.commit()
                        print("✅ 마이그레이션 완료: password_hash 컬럼이 NULL 허용으로 변경되었습니다.")
            except OperationalError as migration_error:
                # 테이블이 아직 없는 경우 무시 (db.create_all()이 처리함)
                print(f"ℹ️ 마이그레이션 체크: {migration_error}")
            except Exception as migration_error:
                print(f"⚠️ 마이그레이션 중 오류 (무시 가능): {migration_error}")
                db.session.rollback()
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
    
    return app
