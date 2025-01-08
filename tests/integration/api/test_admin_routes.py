"""
管理者関連のAPIエンドポイントのテスト
"""
import pytest
import json
from http import HTTPStatus
from datetime import datetime
from app import create_app, db
from app.infrastructure.database.models import UserModel
from app.domain.value_objects.role import RoleType

# テストデータ
TEST_SUPER_ADMIN_EMAIL = "super.admin@example.com"
TEST_SUPER_ADMIN_PASSWORD = "SuperAdmin123!"
TEST_SUPER_ADMIN_NAME = "Test Super Admin"

@pytest.fixture
def app():
    """テスト用のFlaskアプリケーションを作成"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key'
    })
    return app

@pytest.fixture
def test_client(app):
    """テスト用のクライアントを作成"""
    return app.test_client()

@pytest.fixture(autouse=True)
def init_database(app):
    """テスト用のデータベースを初期化"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

def test_successful_super_admin_registration(test_client):
    """
    正常系: スーパー管理者登録が成功するケース
    """
    # リクエストデータ
    data = {
        'email': TEST_SUPER_ADMIN_EMAIL,
        'password': TEST_SUPER_ADMIN_PASSWORD,
        'name': TEST_SUPER_ADMIN_NAME
    }

    # APIリクエストの実行
    response = test_client.post(
        '/api/admin/super-admin/register',
        data=json.dumps(data),
        content_type='application/json'
    )

    # レスポンスの検証
    assert response.status_code == HTTPStatus.CREATED
    response_data = json.loads(response.data)
    assert 'user' in response_data
    assert response_data['user']['email'] == TEST_SUPER_ADMIN_EMAIL
    assert response_data['user']['name'] == TEST_SUPER_ADMIN_NAME
    assert response_data['user']['role'] == RoleType.SUPER_ADMIN.value
    assert response_data['user']['is_active'] is True

    # データベースに保存されたことを確認
    with test_client.application.app_context():
        user = UserModel.query.filter_by(email=TEST_SUPER_ADMIN_EMAIL).first()
        assert user is not None
        assert user.email == TEST_SUPER_ADMIN_EMAIL
        assert user.name == TEST_SUPER_ADMIN_NAME
        assert user.role == RoleType.SUPER_ADMIN

def test_successful_super_admin_login(test_client):
    """
    正常系: スーパー管理者ログインが成功するケース
    """
    # スーパー管理者を事前に登録
    register_data = {
        'email': TEST_SUPER_ADMIN_EMAIL,
        'password': TEST_SUPER_ADMIN_PASSWORD,
        'name': TEST_SUPER_ADMIN_NAME
    }
    test_client.post(
        '/api/admin/super-admin/register',
        data=json.dumps(register_data),
        content_type='application/json'
    )

    # ログインリクエスト
    login_data = {
        'email': TEST_SUPER_ADMIN_EMAIL,
        'password': TEST_SUPER_ADMIN_PASSWORD
    }
    response = test_client.post(
        '/api/auth/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )

    # レスポンスの検証
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.data)
    assert 'token' in response_data
    assert 'user' in response_data
    assert response_data['user']['email'] == TEST_SUPER_ADMIN_EMAIL
    assert response_data['user']['name'] == TEST_SUPER_ADMIN_NAME

def test_duplicate_super_admin_registration(test_client):
    """
    異常系: 2人目のスーパー管理者登録を試みるケース
    """
    # 最初のスーパー管理者を登録
    data = {
        'email': TEST_SUPER_ADMIN_EMAIL,
        'password': TEST_SUPER_ADMIN_PASSWORD,
        'name': TEST_SUPER_ADMIN_NAME
    }
    test_client.post(
        '/api/admin/super-admin/register',
        data=json.dumps(data),
        content_type='application/json'
    )

    # 2人目のスーパー管理者の登録を試みる
    second_admin_data = {
        'email': "second.super.admin@example.com",
        'password': TEST_SUPER_ADMIN_PASSWORD,
        'name': "Second Super Admin"
    }
    response = test_client.post(
        '/api/admin/super-admin/register',
        data=json.dumps(second_admin_data),
        content_type='application/json'
    )

    # レスポンスの検証
    assert response.status_code == HTTPStatus.BAD_REQUEST
    response_data = json.loads(response.data)
    assert 'error' in response_data

def test_super_admin_login_with_invalid_credentials(test_client):
    """
    異常系: 不正な認証情報でスーパー管理者ログインを試みるケース
    """
    # スーパー管理者を事前に登録
    register_data = {
        'email': TEST_SUPER_ADMIN_EMAIL,
        'password': TEST_SUPER_ADMIN_PASSWORD,
        'name': TEST_SUPER_ADMIN_NAME
    }
    test_client.post(
        '/api/admin/super-admin/register',
        data=json.dumps(register_data),
        content_type='application/json'
    )

    # 不正なパスワードでログイン
    login_data = {
        'email': TEST_SUPER_ADMIN_EMAIL,
        'password': 'WrongPassword123!'
    }
    response = test_client.post(
        '/api/auth/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )

    # レスポンスの検証
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    response_data = json.loads(response.data)
    assert 'error' in response_data 