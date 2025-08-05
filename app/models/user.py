from werkzeug.security import generate_password_hash, check_password_hash
from app import get_db

class User:
    """사용자 모델"""
    
    def __init__(self, id, password=None, created_at=None):
        self.id = id
        self.password = password
        self.created_at = created_at
    
    @staticmethod
    def get(user_id):
        """사용자 조회"""
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row['id'],
                    password=row['password'],
                    created_at=row['created_at']
                )
        return None
    
    def set_password(self, password):
        """비밀번호 해시화"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """비밀번호 확인"""
        return check_password_hash(self.password, password)
    
    def save(self):
        """사용자 저장"""
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO user (id, password) VALUES (?, ?)",
                (self.id, self.password)
            )
            db.commit()
    
    def __repr__(self):
        return f'<User {self.id}>' 