<<<<<<< Updated upstream
=======
from flask import render_template, request, redirect, url_for, flash, Blueprint, make_response
import jwt
from datetime import datetime, timedelta, timezone
import os

from app.models import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

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
        return payload.get('user_id')
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
        
        # 이제 user_id(String)로 기본 키 조회가 정상적으로 작동
        user = User.query.get(user_id)
        
        if user and user.check_password(password):
            token = create_jwt_token(user.id) # user.id를 사용
            
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
        user_id = request.form.get('userid')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([user_id, password, confirm_password]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('register.html', title='회원가입')
        
        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('register.html', title='회원가입')
        
        # 이제 user_id(String)로 중복 체크가 정상적으로 작동
        if User.query.get(user_id):
            flash('이미 존재하는 아이디입니다.', 'error')
            return render_template('register.html', title='회원가입')
        
        # User 모델의 id는 이제 문자열(userid)
        new_user = User(id=user_id)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='회원가입')
>>>>>>> Stashed changes
