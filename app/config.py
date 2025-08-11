import os
from datetime import timedelta

class Config:
    """기본 설정 클래스"""
    BASE_DIR = os.path.dirname(__file__)


    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'vulndb.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # 게시판 타입들
    BOARD_TYPES = ['free', 'secret', 'grad', 'market', 'new', 'info', 'prom', 'team']
    
    # 게시판 한글 이름
    BOARD_NAMES = {
        'free': '자유게시판',
        'secret': '비밀게시판', 
        'grad': '졸업게시판',
        'market': '장터',
        'new': '새내기게시판',
        'info': '정보게시판',
        'prom': '홍보게시판',
        'team': '동아리게시판'
    }

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True

class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False 