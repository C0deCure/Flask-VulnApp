<<<<<<< Updated upstream
=======
from datetime import datetime

def format_datetime(dt):
    """날짜 시간 포맷팅"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%d %H:%M')

def nl2br(text):
    """줄바꿈을 <br> 태그로 변환"""
    if text:
        return text.replace('\n', '<br>')
    return text

def truncate_text(text, length=100):
    """텍스트 자르기"""
    if len(text) <= length:
        return text
    return text[:length] + '...' 

from app.models import PointHistory

def has_unlocked_exam(user_id: str, exam_id: int) -> bool:
    """해당 사용자가 특정 시험 정보를 열람한 적이 있는지 확인"""
    return PointHistory.query.filter_by(
        user_id=user_id,
        reason="EXAM_INFO_VIEW",
        ref_type="exam_info",
        ref_id=exam_id
    ).first() is not None
>>>>>>> Stashed changes
