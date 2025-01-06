import pytest
from http import HTTPStatus
from app.domain.value_objects.role import RoleType
from app.infrastructure.database.models import UserModel


class TestAdminRoutes:
    """管理者ルートのテスト"""

    def test_successful_super_admin_registration(self, client):
        """正常なスーパー管理者登録のテスト"""
        response = client.post('/api/admin/super-admin/register', json={
            'email': 'admin@example.com',
            'password': 'Admin1234!',
            'name': 'Super Admin'
        })

        assert response.status_code == HTTPStatus.CREATED
        data = response.get_json()
        assert data['message'] == 'スーパー管理者の登録が完了しました'
        assert data['user']['email'] == 'admin@example.com'
        assert data['user']['name'] == 'Super Admin'
        assert data['user']['role'] == RoleType.SUPER_ADMIN.value

    def test_duplicate_super_admin_registration(self, client, db_session):
        """重複したスーパー管理者登録のテスト"""
        # 最初のスーパー管理者を登録
        client.post('/api/admin/super-admin/register', json={
            'email': 'admin@example.com',
            'password': 'Admin1234!',
            'name': 'Super Admin'
        })

        # 2人目のスーパー管理者を登録しようとする
        response = client.post('/api/admin/super-admin/register', json={
            'email': 'admin2@example.com',
            'password': 'Admin1234!',
            'name': 'Super Admin 2'
        })

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'スーパー管理者はすでに登録されています'

    def test_invalid_email_format(self, client):
        """無効なメールアドレス形式でのテスト"""
        response = client.post('/api/admin/super-admin/register', json={
            'email': 'invalid-email',
            'password': 'Admin1234!',
            'name': 'Super Admin'
        })

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.get_json()
        assert 'error' in data
        assert '無効なメールアドレス形式です' in data['error']

    def test_weak_password(self, client):
        """弱いパスワードでのテスト"""
        response = client.post('/api/admin/super-admin/register', json={
            'email': 'admin@example.com',
            'password': 'weak',
            'name': 'Super Admin'
        })

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.get_json()
        assert 'error' in data
        assert 'パスワード' in data['error']

    def test_missing_required_fields(self, client):
        """必須フィールドが不足している場合のテスト"""
        response = client.post('/api/admin/super-admin/register', json={
            'email': 'admin@example.com'
        })

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == '必須フィールドが不足しています' 