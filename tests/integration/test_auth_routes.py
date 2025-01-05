import pytest
from http import HTTPStatus
from werkzeug.security import generate_password_hash
from app.infrastructure.database.models import UserModel

@pytest.fixture
def test_user(db_session):
    """テストユーザーの作成"""
    user = UserModel(
        id="test-id",
        email="test@example.com",
        name="Test User",
        password_hash=generate_password_hash("Test1234!"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def auth_token(client, test_user):
    """認証トークンを取得"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test1234!'
    })
    return response.get_json()['token']

class TestAuthRoutes:
    """認証ルートのテスト"""

    def test_successful_login(self, client, test_user):
        """正常なログインのテスト"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test1234!'
        })

        assert response.status_code == HTTPStatus.OK
        data = response.get_json()
        assert 'token' in data
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
        assert data['message'] == 'ログインに成功しました'

    def test_invalid_credentials(self, client, test_user):
        """無効な認証情報でのログイン失敗テスト"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPass123!'
        })

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        data = response.get_json()
        assert 'error' in data
        assert 'メールアドレスまたはパスワードが正しくありません' in data['error']

    def test_missing_credentials(self, client):
        """認証情報が不足している場合のテスト"""
        response = client.post('/api/auth/login', json={})

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.get_json()
        assert 'error' in data
        assert '必須フィールドが不足しています' in data['error']

    def test_successful_logout(self, client, auth_token):
        """正常なログアウトのテスト"""
        response = client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == HTTPStatus.OK
        data = response.get_json()
        assert data['message'] == 'ログアウトに成功しました'

    def test_logout_without_token(self, client):
        """トークンなしでのログアウト失敗テスト"""
        response = client.post('/api/auth/logout')

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        data = response.get_json()
        assert 'error' in data
        assert '認証トークンが必要です' in data['error']

    def test_logout_with_invalid_token(self, client):
        """無効なトークンでのログアウト失敗テスト"""
        response = client.post(
            '/api/auth/logout',
            headers={'Authorization': 'Bearer invalid-token'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        data = response.get_json()
        assert 'error' in data
        assert '無効なトークンです' in data['error'] 