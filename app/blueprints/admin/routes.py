from flask import render_template, Blueprint, abort
from flask_login import current_user
import click
from app import db
from app.models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    # 로그인 여부 판단
    if not current_user.is_authenticated:
        abort(401)
    # admin 판단
    if not current_user.is_admin:
        abort(403)

@admin_bp.route('/test')
def test():
    return 'admin test'

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('admin.html', title='Dashboard')

# admin 계정 추가하기
@admin_bp.cli.command('create')
@click.argument('username', default='admin')
def create_admin(username):
    user = User.query.filter_by(username=username).first()
    if user:
        if user.is_admin:
            print(f"[Admin] admin '{username}' already exists.")
            return
        else:
            # 일반 사용자를 관리자로 승격
            user.is_admin = True
            db.session.commit()
            print(f"[Admin] Existing user '{username}' has been promoted to admin.")
            return

    # 새 관리자 계정 생성
    print(f"[Admin] Creating new admin user: '{username}' ...")

    # 테스트용 admin 계정
    # 나중에 수정 필요
    password = click.prompt("Enter password for admin")

    email = f"{username}@example.com"

    try:
        admin_user = User(
            username=username,
            email=email,
            is_admin=True
        )
        admin_user.password = password

        db.session.add(admin_user)
        db.session.commit()

    except Exception as e:
        db.session.rollback()

@admin_bp.cli.command('delete')
@click.argument('username', default='admin')
def delete_admin(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        print(f"[Admin] User '{username}' does not exist.")
        return

    try:
        print(f"[Admin] Deleting user '{username}' ...")
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)