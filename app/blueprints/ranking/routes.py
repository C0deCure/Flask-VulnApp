from flask import render_template, request, redirect, url_for, flash, current_app
from app import get_db
from app.blueprints.ranking import ranking_bp

@ranking_bp.route('/ranking')
def ranking():
    """학과별 랭킹 페이지"""
    try:
        with get_db() as db:
            cursor = db.cursor()
            # 학과별 학생 수 조회
            cursor.execute("""
                SELECT major, COUNT(*) as student_count 
                FROM user 
                WHERE major IS NOT NULL AND major != '' 
                GROUP BY major 
                ORDER BY student_count DESC 
                LIMIT 5
            """)
            major_rankings = cursor.fetchall()
            
            # 랭킹 데이터 생성 (1명당 1000포인트)
            rankings = []
            for i, row in enumerate(major_rankings, 1):
                major_name = row['major']
                student_count = row['student_count']
                points = student_count * 1000
                
                rankings.append({
                    'rank': i,
                    'major': major_name,
                    'student_count': student_count,
                    'points': points
                })
        
        return render_template('ranking.html', 
                             title='학과별 랭킹', 
                             rankings=rankings)
        
    except Exception as e:
        flash(f'랭킹 정보를 불러오는 중 오류가 발생했습니다: {str(e)}', 'error')
        return render_template('ranking.html', 
                             title='학과별 랭킹', 
                             rankings=[])

@ranking_bp.route('/ranking/api')
def ranking_api():
    """랭킹 데이터 API (JSON 형태로 반환)"""
    try:
        with get_db() as db:
            cursor = db.cursor()
            # 학과별 학생 수 조회
            cursor.execute("""
                SELECT major, COUNT(*) as student_count 
                FROM user 
                WHERE major IS NOT NULL AND major != '' 
                GROUP BY major 
                ORDER BY student_count DESC 
                LIMIT 5
            """)
            major_rankings = cursor.fetchall()
            
            # 랭킹 데이터 생성 (1명당 1000포인트)
            rankings = []
            for i, row in enumerate(major_rankings, 1):
                major_name = row['major']
                student_count = row['student_count']
                points = student_count * 1000
                
                rankings.append({
                    'rank': i,
                    'major': major_name,
                    'student_count': student_count,
                    'points': points
                })
        
        return {
            'success': True,
            'rankings': rankings,
            'total_majors': len(rankings)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'랭킹 정보를 불러오는 중 오류가 발생했습니다: {str(e)}',
            'rankings': []
        }
