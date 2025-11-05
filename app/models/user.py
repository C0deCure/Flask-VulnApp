from werkzeug.security import generate_password_hash, check_password_hash
from app import get_db

class User:
    """사용자 모델"""
    
    def __init__(self, id, password=None, name=None, student_number=None, department=None, email=None, phone=None, terms_agreed=0, created_at=None):
        self.id = id
        self.password = password
        self.name = name
        self.student_number = student_number
        self.department = department
        self.email = email
        self.phone = phone
        self.terms_agreed = terms_agreed
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
                    name=row['name'],
                    student_number=row['student_number'],
                    department=row['department'],
                    email=row['email'],
                    phone=row['phone'],
                    terms_agreed=row['terms_agreed'],
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
                "INSERT OR REPLACE INTO user (id, password, name, student_number, department, email, phone, terms_agreed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (self.id, self.password, self.name, self.student_number, self.department, self.email, self.phone, self.terms_agreed)
            )
            db.commit()
    
    def __repr__(self):
        return f'<User {self.id}>' 