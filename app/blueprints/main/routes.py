from flask import render_template, request, redirect, url_for, flash, current_app, Blueprint
from flask_login import current_user, login_required

# Blueprint 생성
main_bp = Blueprint('main', __name__)


@main_bp.route('/test')
def test():
    """테스트 페이지"""
    return "Flask 애플리케이션이 정상적으로 작동합니다!"

@main_bp.route('/')
def index():
    """메인 페이지 - 각 게시판의 최신 글 4개씩 표시"""
    try:
        boards_data = {}
        return render_template('index.html', title='에브리타임', **boards_data)
        
    except Exception as e:
        flash(f'오류가 발생했습니다: {str(e)}', 'error')
        return render_template('index.html', title='에브리타임')

