from .. import db
from datetime import datetime
from sqlalchemy import UniqueConstraint

# Post_MAX_Title =
# Post_MAX_DESCRIPTION =


class PostVotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.Integer, nullable=False)  # 1 for upvote, -1 for downvote

    # 한 사용자는 한 게시물에 한 번만 투표할 수 있도록 복합 유니크 제약조건 설정
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='_user_post_uc'),)

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
    post_votes = db.relationship('PostVotes', backref='post', lazy=True, cascade="all, delete-orphan")

    # thumbnail

    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))

    # board = db.relationship('Board', backref=db.backref('posts', lazy='dynamic'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    user = db.relationship('User', backref='post')

    @property
    def total_votes(self):
        return sum(vote.value for vote in self.post_votes)

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
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    # self-referential
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    children = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))

    # post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic'))
    # children = db.relationship('Comment', backref=db.backref('parent', lazy='dynamic'))
