from email.policy import default

from .. import db
from datetime import datetime

# BOARD_MAX_NAME =
# BOARD_MAX_DESCRIPTION =

class Board(db.Model):
    """
    <UNK> <UNK> <UNK>
    """
    __tablename__ = 'board'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)
    url = db.Column(db.String, unique=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now())
