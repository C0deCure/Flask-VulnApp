from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from datetime import datetime, timedelta
from dotenv import load_dotenv

import jwt
import os

from werkzeug.middleware.proxy_fix import ProxyFix

# 환경 변수 로드
load_dotenv()

# JWT 설정
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-secret-key-here'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()

# loginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = "info"

def create_app(config_name='default'):
    """애플리케이션 팩토리 함수"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # 설정 로드
    if config_name == 'development':
        app.config.from_object('app.config.DevelopmentConfig')
    elif config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    else:
        app.config.from_object('app.config.Config')

    # DB init
    db.init_app(app)  # register db on app
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)
    # model import
    from app import models

    # 템플릿 필터 등록
    from .utils.helpers import nl2br, format_datetime, truncate_text
    app.jinja_env.filters['nl2br'] = nl2br
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['truncate_text'] = truncate_text

    # 전역 템플릿 변수 등록
    # @app.context_processor
    # def inject_user():
    #     from flask import request
    #     return {'current_user': get_current_user(request)}
    
    # Blueprint 등록
    from .blueprints.main import main_bp
    from .blueprints.auth import auth_bp
    from .blueprints.api import api_bp
    from .blueprints.board import board_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(board_bp)

    # reverse proxy setting
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_prefix=1)

    # login_manager
    login_manager.init_app(app)

    # insert default data
    from .init_data import insert_default_boards
    with app.app_context():
        insert_default_boards()

    return app

def create_jwt_token(user_id):
    """JWT 토큰 생성"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token):
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(request):
    """현재 사용자 정보 가져오기"""
    token = request.cookies.get('auth_token')
    if token:
        user_id = verify_jwt_token(token)
        if user_id:
            return {'id': user_id, 'is_authenticated': True}
    return {'id': None, 'is_authenticated': False}



'''
folder name app?
collision?
'''