from flask import jsonify, request, current_app, Blueprint, abort
from flask_login import current_user, login_required
from app.models import Board, Post, Comment, User, PostVotes
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
            "user_id": comment.user.id,
        })

    return jsonify(result)

# edit comment
@api_bp.route("/comments/<int:comment_id>", methods=["PUT", "PATCH"])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        abort(404, description="Comment not found")

    if comment.user_id != current_user.id:
        abort(403, description="You are not authorized to perform this action.")

    data = request.get_json()
    new_content = data.get("text")
    if not new_content:
        abort(400, description="Content is required")

    try:
        print(f"Updating comment {comment_id} to: {new_content}")
        comment.text = new_content
        db.session.commit()
        print("Commit successful!")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
        abort(500, description="Failed to update comment due to a database error.")

    print(new_content)
    print(f"Is comment object dirty? {comment in db.session.dirty}")

    db.session.commit()

    return jsonify({"message": "Comment updated", "comment": {"id": comment.id, "content": comment.text}})

# erase comment
# TODO : login_required (coment CRUD)
@api_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        abort(404, description="Comment not found")

    if comment.user_id != current_user.id:
        abort(403, description="You are not authorized to perform this action.")

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment deleted"})

@api_bp.route("/posts/<int:post_id>/vote", methods=["POST"])
@login_required
def vote_post(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    new_value = data.get('value') # 클라이언트가 보낸 값 (1 또는 -1)

    if new_value not in [1, -1]:
        return jsonify({"error": "Invalid vote value."}), 400

    # 현재 사용자가 이 게시물에 이미 투표했는지 확인
    existing_vote = PostVotes.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if existing_vote:
        # 이미 같은 투표를 했다면 (예: 추천을 또 누름) -> 투표 취소
        if existing_vote.value == new_value:
            db.session.delete(existing_vote)
        # 다른 투표를 했다면 (예: 비추천 -> 추천) -> 투표 변경
        else:
            existing_vote.value = new_value
    else:
        # 첫 투표라면 -> 새로운 투표 기록 생성
        new_vote = PostVotes(user_id=current_user.id, post_id=post.id, value=new_value)
        db.session.add(new_vote)

    db.session.commit()

    # 프론트엔드에서 UI를 업데이트할 수 있도록 최신 정보를 반환
    user_vote_value = PostVotes.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    return jsonify({
        "message": "Vote processed successfully.",
        "total_votes": post.total_votes,
        "user_vote": user_vote_value.value if user_vote_value else 0 # 사용자의 현재 투표 상태 (없으면 0)
    })
