from flask import Blueprint

# Blueprint 생성
ranking_bp = Blueprint('ranking', __name__)

# 라우트 임포트 (순환 임포트 방지)
from app.blueprints.ranking import routes
