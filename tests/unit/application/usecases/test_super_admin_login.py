"""
スーパー管理者ログインユースケースのテストモジュール
"""
import pytest
from unittest.mock import Mock
from datetime import datetime

from app.application.usecases.super_admin_login import SuperAdminLoginUseCase, SuperAdminLoginRequest, SuperAdminLoginResponse
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role, RoleType
from app.domain.value_objects.auth_token import AuthToken
from app.domain.exceptions import AuthenticationError, UnauthorizedError

# テストデータ
TEST_EMAIL = "super.admin@example.com"
TEST_PASSWORD = "Password123!"
TEST_NAME = "Test Super Admin"
TEST_TOKEN = "dummy-token"

@pytest.fixture
def mock_auth_service():
    """認証サービスのモック"""
    return Mock()

@pytest.fixture
def super_admin_login_usecase(mock_auth_service):
    """スーパー管理者ログインユースケースのフィクスチャ"""
    return SuperAdminLoginUseCase(auth_service=mock_auth_service)

@pytest.fixture
def super_admin_user():
    """スーパー管理者ユーザーのフィクスチャ"""
    return User(
        id="super-admin-id",
        _email=Email(TEST_EMAIL),
        _password=Password.create(TEST_PASSWORD),
        name=TEST_NAME,
        role=Role(RoleType.SUPER_ADMIN),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

def test_successful_super_admin_login(super_admin_login_usecase, mock_auth_service, super_admin_user):
    """
    正常系: スーパー管理者ログインが成功するケース
    """
    # モックの設定
    auth_token = AuthToken(TEST_TOKEN)
    mock_auth_service.authenticate.return_value = (super_admin_user, auth_token)

    # ユースケースの実行
    result = super_admin_login_usecase.execute(
        request=SuperAdminLoginRequest(
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )
    )

    # 検証
    assert result is not None
    assert isinstance(result, SuperAdminLoginResponse)
    assert result.user == super_admin_user
    assert result.token == auth_token

    # 認証サービスのメソッドが正しく呼び出されたことを確認
    mock_auth_service.authenticate.assert_called_once_with(
        email=TEST_EMAIL,
        password=TEST_PASSWORD
    )

def test_login_with_invalid_credentials(super_admin_login_usecase, mock_auth_service):
    """
    異常系: 不正な認証情報でログインを試みるケース
    """
    # モックの設定
    mock_auth_service.authenticate.side_effect = ValueError("メールアドレスまたはパスワードが正しくありません")

    # 例外が発生することを確認
    with pytest.raises(AuthenticationError):
        super_admin_login_usecase.execute(
            request=SuperAdminLoginRequest(
                email=TEST_EMAIL,
                password=TEST_PASSWORD
            )
        )

    # 認証サービスのメソッドが正しく呼び出されたことを確認
    mock_auth_service.authenticate.assert_called_once_with(
        email=TEST_EMAIL,
        password=TEST_PASSWORD
    )

def test_login_with_non_super_admin_user(super_admin_login_usecase, mock_auth_service):
    """
    異常系: スーパー管理者以外のユーザーでログインを試みるケース
    """
    # モックの設定
    normal_admin = User(
        id="admin-id",
        _email=Email(TEST_EMAIL),
        _password=Password.create(TEST_PASSWORD),
        name=TEST_NAME,
        role=Role(RoleType.ADMIN),  # 通常の管理者ロール
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    auth_token = AuthToken(TEST_TOKEN)
    mock_auth_service.authenticate.return_value = (normal_admin, auth_token)

    # 例外が発生することを確認
    with pytest.raises(UnauthorizedError):
        super_admin_login_usecase.execute(
            request=SuperAdminLoginRequest(
                email=TEST_EMAIL,
                password=TEST_PASSWORD
            )
        )

    # 認証サービスのメソッドが正しく呼び出されたことを確認
    mock_auth_service.authenticate.assert_called_once_with(
        email=TEST_EMAIL,
        password=TEST_PASSWORD
    ) 