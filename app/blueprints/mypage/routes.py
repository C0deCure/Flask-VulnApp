from flask import Blueprint, render_template, request, redirect, url_for, g, flash, jsonify, make_response, current_app
from app.models import User, Note
from app.extensions import db
from app.models import Free, Secret, Grad, Market, New, Info, Prom, Team
from urllib.parse import urlparse

# mypage 블루프린트 생성
mypage_bp = Blueprint('mypage', __name__, url_prefix='/mypage')

BOARD_MODELS = {
    'free': Free, 'secret': Secret, 'grad': Grad, 'market': Market,
    'new': New, 'info': Info, 'prom': Prom, 'team': Team
}

@mypage_bp.route('/', methods=['GET', 'POST'])
def profile():
    """마이페이지 뷰 및 정보 수정 처리 (리팩토링 최종 버전)"""
    if not g.user:
        # GET 요청 시에는 기존처럼 로그인 페이지로 리디렉션
        if request.method == 'GET':
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login'))
        # POST(API) 요청 시에는 JSON으로 에러 응답
        return jsonify({'status': 'error', 'message': '로그인이 필요합니다.'}), 401

    # --- POST 요청 (API 방식) 처리 ---
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': '잘못된 요청입니다.'}), 400

        user_id_from_form = data.get('id')
        new_password = data.get('password')

        user_to_update = User.query.get(user_id_from_form)
        
        if user_to_update:
            user_to_update.set_password(new_password) # 모델의 set_password 메서드 사용
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': f"ID '{user_to_update.id}' 사용자의 정보가 성공적으로 업데이트되었습니다."
            })
        else:
            return jsonify({'status': 'error', 'message': '존재하지 않는 사용자입니다.'}), 404
            
    # --- GET 요청 처리 ---
    return render_template('mypage/mypage.html')

@mypage_bp.route('/rules')
def community_rules():
    """커뮤니티 이용규칙 페이지를 보여주는 라우트"""
    return render_template('mypage/community_rules.html')

@mypage_bp.route('/terms')
def terms_of_service():
    """서비스 이용약관 페이지를 보여주는 라우트"""
    return render_template('mypage/terms_of_service.html')

@mypage_bp.route('/my-posts')
def my_posts():
    """내가 쓴 글 모아보기"""
    if not g.user:
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    board_names = {
        'free': '자유게시판', 'secret': '비밀게시판', 'grad': '졸업게시판',
        'market': '장터', 'new': '새내기게시판', 'info': '정보게시판',
        'prom': '홍보게시판', 'team': '동아리게시판'
    }

    posts_by_board = {}
    
    for board_type, model in BOARD_MODELS.items():
        date_attr_name = f'{board_type[0]}_date'
        if hasattr(model, date_attr_name):
            date_attr = getattr(model, date_attr_name)
            user_posts = model.query.filter_by(author_id=g.user.id).order_by(date_attr.desc()).all()
            if user_posts:
                posts_by_board[board_type] = user_posts
            
    return render_template('mypage/my_posts.html', 
                           posts_by_board=posts_by_board, 
                           board_names=board_names)
    
@mypage_bp.route('/delete-account', methods=['POST'])
def delete_account():
    """회원 탈퇴 처리"""
    if not g.user:
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # CSRF 방지를 위한 Referer 헤더 검증
    # 요청의 출처(Referer)가 현재 우리 서버의 호스트와 일치하는지 확인
    if not request.referrer:
        flash('요청 출처를 확인할 수 없습니다.', 'error')
        return redirect(url_for('mypage.profile'))
    
    referrer_host = urlparse(request.referrer).hostname
    server_host = urlparse(request.host_url).hostname
    
    if referrer_host != server_host:
        flash('잘못된 접근입니다.', 'error')
        return redirect(url_for('mypage.profile'))

    try:
        user_to_delete = g.user
        # 1. 모든 게시판을 순회하며 작성한 게시글 삭제
        for board_type, model in BOARD_MODELS.items():
            model.query.filter_by(author_id=user_to_delete.id).delete()
            
        # 2. 보낸 쪽지 모두 삭제
        Note.query.filter_by(sender_id=user_to_delete.id).delete()
                
        db.session.delete(user_to_delete)
        db.session.commit()
        
        flash('회원 탈퇴가 완료되었습니다. 이용해주셔서 감사합니다.', 'success')
        response = make_response(redirect(url_for('main.index')))
        response.delete_cookie('auth_token')
        return response

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"회원 탈퇴 중 오류 발생: {e}") # 서버 로그에 에러 기록
        flash('회원 탈퇴 중 오류가 발생했습니다. 다시 시도해주세요.', 'error')
        return redirect(url_for('mypage.profile'))