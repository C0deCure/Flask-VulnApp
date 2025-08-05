import sqlite3
import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# JWT 설정
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-secret-key-here'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def get_db():
    """데이터베이스 연결"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'app.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """데이터베이스 초기화 및 테이블 생성"""
    with get_db() as db:
        cursor = db.cursor()
        
        # 사용자 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 자유게시판 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS free (
                f_num INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT DEFAULT '익명',
                f_title TEXT NOT NULL,
                f_txt TEXT NOT NULL,
                f_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 비밀게시판 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS secret (
                s_num INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT DEFAULT '익명',
                s_title TEXT NOT NULL,
                s_txt TEXT NOT NULL,
                s_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 졸업게시판 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grad (
                g_num INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT DEFAULT '익명',
                g_title TEXT NOT NULL,
                g_txt TEXT NOT NULL,
                g_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 장터 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market (
                m_num INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT DEFAULT '익명',
                m_title TEXT NOT NULL,
                m_txt TEXT NOT NULL,
                m_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 새내기게시판 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS new (
                n_num INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT DEFAULT '익명',
                n_title TEXT NOT NULL,
                n_txt TEXT NOT NULL,
                n_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 정보게시판 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS info (
                i_num INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT DEFAULT '익명',
                i_title TEXT NOT NULL,
                i_txt TEXT NOT NULL,
                i_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 홍보게시판 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prom (
                p_num INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT DEFAULT '익명',
                p_title TEXT NOT NULL,
                p_txt TEXT NOT NULL,
                p_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 동아리게시판 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team (
                t_num INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT DEFAULT '익명',
                t_title TEXT NOT NULL,
                t_txt TEXT NOT NULL,
                t_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.commit()

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
    
    # 템플릿 필터 등록
    from app.utils.helpers import nl2br, format_datetime, truncate_text
    app.jinja_env.filters['nl2br'] = nl2br
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['truncate_text'] = truncate_text
    
    # 전역 템플릿 변수 등록
    @app.context_processor
    def inject_user():
        from flask import request
        return {'current_user': get_current_user(request)}
    
    # Blueprint 등록
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 데이터베이스 초기화
    with app.app_context():
        init_db()
    
    return app 