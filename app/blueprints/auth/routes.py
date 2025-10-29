from flask import current_app, g, request, make_response, redirect, url_for, flash, Blueprint, render_template
import jwt
from datetime import datetime, timedelta, timezone
import os
from app.models import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

def create_jwt_token(user_id):
    """JWT 토큰 생성 (app.config 사용)"""
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm=current_app.config['JWT_ALGORITHM']
    )

def verify_jwt_token(token):
    """JWT 토큰 검증 (app.config 사용)"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=[current_app.config['JWT_ALGORITHM']]
        )
        return payload.get('user_id')
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
    except Exception as e:
        return None

# g.user 로드 함수 (이제 단순화된 검증 함수 사용)
@auth_bp.before_app_request
def load_logged_in_user():
    """요청 처리 전에 로그인된 사용자 정보를 로드"""
    token = request.cookies.get('auth_token')
    g.user = None
    if token:
        user_id = verify_jwt_token(token) # 단순화된 검증 함수 호출
        if user_id:
            g.user = User.query.get(user_id)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 처리"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('아이디와 비밀번호를 모두 입력해주세요.', 'error')
            return render_template('login.html', title='로그인')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            token = create_jwt_token(user.id) # HS256 토큰 생성
            response = make_response(redirect(url_for('main.index')))
            max_age_seconds = current_app.config['JWT_EXPIRATION_HOURS'] * 3600
            response.set_cookie('auth_token', token, httponly=True, max_age=max_age_seconds, samesite='Lax')
            flash('로그인되었습니다.', 'success')
            return response
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')

    return render_template('login.html', title='로그인')

@auth_bp.route('/logout')
def logout():
    """로그아웃 처리"""
    response = make_response(redirect(url_for('main.index')))
    response.delete_cookie('auth_token')
    flash('로그아웃되었습니다.', 'success')
    return response

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입 처리"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, password, confirm_password]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('register.html', title='회원가입')

        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('register.html', title='회원가입')

        if User.query.filter_by(username=username).first():
            flash('이미 존재하는 아이디입니다.', 'error')
            return render_template('register.html', title='회원가입')

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', title='회원가입')

