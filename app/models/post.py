from .. import db
from datetime import datetime

# Post_MAX_Title =
# Post_MAX_DESCRIPTION =

post_upvotes = db.Table(
    'post_upvotes',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

comment_upvotes = db.Table(
    'comment_upvotes',
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Post(db.Model):
    """<UNK> <UNK> <UNK>"""
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    # votes = db.Column(db.Integer, default=0)

    # thumbnail

    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))

    # board = db.relationship('Board', backref=db.backref('posts', lazy='dynamic'))
    # commment = db.relationship('Comment', backref='post', lazy='dynamic')

class Comment(db.Model):
    """<UNK> <UNK> <UNK>"""
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    # votes = db.Column(db.Integer, default=0)
    # depth = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    # parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

    post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic'))
    # children = db.relationship('Comment', backref=db.backref('parent', lazy='dynamic'))
