<<<<<<< HEAD
<<<<<<< Updated upstream
=======
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
=======
from flask import render_template, request, redirect, url_for, flash, current_app, Blueprint
from app import get_db, verify_jwt_token
from datetime import datetime

# Blueprint 생성
main_bp = Blueprint('main', __name__)

# 게시판 테이블 매핑
BOARD_TABLES = {
    'free': 'free',
    'secret': 'secret',
    'grad': 'grad',
    'market': 'market',
    'new': 'new',
    'info': 'info',
    'prom': 'prom',
    'team': 'team'
}

# 게시판 ID 필드 매핑
BOARD_ID_FIELDS = {
    'free': 'f_num',
    'secret': 's_num',
    'grad': 'g_num',
    'market': 'm_num',
    'new': 'n_num',
    'info': 'i_num',
    'prom': 'p_num',
    'team': 't_num'
}

# 게시판 제목 필드 매핑
BOARD_TITLE_FIELDS = {
    'free': 'f_title',
    'secret': 's_title',
    'grad': 'g_title',
    'market': 'm_title',
    'new': 'n_title',
    'info': 'i_title',
    'prom': 'p_title',
    'team': 't_title'
}

# 게시판 내용 필드 매핑
BOARD_CONTENT_FIELDS = {
    'free': 'f_txt',
    'secret': 's_txt',
    'grad': 'g_txt',
    'market': 'm_txt',
    'new': 'n_txt',
    'info': 'i_txt',
    'prom': 'p_txt',
    'team': 't_txt'
}

# 게시판 날짜 필드 매핑
BOARD_DATE_FIELDS = {
    'free': 'f_date',
    'secret': 's_date',
    'grad': 'g_date',
    'market': 'm_date',
    'new': 'n_date',
    'info': 'i_date',
    'prom': 'p_date',
    'team': 't_date'
}

# 게시판 복수형 변수명 매핑
BOARD_PLURAL_NAMES = {
    'free': 'frees',
    'secret': 'secrets',
    'grad': 'grads',
    'market': 'markets',
    'new': 'news',
    'info': 'infos',
    'prom': 'proms',
    'team': 'teams'
}

def get_current_user_id():
    """현재 로그인한 사용자 ID 가져오기"""
    token = request.cookies.get('auth_token')
    if token:
        return verify_jwt_token(token)
    return None

@main_bp.route('/test')
def test():
    """테스트 페이지"""
    return "Flask 애플리케이션이 정상적으로 작동합니다!"
>>>>>>> d2f9f73d86bfa294f94db90eab8290f45c3a0910

@main_bp.route('/')
def index():
    """메인 페이지 - 각 게시판의 최신 글 4개씩 표시"""
<<<<<<< HEAD
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

=======
    try:
        boards_data = {}
        
        with get_db() as db:
            cursor = db.cursor()
            
            for board_type in current_app.config['BOARD_TYPES']:
                table_name = BOARD_TABLES[board_type]
                date_field = BOARD_DATE_FIELDS[board_type]
                
                cursor.execute(f"SELECT * FROM {table_name} ORDER BY {date_field} DESC LIMIT 4")
                posts = cursor.fetchall()
                
                # 복수형 변수명으로 데이터 전달
                boards_data[BOARD_PLURAL_NAMES[board_type]] = posts
        
        return render_template('index.html', title='에브리타임', **boards_data)
        
    except Exception as e:
        flash(f'오류가 발생했습니다: {str(e)}', 'error')
        return render_template('index.html', title='에브리타임')

# 더 구체적인 라우트들을 먼저 정의 (write, edit, delete)
@main_bp.route('/free/write', methods=['GET', 'POST'])
@main_bp.route('/secret/write', methods=['GET', 'POST'])
@main_bp.route('/grad/write', methods=['GET', 'POST'])
@main_bp.route('/market/write', methods=['GET', 'POST'])
@main_bp.route('/new/write', methods=['GET', 'POST'])
@main_bp.route('/info/write', methods=['GET', 'POST'])
@main_bp.route('/prom/write', methods=['GET', 'POST'])
@main_bp.route('/team/write', methods=['GET', 'POST'])
def board_write_specific():
    """특정 게시판 글쓰기"""
    board_type = request.path.split('/')[1]
    
    if board_type not in current_app.config['BOARD_TYPES']:
        flash('존재하지 않는 게시판입니다.', 'error')
        return redirect(url_for('main.index'))
    
>>>>>>> d2f9f73d86bfa294f94db90eab8290f45c3a0910
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('text')
        
<<<<<<< HEAD
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
>>>>>>> Stashed changes
=======
        if not title or not content:
            flash('제목과 내용을 모두 입력해주세요.', 'error')
            template_name = f"{board_type}write.html"
            return render_template(template_name, board_type=board_type)
        
        table_name = BOARD_TABLES[board_type]
        title_field = BOARD_TITLE_FIELDS[board_type]
        content_field = BOARD_CONTENT_FIELDS[board_type]
        
        # 현재 로그인한 사용자 ID 가져오기
        current_user_id = get_current_user_id()
        author = current_user_id if current_user_id else '익명'
        
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute(
                f"INSERT INTO {table_name} (id, {title_field}, {content_field}) VALUES (?, ?, ?)",
                (author, title, content)
            )
            db.commit()
        
        flash('게시글이 작성되었습니다.', 'success')
        return redirect(url_for('main.board_list_specific'))
    
    template_name = f"{board_type}write.html"
    return render_template(template_name, 
                         board_type=board_type,
                         title=current_app.config['BOARD_NAMES'][board_type])

@main_bp.route('/free/<int:post_id>/edit', methods=['GET', 'POST'])
@main_bp.route('/secret/<int:post_id>/edit', methods=['GET', 'POST'])
@main_bp.route('/grad/<int:post_id>/edit', methods=['GET', 'POST'])
@main_bp.route('/market/<int:post_id>/edit', methods=['GET', 'POST'])
@main_bp.route('/new/<int:post_id>/edit', methods=['GET', 'POST'])
@main_bp.route('/info/<int:post_id>/edit', methods=['GET', 'POST'])
@main_bp.route('/prom/<int:post_id>/edit', methods=['GET', 'POST'])
@main_bp.route('/team/<int:post_id>/edit', methods=['GET', 'POST'])
def board_edit_specific(post_id):
    """특정 게시글 수정"""
    board_type = request.path.split('/')[1]
    
    if board_type not in current_app.config['BOARD_TYPES']:
        flash('존재하지 않는 게시판입니다.', 'error')
        return redirect(url_for('main.index'))
    
    table_name = BOARD_TABLES[board_type]
    id_field = BOARD_ID_FIELDS[board_type]
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE {id_field} = ?", (post_id,))
        post = cursor.fetchone()
    
    if not post:
        flash('존재하지 않는 게시글입니다.', 'error')
        return redirect(url_for('main.board_list_specific'))
    
    # 작성자 확인 (로그인한 사용자만 수정 가능)
    current_user_id = get_current_user_id()
    if not current_user_id or post['id'] != current_user_id:
        flash('게시글을 수정할 권한이 없습니다.', 'error')
        return redirect(url_for('main.board_show_specific', post_id=post_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('text')
        
        if not title or not content:
            flash('제목과 내용을 모두 입력해주세요.', 'error')
            template_name = f"{board_type}edit.html"
            return render_template(template_name, post=post, row=post, board_type=board_type)
        
        title_field = BOARD_TITLE_FIELDS[board_type]
        content_field = BOARD_CONTENT_FIELDS[board_type]
        
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute(
                f"UPDATE {table_name} SET {title_field} = ?, {content_field} = ? WHERE {id_field} = ?",
                (title, content, post_id)
            )
            db.commit()
        
        flash('게시글이 수정되었습니다.', 'success')
        return redirect(url_for('main.board_show_specific', post_id=post_id))
    
    template_name = f"{board_type}edit.html"
    return render_template(template_name, 
                         post=post,
                         row=post,  # 템플릿에서 사용하는 변수명
                         title=current_app.config['BOARD_NAMES'][board_type])

@main_bp.route('/free/<int:post_id>/delete')
@main_bp.route('/secret/<int:post_id>/delete')
@main_bp.route('/grad/<int:post_id>/delete')
@main_bp.route('/market/<int:post_id>/delete')
@main_bp.route('/new/<int:post_id>/delete')
@main_bp.route('/info/<int:post_id>/delete')
@main_bp.route('/prom/<int:post_id>/delete')
@main_bp.route('/team/<int:post_id>/delete')
def board_delete_specific(post_id):
    """특정 게시글 삭제"""
    board_type = request.path.split('/')[1]
    
    if board_type not in current_app.config['BOARD_TYPES']:
        flash('존재하지 않는 게시판입니다.', 'error')
        return redirect(url_for('main.index'))
    
    table_name = BOARD_TABLES[board_type]
    id_field = BOARD_ID_FIELDS[board_type]
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE {id_field} = ?", (post_id,))
        post = cursor.fetchone()
    
    if not post:
        flash('존재하지 않는 게시글입니다.', 'error')
        return redirect(url_for('main.board_list_specific'))
    
    # 작성자 확인 (로그인한 사용자만 삭제 가능)
    current_user_id = get_current_user_id()
    if not current_user_id or post['id'] != current_user_id:
        flash('게시글을 삭제할 권한이 없습니다.', 'error')
        return redirect(url_for('main.board_show_specific', post_id=post_id))
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE {id_field} = ?", (post_id,))
        db.commit()
    
    flash('게시글이 삭제되었습니다.', 'success')
    return redirect(url_for('main.board_list_specific'))

# 게시글 상세 보기 (더 구체적인 라우트)
@main_bp.route('/free/<int:post_id>')
@main_bp.route('/secret/<int:post_id>')
@main_bp.route('/grad/<int:post_id>')
@main_bp.route('/market/<int:post_id>')
@main_bp.route('/new/<int:post_id>')
@main_bp.route('/info/<int:post_id>')
@main_bp.route('/prom/<int:post_id>')
@main_bp.route('/team/<int:post_id>')
def board_show_specific(post_id):
    """특정 게시글 상세 보기"""
    board_type = request.path.split('/')[1]
    
    if board_type not in current_app.config['BOARD_TYPES']:
        flash('존재하지 않는 게시판입니다.', 'error')
        return redirect(url_for('main.index'))
    
    table_name = BOARD_TABLES[board_type]
    id_field = BOARD_ID_FIELDS[board_type]
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE {id_field} = ?", (post_id,))
        post = cursor.fetchone()
    
    if not post:
        flash('존재하지 않는 게시글입니다.', 'error')
        return redirect(url_for('main.board_list_specific'))
    
    template_name = f"{board_type}show.html"
    return render_template(template_name, 
                         post=post,
                         row=post,  # 템플릿에서 사용하는 변수명
                         title=current_app.config['BOARD_NAMES'][board_type])

# 게시판 목록 (가장 일반적인 라우트를 마지막에 정의)
@main_bp.route('/free')
@main_bp.route('/secret')
@main_bp.route('/grad')
@main_bp.route('/market')
@main_bp.route('/new')
@main_bp.route('/info')
@main_bp.route('/prom')
@main_bp.route('/team')
def board_list_specific():
    """특정 게시판 목록 페이지"""
    board_type = request.path.lstrip('/')
    
    if board_type not in current_app.config['BOARD_TYPES']:
        flash('존재하지 않는 게시판입니다.', 'error')
        return redirect(url_for('main.index'))
    
    table_name = BOARD_TABLES[board_type]
    date_field = BOARD_DATE_FIELDS[board_type]
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY {date_field} DESC LIMIT 8")
        posts = cursor.fetchall()
    
    template_name = f"{board_type}list.html"
    return render_template(template_name, 
                         posts=posts,
                         frees=posts if board_type == 'free' else [],
                         secrets=posts if board_type == 'secret' else [],
                         grads=posts if board_type == 'grad' else [],
                         markets=posts if board_type == 'market' else [],
                         news=posts if board_type == 'new' else [],
                         infos=posts if board_type == 'info' else [],
                         proms=posts if board_type == 'prom' else [],
                         teams=posts if board_type == 'team' else [],
                         title=current_app.config['BOARD_NAMES'][board_type]) 
>>>>>>> d2f9f73d86bfa294f94db90eab8290f45c3a0910
