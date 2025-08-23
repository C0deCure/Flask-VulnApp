from flask import Blueprint, render_template, request, flash, redirect, url_for, g
from flask import render_template_string
from datetime import datetime

# SQLAlchemy 모델과 db 객체, 필요한 함수들을 가져옴
from app.models import User, Room, Note
from app.models import Free, Secret, Grad, Market, New, Info, Prom, Team # 게시판 모델
from app.extensions import db
from sqlalchemy import desc

message_bp = Blueprint('message', __name__, url_prefix='/message')

# 게시판 모델 딕셔너리 (main 블루프린트와 동일하게 사용)
BOARD_MODELS = {
    'free': Free, 'secret': Secret, 'grad': Grad, 'market': Market,
    'new': New, 'info': Info, 'prom': Prom, 'team': Team
}

@message_bp.route('/')
def room_list():
    """쪽지방 목록 보기"""
    # 현재 사용자가 참여한 모든 방을 마지막 메시지 시간 순으로 정렬
    rooms = sorted(g.user.rooms, key=lambda r: (r.notes.order_by(desc(Note.created_at)).first().created_at if r.notes.count() > 0 else datetime.min), reverse=True)

    processed_rooms = []
    for room in rooms:
        other_user = next((u for u in room.users if u.id != g.user.id), None)
        last_note = room.notes.order_by(desc(Note.created_at)).first()
        
        processed_rooms.append({
            'room_id': room.id,
            'other_user_id': other_user.id if other_user else "알수없음",
            'last_message': render_template_string(last_note.content) if last_note else "메시지가 없습니다.",
            'last_date': last_note.created_at if last_note else None
        })
        
    return render_template('message/room_list.html', rooms=processed_rooms)

@message_bp.route('/create', methods=['GET', 'POST'])
def create_room():
    """새로운 상대에게 쪽지를 보내 쪽지방을 생성하는 기능"""
    if request.method == 'POST':
        receiver_id = request.form.get('receiver_id')
        content = request.form.get('content')
        
        receiver = User.query.get(receiver_id)
        if not receiver:
            flash('존재하지 않는 사용자입니다.', 'error')
            return redirect(url_for('message.create_room'))
        
        sender = g.user
        # 두 사용자만 참여하는 방을 찾음
        room = Room.query.join(Room.users).filter(User.id == sender.id).join(Room.users).filter(User.id == receiver.id).first()
        
        if not room: # 방이 없으면 새로 만듬
            room = Room()
            room.users.append(sender)
            room.users.append(receiver)
            db.session.add(room)
            
        new_note = Note(content=content, room=room, sender_id=sender.id)
        db.session.add(new_note)
        db.session.commit()
        
        flash('쪽지를 성공적으로 보냈습니다.', 'success')
        return redirect(url_for('message.room_detail', room_id=room.id))
        
    return render_template('message/create_room_form.html')

@message_bp.route('/<int:room_id>', methods=['GET', 'POST'])
def room_detail(room_id):
    """대화 내용 보기"""
    room = Room.query.get_or_404(room_id)
        
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_note = Note(content=content, room_id=room.id, sender_id=g.user.id)
            db.session.add(new_note)
            db.session.commit()
        return redirect(url_for('message.room_detail', room_id=room.id))

    # 왼쪽 목록용 전체 방 목록 가져오기
    all_rooms = sorted(g.user.rooms, key=lambda r: (r.notes.order_by(desc(Note.created_at)).first().created_at if r.notes.count() > 0 else datetime.min), reverse=True)
    processed_rooms = []
    for r in all_rooms:
        other_user = next((u for u in r.users if u.id != g.user.id), None)
        last_note = r.notes.order_by(desc(Note.created_at)).first()
        processed_rooms.append({'room_id': r.id, 'other_user_id': other_user.id if other_user else "알수없음", 'last_message': render_template_string(last_note.content) if last_note else "", 'last_date': last_note.created_at if last_note else None})

    # 오른쪽 대화 내용 가져오기
    messages = room.notes.order_by(desc(Note.created_at)).all()
    rendered_messages = [{'id': msg.id, 'sender_id': msg.sender_id, 'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'), 'content': render_template_string(msg.content)} for msg in messages]
    
    other_user_name = next((u.id for u in room.users if u.id != g.user.id), "익명")

    return render_template(
        'message/room_detail.html', 
        rooms=processed_rooms,
        messages=rendered_messages,
        current_room_id=room_id,
        current_room_name=other_user_name 
    )

@message_bp.route('/<int:room_id>/delete', methods=['POST'])
def room_delete(room_id):
    """쪽지방 삭제 (ORM 버전)"""
    room = Room.query.get_or_404(room_id)
    # IDOR 취약점을 위해 권한 확인 로직을 의도적으로 생략    
    db.session.delete(room)
    db.session.commit()
    
    flash(f'{room_id}번 쪽지방이 삭제되었습니다.', 'success')
    return redirect(url_for('message.room_list'))

@message_bp.route('/create/from_post/<string:board_type>/<int:post_id>', methods=['GET', 'POST'])
def create_from_post(board_type, post_id):
    """게시물에서 쪽지 보내기 (ORM 버전)"""
    model = BOARD_MODELS.get(board_type)
    if not model:
        flash('존재하지 않는 게시판입니다.', 'error'); return redirect(url_for('main.index'))
    
    # post_id는 각 게시판 모델의 f_num, g_num 등에 해당
    num_attr = f'{board_type[0]}_num'
    post = model.query.filter(getattr(model, num_attr) == post_id).first_or_404()
    receiver_id = post.id # post.id는 작성자 ID
    
    if request.method == 'POST':
        content = request.form.get('content')
        sender = g.user
        receiver = User.query.get(receiver_id)

        # 두 사용자만 참여하는 방을 찾음
        room = db.session.query(Room).join(Room.users).filter(User.id == sender.id).join(Room.users).filter(User.id == receiver.id).first()
        
        if not room: # 방이 없으면 새로 만듬
            room = Room()
            room.users.append(sender)
            room.users.append(receiver)
            db.session.add(room)
            
        new_note = Note(content=content, room=room, sender_id=sender.id)
        db.session.add(new_note)
        db.session.commit()
        
        flash('쪽지를 성공적으로 보냈습니다.', 'success')
        return redirect(url_for('message.room_detail', room_id=room.id))
        
    return render_template('message/create_from_post.html')