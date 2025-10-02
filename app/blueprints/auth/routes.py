from flask import render_template, request, redirect, url_for, flash, Blueprint, make_response
from app.models.user import User
from app import get_db, create_jwt_token, verify_jwt_token

# Blueprint 생성
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인"""
    if request.method == 'POST':
        user_id = request.form.get('userid')
        password = request.form.get('password')
        
        if not user_id or not password:
            flash('아이디와 비밀번호를 모두 입력해주세요.', 'error')
            return render_template('login.html', title='로그인')
        
        user = User.get(user_id)
        
        if user and user.check_password(password):
            # JWT 토큰 생성
            token = create_jwt_token(user_id)
            
            # 응답 생성
            response = make_response(redirect(url_for('main.index')))
            response.set_cookie('auth_token', token, httponly=True, max_age=24*60*60)  # 24시간
            
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
        major = request.form.get('major')
        
        if not user_id or not password or not major:
            flash('아이디, 비밀번호, 학과를 모두 입력해주세요.', 'error')
            return render_template('register.html', title='회원가입')
        
        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('register.html', title='회원가입')
        
        if User.get(user_id):
            flash('이미 존재하는 아이디입니다.', 'error')
            return render_template('register.html', title='회원가입')
        
        user = User(id=user_id, major=major)
        user.set_password(password)
        user.save()
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='회원가입') 