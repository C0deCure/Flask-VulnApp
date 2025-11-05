from flask import render_template, request, redirect, url_for, flash, Blueprint, make_response
from app.models.user import User
from app import get_db, create_jwt_token, verify_jwt_token
from werkzeug.security import check_password_hash

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
        

        try:
            db = get_db()

            query = "SELECT id, password FROM user WHERE id = '" + user_id + "'"

            print(f"--- [DEBUG] Executing Query: {query} ---")
            cursor = db.execute(query)
            result = cursor.fetchone()

            if result:
                stored_hash = result[1]
                if stored_hash and check_password_hash(stored_hash, password):
                    user_id_from_db = result[0]
                    token = create_jwt_token(user_id_from_db)
                    response = make_response(redirect(url_for('main.index')))
                    response.set_cookie('auth_token', token, httponly=True, max_age=24*60*60)
                    flash('로그인되었습니다.', 'success')
                    return response
                else:
                    flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')
            else:
                flash("존재하지 않는 아이디입니다.", 'error')
        except Exception as e:
            print(f"Query Error: {e}")
            flash('로그인 처리 중 오류가 발생했습니다.', 'error')
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
        name = request.form.get('name')
        student_number = request.form.get('student_number')
        department = request.form.get('department')
        email = request.form.get('email')
        phone = request.form.get('phone')
        terms_agreed = 1 if request.form.get('terms_agreed') == '1' else 0


        if not all([user_id, password, confirm_password, name, student_number, department, email, phone]):
            flash('모든 항목을 입력해주세요.', 'error')
            return render_template('register.html', title='회원가입')
        
        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('register.html', title='회원가입')
        
        if User.get(user_id):
            flash('이미 존재하는 아이디입니다.', 'error')
            return render_template('register.html', title='회원가입')
        
        user = User(
            id=user_id,
            name=name,
            student_number=student_number,
            department=department,
            email=email,
            phone=phone,
            terms_agreed=terms_agreed
        )
        user.set_password(password)
        user.save()

        token = create_jwt_token(user_id)
        response = make_response(redirect(url_for('main.index')))
        response.set_cookie('auth_token', token, httponly=True, max_age=24*60*60)  # 24시간
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='회원가입') 

@auth_bp.route('/profile')
def profile():
    """JWT 토큰 검증을 통한 인증된 사용자만 접근"""
    token = request.cookies.get('auth_token')
    payload = verify_jwt_token(token)
    if payload:
        user_id = payload.get('user_id')
        user = User.get(user_id)
        if user:
            return render_template('profile.html', user=user, title='내 정보')
        else:
            flash('사용자 정보를 찾을 수 없습니다.', 'error')
            return redirect(url_for('auth.login'))
    else:
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))