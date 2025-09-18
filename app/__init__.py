from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from werkzeug.middleware.proxy_fix import ProxyFix

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

'''
folder name app?
collision?
'''