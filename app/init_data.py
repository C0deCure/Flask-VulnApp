from app.models import Board
from app import db

BOARDS = [{"name":"free", "description":"자유게시판", "url":"free"},
          {"name":"secret", "description":"비밀게시판", "url":"secret"},
          {"name":"grad", "description":"졸업게시판", "url":"grad"},
          {"name":"market", "description":"장터", "url":"market"},
          {"name":"new", "description":"새내기게시판", "url":"new"},
          {"name":"info", "description":"정보게시판", "url":"info"},
          {"name":"prom", "description":"홍보게시판", "url":"prom"},
          {"name":"team", "description":"동아리게시판", "url":"team"},]

def insert_default_boards():
    is_added = False
    for board in BOARDS:
        exists = Board.query.filter_by(name=board["name"]).first()
        if not exists:
            is_added = True
            db.session.add(Board(**board))

    if is_added:
        db.session.commit()

