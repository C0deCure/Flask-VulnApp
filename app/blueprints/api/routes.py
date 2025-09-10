from flask import jsonify, request, current_app, Blueprint, abort
from app.models import Board, Post, Comment, User
from app import db

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

# edit comment
@api_bp.route("/comments/<int:comment_id>", methods=["PUT", "PATCH"])
def update_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        abort(404, description="Comment not found")

    data = request.get_json()
    new_content = data.get("text")
    if not new_content:
        abort(400, description="Content is required")

    comment.content = new_content
    db.session.commit()

    return jsonify({"message": "Comment updated", "comment": {"id": comment.id, "content": comment.text}})

# erase comment
@api_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        abort(404, description="Comment not found")

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment deleted"})
