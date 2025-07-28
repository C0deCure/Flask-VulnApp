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
    
    posts_data = []
    for post in posts:
        posts_data.append({
            'id': post[id_field],
            'title': post[title_field],
            'content': post[content_field],
            'author': post['id'],
            'created_at': post[date_field]
        })
    
    return jsonify({
        'board_type': board_type,
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