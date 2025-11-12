from flask import Blueprint, render_template, request, flash, redirect, url_for, g, current_app # <-- current_app 추가
from flask import render_template_string
from datetime import datetime
from jinja2.exceptions import TemplateSyntaxError
from markupsafe import escape

from app.models import User, Room, Note
from app.models import Free, Secret, Grad, Market, New, Info, Prom, Team
from app.extensions import db
from sqlalchemy import desc, asc

message_bp = Blueprint('message', __name__, url_prefix='/message')

# 게시판 모델 딕셔너리
BOARD_MODELS = {
    'free': Free, 'secret': Secret, 'grad': Grad, 'market': Market,
    'new': New, 'info': Info, 'prom': Prom, 'team': Team
}

@message_bp.route('/')
def room_list():
    """쪽지방 목록 보기"""
    if not g.user:
        flash('로그인이 필요합니다.', 'error'); return redirect(url_for('auth.login'))

    rooms = sorted(g.user.rooms, key=lambda r: (r.notes.order_by(desc(Note.created_at)).first().created_at if r.notes.count() > 0 else datetime.min), reverse=True)

    processed_rooms = []
    for room in rooms:
        other_user = next((u for u in room.users if u.id != g.user.id), None)
        last_note = room.notes.order_by(desc(Note.created_at)).first()

        last_message_content = "메시지가 없습니다."
        if last_note:
            try:
                # SSTI 컨텍스트에 config 객체를 주입
                ssti_context = {'config': current_app.config}
                last_message_content = render_template_string(last_note.content, **ssti_context)
            except TemplateSyntaxError:
                last_message_content = escape(last_note.content)
            except Exception:
                last_message_content = escape(last_note.content)

        processed_rooms.append({
            'room_id': room.id,
            'other_user_username': other_user.username if other_user else "알수없음",
            'last_message': last_message_content,
            'last_date': last_note.created_at if last_note else None
        })

    return render_template('message/room_list.html', rooms=processed_rooms)

@message_bp.route('/<int:room_id>', methods=['GET', 'POST'])
def room_detail(room_id):
    """대화 내용 보기 (config 노출)"""
    if not g.user:
        flash('로그인이 필요합니다.', 'error'); return redirect(url_for('auth.login'))

    room = Room.query.get_or_404(room_id)

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_note = Note(content=content, room_id=room.id, sender_id=g.user.id)
            db.session.add(new_note)
            db.session.commit()
        return redirect(url_for('message.room_detail', room_id=room.id))

    # 왼쪽 목록 (room_list와 동일하게 config 컨텍스트 주입)
    all_rooms = sorted(g.user.rooms, key=lambda r: (r.notes.order_by(desc(Note.created_at)).first().created_at if r.notes.count() > 0 else datetime.min), reverse=True)
    processed_rooms = []
    for r in all_rooms:
        other_user = next((u for u in r.users if u.id != g.user.id), None)
        last_note = r.notes.order_by(desc(Note.created_at)).first()
        last_message_content = ""
        if last_note:
             try:
                 ssti_context = {'config': current_app.config}
                 last_message_content = render_template_string(last_note.content, **ssti_context)
             except TemplateSyntaxError:
                 last_message_content = escape(last_note.content)
             except Exception:
                 last_message_content = escape(last_note.content)
        processed_rooms.append({'room_id': r.id, 'other_user_username': other_user.username if other_user else "알수없음", 'last_message': last_message_content, 'last_date': last_note.created_at if last_note else None})

    messages = room.notes.order_by(desc(Note.created_at)).all()
    rendered_messages = []
    for msg in messages:
        msg_dict = msg.__dict__.copy()
        try:
            ssti_context = {'config': current_app.config}
            msg_dict['content'] = render_template_string(msg.content, **ssti_context)
        except TemplateSyntaxError:
            msg_dict['content'] = escape(msg.content)
        except Exception as e:
            msg_dict['content'] = escape(msg.content)

        msg_dict['created_at'] = msg.created_at.strftime('%Y-%m-%d %H:%M')
        rendered_messages.append(msg_dict)

    other_user_name = next((u.username for u in room.users if u.id != g.user.id), "익명")

    return render_template(
        'message/room_detail.html',
        rooms=processed_rooms,
        messages=rendered_messages,
        current_room_id=room_id,
        current_room_name=other_user_name
    )

@message_bp.route('/create/from_post/<string:board_type>/<int:post_id>', methods=['GET', 'POST'])
def create_from_post(board_type, post_id):
    """게시물에서 쪽지 보내기 (GET: 작성 페이지, POST: 전송 처리)"""
    if not g.user:
        flash('로그인이 필요합니다.', 'error'); return redirect(url_for('auth.login'))

    model = BOARD_MODELS.get(board_type)
    if not model:
        flash('존재하지 않는 게시판입니다.', 'error'); return redirect(url_for('main.index'))
    
    num_attr = f'{board_type[0]}_num'
    post = model.query.filter(getattr(model, num_attr) == post_id).first_or_404()
    
    receiver = User.query.get(post.author_id)
    if not receiver:
        flash('수신자를 찾을 수 없습니다.', 'error'); return redirect(request.referrer)

    # --- POST 요청 (쪽지 전송) 처리 ---
    if request.method == 'POST':
        if receiver.id == g.user.id:
            flash('자기 자신에게는 쪽지를 보낼 수 없습니다.', 'error')
            return redirect(url_for('main.board_show', board_type=board_type, post_id=post_id))

        content = request.form.get('content')
        if not content:
            flash('내용을 입력해주세요.', 'error')
            return redirect(url_for('message.create_from_post', board_type=board_type, post_id=post_id))

        sender = g.user
        room = Room.query.filter(Room.users.any(User.id == sender.id)).filter(Room.users.any(User.id == receiver.id)).first()
            
        if not room:
            room = Room()
            room.users.append(sender)
            room.users.append(receiver)
            db.session.add(room)
                
        new_note = Note(content=content, room=room, sender_id=sender.id)
        db.session.add(new_note)
        db.session.commit()
        
        flash('쪽지를 성공적으로 보냈습니다.', 'success')
        return redirect(url_for('message.room_detail', room_id=room.id))
    
    # --- GET 요청 (쪽지 작성 페이지 보여주기) ---
    # 이제 GET 요청이 오면 이 부분이 실행됩니다.
    return render_template('message/create_from_post.html', receiver=receiver)

@message_bp.route('/create', methods=['GET', 'POST'])
def create_room():
    """새로운 상대에게 쪽지를 보내 쪽지방을 생성하는 기능"""
    if not g.user:
        flash('로그인이 필요합니다.', 'error'); return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # form에서 받는 사람의 username을 받음
        receiver_username = request.form.get('receiver_username')
        content = request.form.get('content')
        
        if not all([receiver_username, content]):
            flash('받는 사람과 내용을 모두 입력해주세요.', 'error')
            return redirect(url_for('message.create_room'))

        # username으로 User 객체를 찾음
        receiver = User.query.filter_by(username=receiver_username).first()
        if not receiver:
            flash('존재하지 않는 사용자입니다.', 'error')
            return redirect(url_for('message.create_room'))

        if receiver.id == g.user.id:
            flash('자기 자신에게는 쪽지를 보낼 수 없습니다.', 'error')
            return redirect(url_for('message.create_room'))

        sender = g.user
        room = Room.query.filter(Room.users.any(User.id == sender.id)).filter(Room.users.any(User.id == receiver.id)).first()
        
        if not room:
            room = Room()
            room.users.append(sender)
            room.users.append(receiver)
            db.session.add(room)
            
        new_note = Note(content=content, room=room, sender_id=sender.id)
        db.session.add(new_note)
        db.session.commit()
        
        flash('쪽지를 성공적으로 보냈습니다.', 'success')
        return redirect(url_for('message.room_detail', room_id=room.id))
        
    return render_template('message/create_room.html')

@message_bp.route('/<int:room_id>/delete', methods=['POST'])
def room_delete(room_id):
    """쪽지방 삭제"""
    if not g.user:
        flash('로그인이 필요합니다.', 'error'); return redirect(url_for('auth.login'))
        
    room = Room.query.get_or_404(room_id)
    # IDOR 취약점을 위해 현재 사용자가 방에 참여했는지 권한 확인 로직을 의도적으로 생략
    db.session.delete(room)
    db.session.commit()
    
    flash(f'{room_id}번 쪽지방이 삭제되었습니다.', 'success')
    return redirect(url_for('message.room_list'))

