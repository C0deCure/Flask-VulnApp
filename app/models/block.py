from app.extensions import db

class Block(db.Model):
    __tablename__ = 'blocks'

    id = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, nullable=False)   # 차단한 사용자
    blocked_id = db.Column(db.Integer, nullable=False)   # 차단당한 사용자

    __table_args__ = (
        db.UniqueConstraint('blocker_id', 'blocked_id', name='unique_block_pair'),
    )