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

@main_bp.route('/')
def index():
    """메인 페이지 - 각 게시판의 최신 글 4개씩 표시"""
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
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('text')
        
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