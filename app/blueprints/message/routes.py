from flask import Blueprint, render_template, request, flash, redirect, url_for, g
from flask import render_template_string # SSTI 취약점 구현을 위해 사용
from app.models.user import User # User 모델 import 
from app import get_db
from datetime import datetime

# message Blueprint 생성
message_bp = Blueprint('message', __name__, url_prefix='/message')
    
@message_bp.before_request
def load_logged_in_user():
    g.user = {'id': 'hacker'}

    if g.user is None:
        # 이 부분은 나중에 실제 JWT 로그인 기능으로 대체.
        return redirect(url_for('auth.login'))
    
# 1. 쪽지방 목록 보기
@message_bp.route('/')
def room_list():
    """/message - 쪽지방 목록을 보여주는 메인 페이지"""
    db = get_db()
    
    # 현재 사용자가 참여한 room 목록을 가져오기
    query = """
        SELECT
            r.id as room_id,
            p2.user_id as other_user_id,
            last_note.content as last_message,
            last_note.created_at as last_date
        FROM room r
        JOIN participant p1 ON r.id = p1.room_id
        JOIN participant p2 ON r.id = p2.room_id
        LEFT JOIN (
            SELECT room_id, content, created_at, ROW_NUMBER() OVER(PARTITION BY room_id ORDER BY created_at DESC) as rn
            FROM note
        ) last_note ON r.id = last_note.room_id AND last_note.rn = 1
        WHERE p1.user_id = ? AND p2.user_id != ?
        ORDER BY last_date DESC;
    """
    
    rooms_from_db = db.execute(query, (g.user['id'], g.user['id'])).fetchall()
    
    # DB에서 가져온 날짜를 datetime 객체로 변환
    processed_rooms = []
    for room in rooms_from_db:
        room_dict = dict(room)
        if room_dict.get('last_date'):
            room_dict['last_date'] = datetime.strptime(room_dict['last_date'], '%Y-%m-%d %H:%M:%S')
        
        if room_dict.get('last_message'):
            room_dict['last_message'] = render_template_string(room_dict['last_message'])
        
        processed_rooms.append(room_dict)
        
    
    return render_template('message/room_list.html', rooms=processed_rooms)

# 2. 새 쪽지 보내기 (쪽지방 생성)
@message_bp.route('/create', methods=['GET', 'POST'])
def create_room():
    """새로운 상대에게 쪽지를 보내 쪽지방을 생성하는 기능"""
    if request.method == 'POST':
        receiver_id = request.form.get('receiver_id')
        content = request.form.get('content')
        
        if not User.get(receiver_id):
            flash('존재하지 않는 사용자입니다.', 'error')
            return redirect(url_for('message.create_room'))
        
        db = get_db()
        # TODO: 두 사람 간의 방이 있는지 확인하느 로직이 필요할까?
        
        # 1. 새로운 방 생성
        cursor = db.execute('INSERT INTO room DEFAULT VALUES')
        room_id = cursor.lastrowid
        
        # 2. 참여자 추가 (보내는 사람, 받는 사람)
        db.execute('INSERT INTO participant (room_id, user_id) VALUES (?, ?)', (room_id, g.user['id']))
        db.execute('INSERT INTO participant (room_id, user_id) VALUES (?, ?)', (room_id, receiver_id))
        
        # 3. 첫 메시지 저장 ( SSTI 주입 지점 )
        db.execute(
            'INSERT INTO note (room_id, sender_id, content) VALUES (?, ?, ?)',
            (room_id, g.user['id'], content)
        )
        
        db.commit()
        
        return redirect(url_for('message.room_detail', room_id=room_id))
    
    return render_template('message/create_room_form.html')

# 3. 특정 쪽지방 대화 내용 보기 & 답장
@message_bp.route('/<int:room_id>', methods=['GET', 'POST'])
def room_detail(room_id):
    """/message/<쪽지방ID> - 대화 내용 보기 및 답장 보내기"""
    db = get_db()
    
    # IDOR (열람) 취약점 구현
    # --- POST 요청 (답장 보내기) ---
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            # SSTI 취약점 구현
            db.execute(
                'INSERT INTO note (room_id, sender_id, content) VALUES (?, ?, ?)',
                (room_id, g.user['id'], content)
            )
            db.commit()
        return redirect(url_for('message.room_detail', room_id=room_id))
    
    # --- GET 요청 (대화 내용 보기) ---
    messages_from_db = db.execute('SELECT * FROM note WHERE room_id = ? ORDER BY created_at DESC', (room_id,)).fetchall()
    
    rendered_messages = []
    for msg in messages_from_db:
        # SSTI 실행
        rendered_content = render_template_string(msg['content'])
        rendered_messages.append({**msg, 'content': rendered_content})
        
    query = """
        SELECT
            r.id as room_id,
            p2.user_id as other_user_id,
            (SELECT content FROM note WHERE room_id = r.id ORDER BY created_at DESC LIMIT 1) as last_message,
            (SELECT created_at FROM note WHERE room_id = r.id ORDER BY created_at DESC LIMIT 1) as last_date
        FROM room r
        JOIN participant p1 ON r.id = p1.room_id
        JOIN participant p2 ON r.id = p2.room_id
        WHERE p1.user_id = ? AND p2.user_id != ?
        ORDER BY last_date DESC;
    """
    rooms_from_db = db.execute(query, (g.user['id'], g.user['id'])).fetchall()
    
    # DB에서 가져온 날짜(문자열)를 datetime 객체로 변환
    processed_rooms = []
    for room in rooms_from_db:
        room_dict = dict(room)
        if room_dict.get('last_date'):
            room_dict['last_date'] = datetime.strptime(room_dict['last_date'], '%Y-%m-%d %H:%M:%S')
        
        if room_dict.get('last_message'):
            room_dict['last_message'] = render_template_string(room_dict['last_message'])
        
        processed_rooms.append(room_dict)
        
    other_user_name = "익명" # 기본값
    for room in processed_rooms:
        if room['room_id'] == room_id:
            other_user_name = room['other_user_id']
            break
    
    # 3. 템플릿에 필요한 모든 데이터를 전달
    return render_template(
        'message/room_detail.html', 
        rooms=processed_rooms,
        messages=rendered_messages,
        current_room_id=room_id,
        current_room_name=other_user_name 
    )

# 4. 쪽지방 삭제
@message_bp.route('/<int:room_id>/delete', methods=['POST'])
def room_delete(room_id):
    """/message/<쪽지방ID>/delete - 쪽지방과 모든 메시지 삭제"""
    db = get_db()
    
    # IDOR (삭제) 취약점 구현
    db.execute('DELETE FROM note WHERE room_id = ?', (room_id,))
    db.execute('DELETE FROM participant WHERE room_id = ?', (room_id,))
    db.execute('DELETE FROM room WHERE id = ?', (room_id,))
    db.commit()
    
    flash(f'{room_id}번 쪽지방이 삭제되었습니다.', 'success')
    return redirect(url_for('message.room_list'))

@message_bp.route('/create/from_post/<string:board_type>/<int:post_id>', methods=['GET', 'POST'])
def create_from_post(board_type, post_id):
    """게시물 작성자에게 쪽지를 보내는 기능"""
    db = get_db()
    board_map = {
        'free': {'table': 'free', 'num_col': 'f_num', 'author_col': 'id'},
        'secret': {'table': 'secret', 'num_col': 's_num', 'author_col': 'id'},
        'grad': {'table': 'grad', 'num_col': 'g_num', 'author_col': 'id'},
        'market': {'table': 'market', 'num_col': 'm_num', 'author_col': 'id'},
        'new': {'table': 'new', 'num_col': 'n_num', 'author_col': 'id'},
        'info': {'table': 'info', 'num_col': 'i_num', 'author_col': 'id'},
        'prom': {'table': 'prom', 'num_col': 'p_num', 'author_col': 'id'},
        'team': {'table': 'team', 'num_col': 't_num', 'author_col': 'id'}
        }
    if board_type not in board_map:
        flash('잘못된 게시판 정보입니다', 'error')
        return redirect(url_for('main.index'))
    board_info = board_map[board_type]
    query = f'SELECT {board_info['author_col']} FROM {board_info['table']} WHERE {board_info['num_col']} = ?'
    author_row = db.execute(query, (post_id,)).fetchone()
    if not author_row:
        flash('존재하지 않는 게시물입니다.', 'error')
        return redirect(url_for('main.index'))
    receiver_id = author_row[0]
    if receiver_id == g.user['id']:
        flash('자기 자신에게는 쪽지를 보낼 수 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    # --- POST 요청 처리 ---
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('내용을 입력해주세요.', 'error')
            return render_template('message/create_from_post.html')
        
        # 1. 두 사용자(현재 유저, 받는 유저)가 모두 참여한 방을 찾음
        sender_id = g.user['id']
        find_room_query = """
            SELECT p1.room_id
            FROM participant p1
            JOIN participant p2 ON p1.room_id = p2.room_id
            WHERE p1.user_id = ? AND p2.user_id = ?
        """
        existing_room = db.execute(find_room_query, (sender_id, receiver_id)).fetchone()
        
        room_id = None
        if existing_room:
            # 2. 만약 방이 존재하면 그 방의 ID 사용
            room_id = existing_room['room_id']
        else:
            # 3. 방이 존재하지 않으면 새로운 방 생성
            cursor = db.execute('INSERT INTO room DEFAULT VALUES')
            room_id = cursor.lastrowid
            db.execute('INSERT INTO participant (room_id, user_id) VALUES (?, ?)', (room_id, sender_id))
            db.execute('INSERT INTO participant (room_id, user_id) VALUES (?, ?)', (room_id, receiver_id))
        
        # 4. 결정된 room_id를 사용하여 메시지를 저장
        db.execute(
            'INSERT INTO note (room_id, sender_id, content) VALUES (?, ?, ?)',
            (room_id, sender_id, content)
        )
        db.commit()
        
        flash('쪽지를 성공적으로 보냈습니다.', 'success')
        return redirect(url_for('message.room_detail', room_id=room_id))
    
    # --- GET 요청 처리 ---
    return render_template('message/create_from_post.html')