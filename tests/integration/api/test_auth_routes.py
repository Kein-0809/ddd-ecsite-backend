"""
認証関連のAPIエンドポイントのテスト
"""
import pytest
import json
from http import HTTPStatus
from datetime import datetime
from app import create_app, db
from app.infrastructure.database.models import UserModel
from app.domain.value_objects.role import RoleType

# テストデータ
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Password123!"
TEST_NAME = "Test User"

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

def test_successful_user_registration(test_client):
    """
    正常系: ユーザー登録が成功するケース
    """
    # リクエストデータ
    data = {
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
        'name': TEST_NAME
    }

    # APIリクエストの実行
    response = test_client.post(
        '/api/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )

    # レスポンスの検証
    assert response.status_code == HTTPStatus.CREATED
    response_data = json.loads(response.data)
    assert 'token' in response_data
    assert 'user' in response_data
    assert response_data['user']['email'] == TEST_EMAIL
    assert response_data['user']['name'] == TEST_NAME
    assert response_data['user']['role'] == RoleType.USER.value

    # データベースに保存されたことを確認
    with test_client.application.app_context():
        user = UserModel.query.filter_by(email=TEST_EMAIL).first()
        assert user is not None
        assert user.email == TEST_EMAIL
        assert user.name == TEST_NAME
        assert user.role == RoleType.USER

def test_duplicate_email_registration(test_client):
    """
    異常系: 既存のメールアドレスで登録を試みるケース
    """
    # 最初のユーザーを登録
    data = {
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
        'name': TEST_NAME
    }
    test_client.post(
        '/api/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )

    # 同じメールアドレスで2回目の登録を試みる
    response = test_client.post(
        '/api/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )

    # レスポンスの検証
    assert response.status_code == HTTPStatus.CONFLICT
    response_data = json.loads(response.data)
    assert 'error' in response_data

def test_invalid_request_data(test_client):
    """
    異常系: 必須フィールドが不足しているケース
    """
    # メールアドレスが欠けているデータ
    data = {
        'password': TEST_PASSWORD,
        'name': TEST_NAME
    }

    response = test_client.post(
        '/api/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )

    # レスポンスの検証
    assert response.status_code == HTTPStatus.BAD_REQUEST
    response_data = json.loads(response.data)
    assert 'error' in response_data

def test_invalid_email_format(test_client):
    """
    異常系: 不正なメールアドレス形式で登録を試みるケース
    """
    data = {
        'email': 'invalid-email',
        'password': TEST_PASSWORD,
        'name': TEST_NAME
    }

    response = test_client.post(
        '/api/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )

    # レスポンスの検証
    assert response.status_code == HTTPStatus.BAD_REQUEST
    response_data = json.loads(response.data)
    assert 'error' in response_data

def test_invalid_password_format(test_client):
    """
    異常系: パスワード要件を満たさないパスワードで登録を試みるケース
    """
    data = {
        'email': TEST_EMAIL,
        'password': 'weak',  # 要件を満たさない弱いパスワード
        'name': TEST_NAME
    }

    response = test_client.post(
        '/api/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )

    # レスポンスの検証
    assert response.status_code == HTTPStatus.BAD_REQUEST
    response_data = json.loads(response.data)
    assert 'error' in response_data 