from flask import jsonify, request, current_app, Blueprint
from app.models import Board, Post, Comment, User

# Blueprint 생성
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

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

@api_bp.route('/boardcard', methods=['GET'])
def get_boardcard():
    boards = Board.query.all()
    result = []

    for board in boards:
        latest_posts = (Post.query.filter_by(board_id=board.id).limit(3).all())
        result.append({
            'board_name': board.name,
            "url": board.url,
            "posts": [
                {
                    "id": post.id,
                    "title": post.title
                }
                for post in latest_posts
            ]
        })
    return jsonify(result)

@api_bp.route('/comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    # comment.user_id
    result = []
    for comment in comments:
        result.append({
            "id": comment.id,
            "text": comment.text,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "user_name": comment.user.username,
        })

    return jsonify(result)