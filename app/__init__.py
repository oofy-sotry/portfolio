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
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
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
    
    # 데이터베이스 연결 테스트
    with app.app_context():
        try:
            db.create_all()
            print("✅ 데이터베이스 연결 성공")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
    
    return app
