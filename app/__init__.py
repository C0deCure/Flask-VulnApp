import os
from flask import Flask, g, request
from .models import User
from .extensions import db # extensions.py에서 db 객체를 가져옴.

def create_app(config_name='default'):
    app = Flask(__name__)

    # 설정 로드
    app.config.from_object('app.config.Config')
    
    # SQLAlchemy 설정 추가
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['JWT_SECRET_KEY'] = os.urandom(32).hex()
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['JWT_EXPIRATION_HOURS'] = 24
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # db 객체를 Flask 앱과 연결(초기화)
    db.init_app(app)
    
    @app.before_request
    def load_logged_in_user():
        """모든 요청이 시작되기 전에 쿠키를 확인하여 로그인한 사용자를 g.user에 저장"""
        # auth 블루프린트에서 JWT 검증 함수를 가져옴
        from .blueprints.auth.routes import verify_jwt_token
        
        token = request.cookies.get('auth_token')
        user_id = verify_jwt_token(token)
        
        # user_id가 유효하면 DB에서 실제 User 객체를 찾아 g.user에 저장
        g.user = User.query.get(user_id) if user_id else None

    @app.context_processor
    def inject_user():
        """모든 템플릿에서 'current_user'라는 이름으로 g.user를 사용할 수 있게 함."""
        return dict(current_user=g.user)

    # 블루프린트 등록
    from .blueprints.main import main_bp
    from .blueprints.auth import auth_bp
    from .blueprints.api import api_bp
    from .blueprints.message import message_bp
    from app.blueprints.mypage import mypage_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(message_bp, url_prefix='/message')
    app.register_blueprint(mypage_bp, url_prefix='/mypage')
    
    return app