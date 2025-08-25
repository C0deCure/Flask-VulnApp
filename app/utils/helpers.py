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