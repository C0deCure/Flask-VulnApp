from flask import render_template, request, redirect, url_for, flash, Blueprint, make_response, g
import jwt
from datetime import datetime, timedelta, timezone
import os

# 필요한 SQLAlchemy 모델과 db 객체를 가져옴
from app.models import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

# JWT 설정은 그대로 유지
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-secret-key-here'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def create_jwt_token(user_id):
    """JWT 토큰 생성 (이제 user_id는 숫자)"""
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token):
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload['user_id'] # 숫자 user_id 반환
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

# g.user에 사용자 객체를 로드하는 로직 추가
@auth_bp.before_app_request
def load_logged_in_user():
    """요청 처리 전에 로그인된 사용자 정보를 로드"""
    token = request.cookies.get('auth_token')
    g.user = None
    if token:
        user_id = verify_jwt_token(token)
        if user_id:
            # 토큰에 저장된 숫자 id로 사용자 조회
            g.user = User.query.get(user_id)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인"""
    if request.method == 'POST':
        # form에서 userid 대신 username을 받도록 변경
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('아이디와 비밀번호를 모두 입력해주세요.', 'error')
            return render_template('login.html', title='로그인')
        
        # id 대신 username으로 사용자를 찾음
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # 토큰에는 이제 문자열 username이 아닌, 숫자 id를 저장
            token = create_jwt_token(user.id)
            
            response = make_response(redirect(url_for('main.index')))
            response.set_cookie('auth_token', token, httponly=True, max_age=JWT_EXPIRATION_HOURS * 3600)
            
            flash('로그인되었습니다.', 'success')
            return response
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')
    
    return render_template('login.html', title='로그인')

@auth_bp.route('/logout')
def logout():
    """로그아웃"""
    response = make_response(redirect(url_for('main.index')))
    response.delete_cookie('auth_token')
    flash('로그아웃되었습니다.', 'success')
    return response

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입"""
    if request.method == 'POST':
        # form에서 userid 대신 username을 받도록 변경
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, password, confirm_password]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('register.html', title='회원가입')
        
        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('register.html', title='회원가입')
        
        # 이미 존재하는 아이디인지 username으로 확인
        if User.query.filter_by(username=username).first():
            flash('이미 존재하는 아이디입니다.', 'error')
            return render_template('register.html', title='회원가입')
        
        # id가 아닌 username으로 User 객체 생성
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='회원가입')