from .extensions import db
from datetime import datetime, timezone
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # User와 Room의 관계는 participant 연결 테이블을 통해 정의
    rooms = db.relationship('Room', secondary='participant', back_populates='users')
    
    @property
    def is_authenticated(self):
        """사용자가 인증되었는지 여부를 반환"""
        return True

    @property
    def is_active(self):
        """사용자가 활성 상태인지 여부를 반환"""
        return True

    def get_id(self):
        """사용자의 고유 ID를 문자열로 반환"""
        return str(self.id)
    
    def set_password(self, password_to_set):
        """비밀번호를 해시하여 저장"""
        self.password = generate_password_hash(password_to_set)

    def check_password(self, password_to_check):
        """입력된 비밀번호가 저장된 해시와 일치하는지 확인"""
        return check_password_hash(self.password, password_to_check)

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    users = db.relationship('User', secondary='participant', back_populates='rooms')
    notes = db.relationship('Note', backref='room', lazy='dynamic', cascade="all, delete-orphan")

# User와 Room의 다대다 관계를 위한 연결 테이블
participant_table = db.Table('participant',
    db.Column('user_id', db.String(80), db.ForeignKey('user.id'), primary_key=True),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True)
)

class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    sender_id = db.Column(db.String(80), db.ForeignKey('user.id'), nullable=False)
    sender = db.relationship('User', backref=db.backref('sent_notes', lazy=True))

# --- 각 게시판 모델 정의 (기존 DB 스키마와 호환) ---

class Free(db.Model):
    __tablename__ = 'free'
    f_num = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(80), db.ForeignKey('user.id'), server_default='익명')
    f_title = db.Column(db.Text, nullable=False)
    f_txt = db.Column(db.Text, nullable=False)
    f_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    author = db.relationship('User', backref='free_posts')

class Secret(db.Model):
    __tablename__ = 'secret'
    s_num = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(80), db.ForeignKey('user.id'), server_default='익명')
    s_title = db.Column(db.Text, nullable=False)
    s_txt = db.Column(db.Text, nullable=False)
    s_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    author = db.relationship('User', backref='secret_posts')

# (Grad, Market, New, Info, Prom, Team 모델도 위와 같은 패턴으로 정의)
class Grad(db.Model):
    __tablename__ = 'grad'
    g_num = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(80), db.ForeignKey('user.id'), server_default='익명')
    g_title = db.Column(db.Text, nullable=False)
    g_txt = db.Column(db.Text, nullable=False)
    g_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    author = db.relationship('User', backref='grad_posts')
    
class Market(db.Model):
    __tablename__ = 'market'
    m_num = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(80), db.ForeignKey('user.id'), server_default='익명')
    m_title = db.Column(db.Text, nullable=False)
    m_txt = db.Column(db.Text, nullable=False)
    m_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    author = db.relationship('User', backref='market_posts')
    
class New(db.Model):
    __tablename__ = 'new'
    n_num = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(80), db.ForeignKey('user.id'), server_default='익명')
    n_title = db.Column(db.Text, nullable=False)
    n_txt = db.Column(db.Text, nullable=False)
    n_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    author = db.relationship('User', backref='new_posts')
    
class Info(db.Model):
    __tablename__ = 'info'
    i_num = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(80), db.ForeignKey('user.id'), server_default='익명')
    i_title = db.Column(db.Text, nullable=False)
    i_txt = db.Column(db.Text, nullable=False)
    i_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    author = db.relationship('User', backref='info_posts')
    
class Prom(db.Model):
    __tablename__ = 'prom'
    p_num = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(80), db.ForeignKey('user.id'), server_default='익명')
    p_title = db.Column(db.Text, nullable=False)
    p_txt = db.Column(db.Text, nullable=False)
    p_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    author = db.relationship('User', backref='prom_posts')
    
class Team(db.Model):
    __tablename__ = 'team'
    t_num = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(80), db.ForeignKey('user.id'), server_default='익명')
    t_title = db.Column(db.Text, nullable=False)
    t_txt = db.Column(db.Text, nullable=False)
    t_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    author = db.relationship('User', backref='team_posts')


# 강의실 기능 관련 ORM 모델 정의
class Lecture(db.Model):
    __tablename__ = 'lecture'
    lecture_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    professor = db.Column(db.String(120), nullable=False)
    campus = db.Column(db.String(50))

    reviews = db.relationship('LectureReview', back_populates='lecture', cascade='all, delete-orphan')
    exams = db.relationship('ExamInfo', back_populates='lecture', cascade='all, delete-orphan')


class LectureReview(db.Model):
    __tablename__ = 'lecture_review'
    r_id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.lecture_id'), nullable=False)
    semester = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False, default='익명')
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # --- 👇 여기에 새로운 필드들을 추가합니다 ---
    rating = db.Column(db.Integer, nullable=True)          # 별점 (1~5)
    homework = db.Column(db.String(20), nullable=True)     # 과제 (많음/보통/없음)
    team_project = db.Column(db.String(20), nullable=True) # 조모임 (많음/보통/없음)
    grading = db.Column(db.String(20), nullable=True)      # 성적 (너그러움/보통/깐깐함)
    attendance = db.Column(db.String(100), nullable=True)  # 출석 (쉼표로 구분된 문자열)
    exam_count = db.Column(db.String(20), nullable=True)   # 시험 횟수
    # ---------------------------------------------

    lecture = db.relationship('Lecture', back_populates='reviews')

class ExamInfo(db.Model):
    __tablename__ = 'exam_info'
    exam_id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.lecture_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    lecture = db.relationship('Lecture', back_populates='exams')


class PointHistory(db.Model):
    __tablename__ = 'point_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), db.ForeignKey('user.id'), nullable=False)
    delta = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(100))
    ref_type = db.Column(db.String(50))
    ref_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
