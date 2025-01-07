"""
ユーザーログアウトユースケースの統合テスト
"""
import pytest
from datetime import datetime

from app import create_app, db
from app.application.usecases.user_logout import UserLogoutUseCase, LogoutRequest
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role, RoleType
from app.domain.value_objects.auth_token import AuthToken
from app.domain.services.auth_service import AuthService
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

# テストデータ
TEST_EMAIL = "test_integration@example.com"
TEST_PASSWORD = "Password123!"
TEST_NAME = "Test Integration User"
TEST_TOKEN = "test-token"

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

@pytest.fixture
def user_repository(init_database):
    """ユーザーリポジトリのインスタンスを作成"""
    return SQLAlchemyUserRepository(db.session)

@pytest.fixture
def auth_service(user_repository, app):
    """認証サービスのインスタンスを作成"""
    return AuthService(user_repository=user_repository)

@pytest.fixture
def user_logout_usecase(auth_service):
    """ユーザーログアウトユースケースのインスタンスを作成"""
    return UserLogoutUseCase(auth_service=auth_service)

@pytest.fixture
def test_user(user_repository):
    """テストユーザーを作成"""
    user = User(
        id="test-id",
        _email=Email(TEST_EMAIL),
        _password=Password.create(TEST_PASSWORD),
        name=TEST_NAME,
        role=Role(RoleType.USER),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return user_repository.save(user)

@pytest.fixture
def test_token(auth_service, test_user):
    """テストトークンを作成"""
    _, token = auth_service.authenticate(TEST_EMAIL, TEST_PASSWORD)
    return token

def test_successful_logout(user_logout_usecase, test_token):
    """
    正常系: ログアウトが成功するケース
    """
    # ユースケースの実行
    user_logout_usecase.execute(
        request=LogoutRequest(token=test_token)
    )

    # トークンが無効化されていることを確認
    assert not user_logout_usecase.auth_service.is_token_valid(test_token)

def test_logout_with_invalid_token(user_logout_usecase):
    """
    正常系: 無効なトークンでログアウトを試みるケース
    (ログアウト時はトークンが無効でもエラーにしない)
    """
    invalid_token = AuthToken("invalid-token")

    # ユースケースの実行（例外が発生しないことを確認）
    user_logout_usecase.execute(
        request=LogoutRequest(token=invalid_token)
    )

def test_multiple_logout_attempts(user_logout_usecase, test_token):
    """
    正常系: 同じトークンで複数回ログアウトを試みるケース
    """
    # 1回目のログアウト
    user_logout_usecase.execute(
        request=LogoutRequest(token=test_token)
    )

    # 2回目のログアウト（例外が発生しないことを確認）
    user_logout_usecase.execute(
        request=LogoutRequest(token=test_token)
    ) 