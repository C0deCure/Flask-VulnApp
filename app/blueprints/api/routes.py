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
    
    posts_data = []
    for post in posts:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author_id,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'board_type': board_type,
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