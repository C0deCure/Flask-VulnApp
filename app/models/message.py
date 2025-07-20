from datetime import datetime
from app.extensions import db

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted_by_sender = db.Column(db.Boolean, default=False)
    is_deleted_by_receiver = db.Column(db.Boolean, default=False)