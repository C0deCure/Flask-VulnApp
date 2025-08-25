from flask import render_template, request, redirect, url_for, flash, Blueprint, make_response
import jwt
from datetime import datetime, timedelta, timezone
import os

# 필요한 SQLAlchemy 모델과 db 객체를 가져옴
from app.models import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

# JWT 관련 함수들을 __init__.py에서 이곳으로 옮김
# (나중에 utils.py 같은 파일로 옮기면 더 좋음)
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-secret-key-here'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def create_jwt_token(user_id):
    """JWT 토큰 생성"""
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
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인"""
    if request.method == 'POST':
        user_id = request.form.get('userid')
        password = request.form.get('password')
        
        if not user_id or not password:
            flash('아이디와 비밀번호를 모두 입력해주세요.', 'error')
            return render_template('login.html', title='로그인')
        
        # ID로 사용자를 찾음
        user = User.query.get(user_id)
        
        # 사용자가 존재하고, 비밀번호가 맞는지 확인
        if user and user.check_password(password):
            token = create_jwt_token(user_id)
            
            response = make_response(redirect(url_for('main.index')))
            response.set_cookie('auth_token', token, httponly=True, max_age=24*60*60)
            
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
        user_id = request.form.get('userid')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([user_id, password, confirm_password]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('register.html', title='회원가입')
        
        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('register.html', title='회원가입')
        
        # 이미 존재하는 아이디인지 확인
        if User.query.get(user_id):
            flash('이미 존재하는 아이디입니다.', 'error')
            return render_template('register.html', title='회원가입')
        
        # 새로운 User 객체를 만들고 DB에 저장
        new_user = User(id=user_id)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='회원가입')