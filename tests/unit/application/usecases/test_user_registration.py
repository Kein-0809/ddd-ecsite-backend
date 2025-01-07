"""
ユーザー登録ユースケースのテストモジュール
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.application.usecases.user_registration import UserRegistrationUseCase, UserRegistrationRequest
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role, RoleType
from app.domain.exceptions import UserAlreadyExistsError

# テストデータ
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Password123!"
TEST_NAME = "Test User"

@pytest.fixture
def mock_user_repository():
    """ユーザーリポジトリのモック"""
    return Mock()

@pytest.fixture
def mock_email_service():
    """メールサービスのモック"""
    return Mock()

@pytest.fixture
def user_registration_usecase(mock_user_repository, mock_email_service):
    """ユーザー登録ユースケースのフィクスチャ"""
    return UserRegistrationUseCase(user_repository=mock_user_repository, email_service=mock_email_service)

def test_successful_user_registration(user_registration_usecase, mock_user_repository, mock_email_service):
    """
    正常系: ユーザー登録が成功するケース
    """
    # モックの設定
    mock_user_repository.find_by_email.return_value = None
    
    # 保存されるユーザーオブジェクトを作成
    expected_user = User(
        id="test-id",
        _email=Email(TEST_EMAIL),
        _password=Password.create(TEST_PASSWORD),
        name=TEST_NAME,
        role=Role(RoleType.USER),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_user_repository.save.return_value = expected_user

    # ユースケースの実行
    result = user_registration_usecase.execute(
        UserRegistrationRequest(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            name=TEST_NAME
        )
    )

    # 検証
    assert result is not None
    assert isinstance(result, User)
    assert result.email.value == TEST_EMAIL
    assert result.name == TEST_NAME
    assert result.role == Role(RoleType.USER)
    assert result.is_active is True

    # リポジトリのメソッドが正しく呼び出されたことを確認
    mock_user_repository.find_by_email.assert_called_once_with(Email(TEST_EMAIL))
    mock_user_repository.save.assert_called_once()
    
    # メールサービスが呼び出されたことを確認
    mock_email_service.send_confirmation_email.assert_called_once_with(result)

def test_duplicate_email_registration(user_registration_usecase, mock_user_repository):
    """
    異常系: 既存のメールアドレスで登録を試みるケース
    """
    # モックの設定
    existing_user = User(
        id="existing-id",
        _email=Email(TEST_EMAIL),
        _password=Password.create(TEST_PASSWORD),
        name=TEST_NAME,
        role=Role(RoleType.USER),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    mock_user_repository.find_by_email.return_value = existing_user

    # 例外が発生することを確認
    with pytest.raises(UserAlreadyExistsError):
        user_registration_usecase.execute(
            UserRegistrationRequest(
                email=TEST_EMAIL,
                password=TEST_PASSWORD,
                name=TEST_NAME
            )
        )

    # リポジトリのメソッドが正しく呼び出されたことを確認
    mock_user_repository.find_by_email.assert_called_once_with(Email(TEST_EMAIL))
    mock_user_repository.save.assert_not_called() 