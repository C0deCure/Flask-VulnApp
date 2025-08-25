from flask import render_template, request, redirect, url_for, flash, current_app, Blueprint, g
from datetime import datetime

# 필요한 SQLAlchemy 모델과 객체들을 가져옴
from app.models import User, Free, Secret, Grad, Market, New, Info, Prom, Team
from app.extensions import db
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.context_processor
def inject_user():
    """모든 템플릿에 공통으로 사용자 정보를 전달하는 함수"""
    # g.user에는 @app.before_request 등에서 설정된 User 객체가 들어있다고 가정.
    return dict(current_user=g.user)

# 복잡했던 딕셔너리들을 이 하나로 통합
# URL 경로로 들어온 문자열('free', 'secret' 등)을 실제 모델 클래스와 연결.
BOARD_MODELS = {
    'free': Free, 'secret': Secret, 'grad': Grad, 'market': Market,
    'new': New, 'info': Info, 'prom': Prom, 'team': Team
}

# (get_current_user_id 함수는 이제 auth 블루프린트나 별도의 유틸리티 파일로 옮기는 것이 좋음)
# def get_current_user_id(): ...

@main_bp.route('/')
def index():
    """메인 페이지 - 각 게시판의 최신 글 4개씩 표시"""
    boards_data = {}
    for board_type, model in BOARD_MODELS.items():
        # 각 모델(테이블)에서 created_at을 기준으로 최신 글 4개를 가져옴
        # 기존 DB 컬럼명과 호환되도록 created_at 대신 f_date, s_date 등을 사용
        date_attr = getattr(model, f'{board_type[0]}_date')
        posts = model.query.order_by(desc(date_attr)).limit(4).all()
        
        # 기존 템플릿과 호환되도록 'frees', 'secrets' 등의 이름으로 전달
        boards_data[board_type + 's'] = posts
    return render_template('index.html', title='SMULife', **boards_data)


# 모든 게시판의 목록/상세보기/쓰기/수정/삭제 라우트를 하나로 통합

@main_bp.route('/<string:board_type>')
def board_list(board_type):
    """게시판 목록 보기 (통합)"""
    model = BOARD_MODELS.get(board_type)
    if not model:
        flash('존재하지 않는 게시판입니다.', 'error'); return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    # 페이지네이션 기능으로 10개씩 글을 나눠 보여줌
    date_attr = getattr(model, f'{board_type[0]}_date')
    pagination = model.query.order_by(desc(date_attr)).paginate(page=page, per_page=10, error_out=False)
    
    return render_template(f'{board_type}list.html', 
                           posts=pagination.items, # 기존 템플릿 호환성을 위해 posts 전달
                           pagination=pagination,
                           board_type=board_type,
                           title=current_app.config['BOARD_NAMES'].get(board_type))

@main_bp.route('/<string:board_type>/<int:post_id>')
def board_show(board_type, post_id):
    """게시글 상세 보기 (통합)"""
    model = BOARD_MODELS.get(board_type)
    num_attr_name = f'{board_type[0]}_num' # f_num, s_num 등
    
    if not model:
        flash('존재하지 않는 게시판입니다.', 'error'); return redirect(url_for('main.index'))
        
    post = model.query.filter(getattr(model, num_attr_name) == post_id).first_or_404()
    
    # 기존 템플릿(`freeshow.html` 등)이 row.f_num 같은 변수를 사용
    # ORM 객체(post)를 row라는 이름으로 전달하여 호환성을 유지
    return render_template(f'{board_type}show.html', 
                           row=post, 
                           title=getattr(post, f'{board_type[0]}_title'))

@main_bp.route('/<string:board_type>/write', methods=['GET', 'POST'])
def board_write(board_type):
    """게시글 작성 (통합)"""
    model = BOARD_MODELS.get(board_type)
    if not model:
        flash('존재하지 않는 게시판입니다.', 'error'); return redirect(url_for('main.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('text')
        
        # g.user.id는 @app.before_request 등에서 설정된 User 객체를 사용
        author_id = g.user.id if g.user else '익명'
        
        # setattr을 사용하여 동적으로 컬럼에 값을 할당
        new_post = model()
        setattr(new_post, f'{board_type[0]}_title', title)
        setattr(new_post, f'{board_type[0]}_txt', content)
        new_post.id = author_id # User ID
        
        db.session.add(new_post)
        db.session.commit()
        
        flash('게시글이 작성되었습니다.', 'success')
        return redirect(url_for('main.board_list', board_type=board_type))
        
    return render_template(f'{board_type}write.html', 
                           board_type=board_type,
                           title=current_app.config['BOARD_NAMES'].get(board_type))

@main_bp.route('/<string:board_type>/<int:post_id>/edit', methods=['GET', 'POST'])
def board_edit(board_type, post_id):
    """게시글 수정 (통합)"""
    model = BOARD_MODELS.get(board_type)
    num_attr_name = f'{board_type[0]}_num'
    if not model:
        flash('존재하지 않는 게시판입니다.', 'error'); return redirect(url_for('main.index'))
    
    post = model.query.filter(getattr(model, num_attr_name) == post_id).first_or_404()
    
    if not g.user or post.id != g.user.id:
        flash('수정할 권한이 없습니다.', 'error')
        return redirect(url_for('main.board_show', board_type=board_type, post_id=post_id))
        
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('text')
        setattr(post, f'{board_type[0]}_title', title)
        setattr(post, f'{board_type[0]}_txt', content)
        db.session.commit()
        flash('게시글이 수정되었습니다.', 'success')
        return redirect(url_for('main.board_show', board_type=board_type, post_id=post_id))

    return render_template(f'{board_type}edit.html', row=post, board_type=board_type)

@main_bp.route('/<string:board_type>/<int:post_id>/delete', methods=['POST', 'GET'])
def board_delete(board_type, post_id):
    """게시글 삭제 (통합)"""
    model = BOARD_MODELS.get(board_type)
    num_attr_name = f'{board_type[0]}_num'
    if not model:
        flash('존재하지 않는 게시판입니다.', 'error'); return redirect(url_for('main.index'))
        
    post = model.query.filter(getattr(model, num_attr_name) == post_id).first_or_404()
    
    if not g.user or post.id != g.user.id:
        flash('삭제할 권한이 없습니다.', 'error')
        return redirect(url_for('main.board_show', board_type=board_type, post_id=post_id))

    db.session.delete(post)
    db.session.commit()
    flash('게시글이 삭제되었습니다.', 'success')
    return redirect(url_for('main.board_list', board_type=board_type))