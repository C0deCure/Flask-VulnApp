import os
import urllib.parse
from datetime import datetime
from doctest import master

from flask import Blueprint, url_for, redirect, render_template, request, session, g, flash, abort, current_app, send_file
from pip._internal import models
from werkzeug.utils import redirect, secure_filename
from flask_login import current_user, login_required

from app.forms import PostForm, CommentForm
from app.models import User, Board, Post, Comment
from app import forms, db

import unicodedata

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


def xss_blacklist_filter(text):
    if not text:
        return text

    blacklist = [
        '<script>', '</script>',
        'javascript:',
        'onload', 'onerror',
        'alert',
        'cookie'
    ]

    for word in blacklist:
        text = text.replace(word, "")

    return text

# TODO : Modify the template(mastershow) to implement the comment.
@board_bp.route('/<board_url>/<int:post_id>', methods=['GET', 'POST'])
def detail(board_url, post_id):
    """<UNK> <UNK> <UNK>"""
    post = Post.query.get_or_404(post_id)
    board = Board.query.get_or_404(post.board_id)

    if post.text:
        post.text = xss_blacklist_filter(post.text)

    post.text = unicodedata.normalize('NFKC', post.text)

    return render_template('mastershow.html', board=board, post=post)

# # Is it safe about CSRF?
@board_bp.route('/<board_url>/write', methods=['GET', 'POST'])
@login_required
def write_post(board_url):
    """<UNK> <UNK> <UNK>"""
    board = Board.query.filter_by(url=board_url).first_or_404()
    form = PostForm()

    if request.method == 'POST':
        title = request.form.get('title')
        text = request.form.get('text')

        original_filename = None
        file_url = None

        if 'file_upload' in request.files:
            file = request.files['file_upload']

            if file and file.filename != '':
                safe_filename = ''
                if safe_filename == '':
                    flash('유효하지 않은 파일명입니다.', 'danger')
                    return redirect(url_for('board.write_post', board_url=board_url))

                try:
                    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)

                    os.makedirs(os.path.dirname(save_path), exist_ok=True)

                    file.save(save_path)

                    file_url = f'uploads/{safe_filename}'
                    original_filename = file.filename

                except Exception as e:
                    flash(f"파일 저장 실패! 오류: {e}", "danger")
                    return redirect(url_for('board.write_post', board_url=board_url))

        # DB에 Post 저장 (파일 경로 포함)
        post = Post(title=title,
                    text=text,
                    user_id=current_user.id,
                    board_id=board.id,
                    filename=original_filename,
                    file_url=file_url)

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('board.board_list', board_url=board.url))

    # GET 요청 시
    return render_template('masterwrite.html', board=board, form=form)

# # Is it safe about CSRF?
@board_bp.route('/<board_url>/delete/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(board_url, post_id):
    """<UNK> <UNK> <UNK>"""
    post = Post.query.get_or_404(post_id)
    board = Board.query.get_or_404(post.board_id)
    # Considering creating a vulnerability by making the username use only lowercase letters instead of user.id
    if post.user_id != current_user.id and not current_user.is_admin:
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
    if post.user_id != current_user.id and not current_user.is_admin:
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

@board_bp.route('/view')
def view():
    filename_from_user = request.args.get('filename')
    if not filename_from_user:
        abort(404)

    if '../' in filename_from_user:
        abort(403, "No Hack!!")

    try:
        decoded_filename = urllib.parse.unquote(filename_from_user)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, decoded_filename)
        if not os.path.exists(file_path):
            abort(404)
        return send_file(file_path)
    except FileNotFoundError:
        abort(404)
    except Exception as e:
        return str(e)