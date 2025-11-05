from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager, verify_jwt_token

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.request_loader
def load_user_from_request(request):
    """현재 사용자 정보 가져오기"""
    token = request.cookies.get('auth_token')
    if token:
        user_id = verify_jwt_token(token)
        if user_id:
            return User.query.get(user_id)
    return None


class User(db.Model, UserMixin):
    """사용자 모델"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = generate_password_hash(plain_text_password)

    def check_password(self, attempted_password):
        """비밀번호 확인"""
        return check_password_hash(self.password_hash, attempted_password)
    
    def save(self):
        """사용자 저장"""
        pass
    
    def __repr__(self):
        return f'<User {self.id}>' 