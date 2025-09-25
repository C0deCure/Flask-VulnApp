from datetime import datetime
from doctest import master

from flask import Blueprint, url_for, redirect, render_template, request, session, g, flash, abort
from pip._internal import models
from werkzeug.utils import redirect
from flask_login import current_user, login_required

from app.forms import PostForm, CommentForm
from app.models import User, Board, Post, Comment
from app import forms, db


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

board_bp = Blueprint('board', __name__, url_prefix='/board')

# TODO :
@board_bp.route('/<board_url>')
def board_list(board_url):
    """<UNK> <UNK> <UNK>"""
    board = Board.query.filter_by(url=board_url).first_or_404()

    page = request.args.get('page', default=1, type=int)
    post_list = Post.query.filter_by(board_id=board.id)
    post_list = post_list.paginate(page=page, per_page=10)

    return render_template('masterlist.html',
                           board=board,
                           masters=post_list)

# TODO : Modify the template(mastershow) to implement the comment.
@board_bp.route('/<board_url>/<int:post_id>', methods=['GET', 'POST'])
def detail(board_url, post_id):
    """<UNK> <UNK> <UNK>"""
    post = Post.query.get_or_404(post_id)
    board = Board.query.get_or_404(post.board_id)
    return render_template('mastershow.html', board=board, post=post)

# # Is it safe about CSRF?
@board_bp.route('/<board_url>/write', methods=['GET', 'POST'])
@login_required
def write_post(board_url):
    """<UNK> <UNK> <UNK>"""
    board = Board.query.filter_by(url=board_url).first_or_404()
    form = PostForm()
    if request.method == 'POST' and form.validate_on_submit():
        board = Board.query.filter_by(url=board_url).first_or_404()
        post = Post(title=form.title.data, text=form.text.data, user_id=current_user.id, board_id=board.id)
        db.session.add(post)
        db.session.commit()
        # flash('게시글이 작성되었습니다.', 'success')
        return redirect(url_for('board.board_list', board_url=board.url))
    return render_template('masterwrite.html', board=board, form=form)

# # Is it safe about CSRF?
@board_bp.route('/<board_url>/delete/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(board_url, post_id):
    """<UNK> <UNK> <UNK>"""
    post = Post.query.get_or_404(post_id)
    board = Board.query.get_or_404(post.board_id)
    # Considering creating a vulnerability by making the username use only lowercase letters instead of user.id
    if current_user.id != post.user_id:
        # TODO : flash and redirect
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('board.board_list', board_url=board.url))

# TODO : Modify the template to implement that you can see what you wrote before in the editor.
@board_bp.route('/<board_url>/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(board_url, post_id):
    """<UNK> <UNK> <UNK>"""
    post = Post.query.get_or_404(post_id)
    board = Board.query.get_or_404(post.board_id)
    if current_user.id != post.user_id:
        # TODO : flash and redirect
        abort(403)
    if request.method == 'POST':
        form = PostForm()
        if form.validate_on_submit():
            # Is there a vulnerability when populating obj with userid???
            form.populate_obj(post)
            post.updated_at = datetime.now()
            db.session.commit()
            return redirect(url_for('board.board_list', board_url=board.url))
    else:
        form = PostForm(obj=post)

    return render_template('masteredit.html', board=board, post=post, form=form)

# Is it safe about CSRF?
@board_bp.route('/<board_url>/<int:post_id>/comment', methods=['POST'])
@login_required
def create_comment(board_url, post_id):
    """<UNK> <UNK> <UNK>"""
    post = Post.query.get_or_404(post_id)
    board = Board.query.get_or_404(post.board_id)
    form = CommentForm(meta={'csrf': False})
    # form = CommentForm()
    if form.validate_on_submit():
        parent = None
        if form.parent_id.data:
            parent = Comment.query.get(form.parent_id.data)

        comment = Comment(
            text=form.text.data,
            user_id=current_user.id,
            post_id=post.id,
            parent=parent
        )

        post.comments.append(comment)
        db.session.commit()
        return redirect(url_for('board.detail', board_url=board.url, post_id=post.id))
    abort(405)
