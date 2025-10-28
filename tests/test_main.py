import unittest
from app import create_app, get_db
from app.models.user import User

class TestMain(unittest.TestCase):
    def setUp(self):
        self.app = create_app('development')
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        with self.app.app_context():
            # 테스트용 데이터베이스 초기화
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute("DELETE FROM user")
                cursor.execute("DELETE FROM free")
                cursor.execute("DELETE FROM secret")
                cursor.execute("DELETE FROM grad")
                cursor.execute("DELETE FROM market")
                cursor.execute("DELETE FROM new")
                cursor.execute("DELETE FROM info")
                cursor.execute("DELETE FROM prom")
                cursor.execute("DELETE FROM team")
                db.commit()
    
    def test_index_page(self):
        """메인 페이지 테스트"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_board_list_page(self):
        """게시판 목록 페이지 테스트"""
        response = self.client.get('/free')
        self.assertEqual(response.status_code, 200)
    
    def test_login_page(self):
        """로그인 페이지 테스트"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
    
    def test_register_page(self):
        """회원가입 페이지 테스트"""
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main() 