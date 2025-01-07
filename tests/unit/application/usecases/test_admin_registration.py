"""
管理者登録ユースケースのテストモジュール
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.application.usecases.admin_registration import AdminRegistrationUseCase, AdminRegistrationRequest
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role, RoleType
from app.domain.exceptions import UserAlreadyExistsError, UnauthorizedError

# テストデータ
TEST_ADMIN_EMAIL = "admin@example.com"
TEST_ADMIN_PASSWORD = "Password123!"
TEST_ADMIN_NAME = "Test Admin"
TEST_SUPER_ADMIN_EMAIL = "super.admin@example.com"

@pytest.fixture
def mock_user_repository():
    """ユーザーリポジトリのモック"""
    return Mock()

@pytest.fixture
def admin_registration_usecase(mock_user_repository):
    """管理者登録ユースケースのフィクスチャ"""
    return AdminRegistrationUseCase(user_repository=mock_user_repository)

@pytest.fixture
def super_admin_user():
    """スーパー管理者ユーザーのフィクスチャ"""
    return User(
        id="super-admin-id",
        _email=Email(TEST_SUPER_ADMIN_EMAIL),
        _password=Password.create(TEST_ADMIN_PASSWORD),
        name="Super Admin",
        role=Role(RoleType.SUPER_ADMIN),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

def test_successful_admin_registration(admin_registration_usecase, mock_user_repository, super_admin_user):
    """
    正常系: 管理者登録が成功するケース
    """
    # モックの設定
    mock_user_repository.find_by_email.side_effect = [
        super_admin_user,  # スーパー管理者の検索結果
        None  # 新規管理者のメールアドレス検索結果
    ]

    # 保存されるユーザーオブジェクトを作成
    expected_admin = User(
        id="test-admin-id",
        _email=Email(TEST_ADMIN_EMAIL),
        _password=Password.create(TEST_ADMIN_PASSWORD),
        name=TEST_ADMIN_NAME,
        role=Role(RoleType.ADMIN),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_user_repository.save.return_value = expected_admin

    # ユースケースの実行
    result = admin_registration_usecase.execute(AdminRegistrationRequest(
        email=TEST_ADMIN_EMAIL,
        password=TEST_ADMIN_PASSWORD,
        name=TEST_ADMIN_NAME
    ))

    # 検証
    assert result is not None
    assert isinstance(result, User)
    assert result.email.value == TEST_ADMIN_EMAIL
    assert result.name == TEST_ADMIN_NAME
    assert result.role.role_type == RoleType.ADMIN
    assert result.is_active is True

    # リポジトリのメソッドが正しく呼び出されたことを確認
    assert mock_user_repository.find_by_email.call_count == 2
    mock_user_repository.save.assert_called_once()

def test_registration_with_invalid_super_admin(admin_registration_usecase, mock_user_repository):
    """
    異常系: 無効なスーパー管理者で管理者登録を試みるケース
    """
    # モックの設定
    mock_user_repository.find_by_email.return_value = None

    # 例外が発生することを確認
    with pytest.raises(UnauthorizedError):
        admin_registration_usecase.execute(AdminRegistrationRequest(
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD,
            name=TEST_ADMIN_NAME
        ))

    # リポジトリのメソッドが正しく呼び出されたことを確認
    mock_user_repository.find_by_email.assert_called_once_with(Email(TEST_SUPER_ADMIN_EMAIL))
    mock_user_repository.save.assert_not_called()

def test_registration_with_duplicate_email(admin_registration_usecase, mock_user_repository, super_admin_user):
    """
    異常系: 既存のメールアドレスで管理者登録を試みるケース
    """
    # モックの設定
    existing_admin = User(
        id="existing-admin-id",
        _email=Email(TEST_ADMIN_EMAIL),
        _password=Password.create(TEST_ADMIN_PASSWORD),
        name=TEST_ADMIN_NAME,
        role=Role(RoleType.ADMIN),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_user_repository.find_by_email.side_effect = [
        super_admin_user,  # スーパー管理者の検索結果
        existing_admin  # 新規管理者のメールアドレス検索結果
    ]

    # 例外が発生することを確認
    with pytest.raises(UserAlreadyExistsError):
        admin_registration_usecase.execute(AdminRegistrationRequest(
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD,
            name=TEST_ADMIN_NAME
        ))

    # リポジトリのメソッドが正しく呼び出されたことを確認
    assert mock_user_repository.find_by_email.call_count == 2
    mock_user_repository.save.assert_not_called() 