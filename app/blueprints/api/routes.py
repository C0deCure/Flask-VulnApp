<<<<<<< HEAD
<<<<<<< Updated upstream
=======
from flask import jsonify, request, current_app, Blueprint

# 필요한 SQLAlchemy 모델과 객체들을 가져옴
from app.models import Free, Secret, Grad, Market, New, Info, Prom, Team
from app.extensions import db
from sqlalchemy import desc

api_bp = Blueprint('api', __name__)

# main 블루프린트와 동일한 모델 딕셔너리를 사용
BOARD_MODELS = {
    'free': Free, 'secret': Secret, 'grad': Grad, 'market': Market,
    'new': New, 'info': Info, 'prom': Prom, 'team': Team
}

@api_bp.route('/boards/<string:board_type>/posts')
def get_board_posts(board_type):
    """게시판 글 목록 API"""
    model = BOARD_MODELS.get(board_type)
    if not model:
        return jsonify({'error': '존재하지 않는 게시판입니다.'}), 404
    
    # 해당 모델(테이블)에서 최신 글 10개를 가져옴.
    posts = model.query.order_by(desc(model.created_at)).limit(10).all()
=======
from flask import jsonify, request, current_app, Blueprint
from app import get_db

# Blueprint 생성
api_bp = Blueprint('api', __name__)

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

@api_bp.route('/boards/<board_type>/posts')
def get_board_posts(board_type):
    """게시판 글 목록 API"""
    if board_type not in current_app.config['BOARD_TYPES']:
        return jsonify({'error': '존재하지 않는 게시판입니다.'}), 404
    
    table_name = BOARD_TABLES[board_type]
    id_field = f'{board_type[0]}_num'
    title_field = f'{board_type[0]}_title'
    content_field = f'{board_type[0]}_txt'
    date_field = f'{board_type[0]}_date'
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY {date_field} DESC LIMIT 10")
        posts = cursor.fetchall()
>>>>>>> d2f9f73d86bfa294f94db90eab8290f45c3a0910
    
    posts_data = []
    for post in posts:
        posts_data.append({
<<<<<<< HEAD
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author_id,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S')
=======
            'id': post[id_field],
            'title': post[title_field],
            'content': post[content_field],
            'author': post['id'],
            'created_at': post[date_field]
>>>>>>> d2f9f73d86bfa294f94db90eab8290f45c3a0910
        })
    
    return jsonify({
        'board_type': board_type,
<<<<<<< HEAD
        'board_name': current_app.config['BOARD_NAMES'].get(board_type),
        'posts': posts_data
    })

@api_bp.route('/boards/<string:board_type>/posts/<int:post_id>')
def get_board_post(board_type, post_id):
    """게시글 상세 API"""
    model = BOARD_MODELS.get(board_type)
    if not model:
        return jsonify({'error': '존재하지 않는 게시판입니다.'}), 404
    
    # 해당 모델(테이블)에서 id 값으로 게시글을 찾음 없으면 404 에러를 반환
    post = model.query.get_or_404(post_id)
    
    post_data = {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author_id,
        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return jsonify(post_data)
>>>>>>> Stashed changes
=======
        'board_name': current_app.config['BOARD_NAMES'][board_type],
        'posts': posts_data
    })

@api_bp.route('/boards/<board_type>/posts/<int:post_id>')
def get_board_post(board_type, post_id):
    """게시글 상세 API"""
    if board_type not in current_app.config['BOARD_TYPES']:
        return jsonify({'error': '존재하지 않는 게시판입니다.'}), 404
    
    table_name = BOARD_TABLES[board_type]
    id_field = f'{board_type[0]}_num'
    title_field = f'{board_type[0]}_title'
    content_field = f'{board_type[0]}_txt'
    date_field = f'{board_type[0]}_date'
    
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE {id_field} = ?", (post_id,))
        post = cursor.fetchone()
    
    if not post:
        return jsonify({'error': '존재하지 않는 게시글입니다.'}), 404
    
    post_data = {
        'id': post[id_field],
        'title': post[title_field],
        'content': post[content_field],
        'author': post['id'],
        'created_at': post[date_field]
    }
    
    return jsonify(post_data) 
>>>>>>> d2f9f73d86bfa294f94db90eab8290f45c3a0910
