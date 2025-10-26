from flask import render_template, request, redirect, url_for, flash, current_app, Blueprint, g
from datetime import datetime

# 필요한 SQLAlchemy 모델과 객체들을 가져옴
from app.models import User, Free, Secret, Grad, Market, New, Info, Prom, Team
from app.extensions import db
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

# BOARD_MODELS 딕셔너리는 그대로 유지
BOARD_MODELS = {
    'free': Free, 'secret': Secret, 'grad': Grad, 'market': Market,
    'new': New, 'info': Info, 'prom': Prom, 'team': Team
}

# index, board_list, board_show 함수는 이전과 동일하게 잘 작동하므로 그대로 둡니다.
# (단, board_show가 렌더링하는 템플릿은 이전 답변을 참고하여 수정되었어야 합니다)
@main_bp.route('/')
def index():
    """메인 페이지"""
    boards_data = {}
    for board_type, model in BOARD_MODELS.items():
        date_attr_name = f'{board_type[0]}_date'
        if hasattr(model, date_attr_name):
            date_attr = getattr(model, date_attr_name)
            posts = model.query.order_by(desc(date_attr)).limit(4).all()
            boards_data[board_type + 's'] = posts
    return render_template('index.html', title='SMULife', **boards_data)

@main_bp.route('/<string:board_type>')
def board_list(board_type):
    """게시판 목록 보기 (통합)"""
    model = BOARD_MODELS.get(board_type)
    if not model:
        flash('존재하지 않는 게시판입니다.', 'error'); return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    date_attr_name = f'{board_type[0]}_date'
    if hasattr(model, date_attr_name):
        date_attr = getattr(model, date_attr_name)
        pagination = model.query.order_by(desc(date_attr)).paginate(page=page, per_page=10, error_out=False)
        return render_template(f'{board_type}list.html', posts=pagination.items, pagination=pagination, board_type=board_type)
    
    flash('게시판을 불러오는 데 실패했습니다.', 'error'); return redirect(url_for('main.index'))

@main_bp.route('/<string:board_type>/<int:post_id>')
def board_show(board_type, post_id):
    """게시글 상세 보기 (통합)"""
    model = BOARD_MODELS.get(board_type)
    num_attr_name = f'{board_type[0]}_num'
    if not model:
        flash('존재하지 않는 게시판입니다.', 'error'); return redirect(url_for('main.index'))
        
    post = model.query.filter(getattr(model, num_attr_name) == post_id).first_or_404()
    return render_template(f'{board_type}show.html', 
                           row=post, 
                           board_type=board_type)


@main_bp.route('/<string:board_type>/write', methods=['GET', 'POST'])
def board_write(board_type):
    """게시글 작성 (통합)"""
    model = BOARD_MODELS.get(board_type)
    if not model:
        flash('존재하지 않는 게시판입니다.', 'error'); return redirect(url_for('main.index'))

    # 로그인 여부 확인 로직 추가
    if not g.user:
        flash('글을 작성하려면 로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('text')
        
        # setattr을 사용하여 동적으로 컬럼에 값을 할당
        new_post = model()
        setattr(new_post, f'{board_type[0]}_title', title)
        setattr(new_post, f'{board_type[0]}_txt', content)
        
        # 작성자를 new_post.id가 아닌, new_post.author 관계로 지정
        new_post.author = g.user
        
        db.session.add(new_post)
        db.session.commit()
        
        flash('게시글이 작성되었습니다.', 'success')
        return redirect(url_for('main.board_list', board_type=board_type))
        
    return render_template(f'{board_type}write.html', board_type=board_type)

@main_bp.route('/<string:board_type>/<int:post_id>/edit', methods=['GET', 'POST'])
def board_edit(board_type, post_id):
    """게시글 수정 (통합)"""
    model = BOARD_MODELS.get(board_type)
    num_attr_name = f'{board_type[0]}_num'
    if not model:
        flash('존재하지 않는 게시판입니다.', 'error'); return redirect(url_for('main.index'))
    
    post = model.query.filter(getattr(model, num_attr_name) == post_id).first_or_404()
    
    # 소유자 확인 시 post.id 대신 post.author_id와 비교
    if not g.user or post.author_id != g.user.id:
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
    
    # 소유자 확인 시 post.id 대신 post.author_id와 비교
    if not g.user or post.author_id != g.user.id:
        flash('삭제할 권한이 없습니다.', 'error')
        return redirect(url_for('main.board_show', board_type=board_type, post_id=post_id))

    db.session.delete(post)
    db.session.commit()
    flash('게시글이 삭제되었습니다.', 'success')
    return redirect(url_for('main.board_list', board_type=board_type))