"""
ユーザーログインユースケースのテストモジュール
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.application.usecases.user_login import UserLoginUseCase, LoginRequest, LoginResponse
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role, RoleType
from app.domain.value_objects.auth_token import AuthToken
from app.domain.exceptions import AuthenticationError

# テストデータ
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Password123!"
TEST_NAME = "Test User"
TEST_TOKEN = "dummy-token"

@pytest.fixture
def mock_user_repository():
    """ユーザーリポジトリのモック"""
    return Mock()

@pytest.fixture
def mock_auth_service():
    """認証サービスのモック"""
    return Mock()

@pytest.fixture
def user_login_usecase(mock_auth_service):
    """ユーザーログインユースケースのフィクスチャ"""
    return UserLoginUseCase(auth_service=mock_auth_service)

@pytest.fixture
def test_user():
    """テストユーザーのフィクスチャ"""
    return User(
        id="test-id",
        _email=Email(TEST_EMAIL),
        _password=Password.create(TEST_PASSWORD),
        name=TEST_NAME,
        role=Role(RoleType.USER),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

def test_successful_login(user_login_usecase, mock_auth_service, test_user):
    """
    正常系: ログインが成功するケース
    """
    # モックの設定
    auth_token = AuthToken(TEST_TOKEN)
    mock_auth_service.authenticate.return_value = (test_user, auth_token)

    # ユースケースの実行
    result = user_login_usecase.execute(
        request=LoginRequest(
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )
    )

    # 検証
    assert result is not None
    assert isinstance(result, LoginResponse)
    assert result.user == test_user
    assert result.token == auth_token
    assert result.role == RoleType.USER.value

    # 認証サービスのメソッドが正しく呼び出されたことを確認
    mock_auth_service.authenticate.assert_called_once_with(
        email=TEST_EMAIL,
        password=TEST_PASSWORD
    )

def test_login_with_invalid_credentials(user_login_usecase, mock_auth_service):
    """
    異常系: 不正な認証情報でログインを試みるケース
    """
    # モックの設定
    mock_auth_service.authenticate.side_effect = ValueError("メールアドレスまたはパスワードが正しくありません")

    # 例外が発生することを確認
    with pytest.raises(AuthenticationError):
        user_login_usecase.execute(
            request=LoginRequest(
                email=TEST_EMAIL,
                password=TEST_PASSWORD
            )
        )

    # 認証サービスのメソッドが正しく呼び出されたことを確認
    mock_auth_service.authenticate.assert_called_once_with(
        email=TEST_EMAIL,
        password=TEST_PASSWORD
    ) 