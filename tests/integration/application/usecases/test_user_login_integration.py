"""
ユーザーログインユースケースの統合テスト
"""
import pytest
from datetime import datetime

from app import create_app, db
from app.application.usecases.user_login import UserLoginUseCase, LoginRequest
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role, RoleType
from app.domain.value_objects.auth_token import AuthToken
from app.domain.exceptions import AuthenticationError
from app.domain.services.auth_service import AuthService
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

# テストデータ
TEST_EMAIL = "test_integration@example.com"
TEST_PASSWORD = "Password123!"
TEST_NAME = "Test Integration User"

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
def user_login_usecase(auth_service):
    """ユーザーログインユースケースのインスタンスを作成"""
    return UserLoginUseCase(auth_service=auth_service)

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

def test_successful_login(user_login_usecase, test_user):
    """
    正常系: ログインが成功するケース
    """
    # ユースケースの実行
    result = user_login_usecase.execute(
        request=LoginRequest(
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )
    )

    # 検証
    assert result is not None
    assert result.user is not None
    assert result.token is not None
    assert isinstance(result.token, AuthToken)
    assert result.user.email.value == TEST_EMAIL
    assert result.user.name == TEST_NAME
    assert result.user.role.role_type == RoleType.USER

def test_login_with_invalid_email(user_login_usecase):
    """
    異常系: 存在しないメールアドレスでログインを試みるケース
    """
    with pytest.raises(AuthenticationError):
        user_login_usecase.execute(
            request=LoginRequest(
                email="nonexistent@example.com",
                password=TEST_PASSWORD
            )
        )

def test_login_with_invalid_password(user_login_usecase, test_user):
    """
    異常系: 不正なパスワードでログインを試みるケース
    """
    with pytest.raises(AuthenticationError):
        user_login_usecase.execute(
            request=LoginRequest(
                email=TEST_EMAIL,
                password="WrongPassword123!"
            )
        )

def test_login_with_inactive_user(user_login_usecase, user_repository, test_user):
    """
    異常系: 無効化されたユーザーでログインを試みるケース
    """
    # ユーザーを無効化
    test_user.is_active = False
    user_repository.save(test_user)

    with pytest.raises(AuthenticationError):
        user_login_usecase.execute(
            request=LoginRequest(
                email=TEST_EMAIL,
                password=TEST_PASSWORD
            )
        ) 