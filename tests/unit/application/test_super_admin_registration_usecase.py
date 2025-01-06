import pytest
from datetime import datetime
from app.application.usecases.super_admin_registration import (
    SuperAdminRegistrationUseCase,
    SuperAdminRegistrationRequest
)
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role, RoleType
from app.domain.repositories.user_repository import UserRepository


@pytest.fixture
def mock_user_repository(mocker):
    """ユーザーリポジトリのモック"""
    return mocker.Mock(spec=UserRepository)


class TestSuperAdminRegistrationUseCase:
    """スーパー管理者登録ユースケースのテスト"""

    def test_successful_registration(self, mock_user_repository):
        """正常な登録のテスト"""
        # モックの設定
        mock_user_repository.exists_super_admin.return_value = False
        mock_user_repository.find_by_email.return_value = None
        
        # saveメソッドの戻り値を設定
        def mock_save(user):
            return user  # 保存されたユーザーをそのまま返す
        mock_user_repository.save.side_effect = mock_save
        
        # リクエストの作成
        request = SuperAdminRegistrationRequest(
            email="admin@example.com",
            password="Admin1234!",
            name="Super Admin"
        )
        
        # ユースケースの実行
        usecase = SuperAdminRegistrationUseCase(user_repository=mock_user_repository)
        user = usecase.execute(request)
        
        # 検証
        assert isinstance(user, User)
        assert user.email.value == "admin@example.com"
        assert user.name == "Super Admin"
        assert user.is_super_admin()
        assert user.is_active is True
        mock_user_repository.save.assert_called_once()

    def test_super_admin_already_exists(self, mock_user_repository):
        """スーパー管理者が既に存在する場合のテスト"""
        # モックの設定
        mock_user_repository.exists_super_admin.return_value = True
        
        # ユースケースの実行と検証
        usecase = SuperAdminRegistrationUseCase(user_repository=mock_user_repository)
        request = SuperAdminRegistrationRequest(
            email="admin@example.com",
            password="Admin1234!",
            name="Super Admin"
        )
        
        with pytest.raises(ValueError) as exc_info:
            usecase.execute(request)
        
        assert str(exc_info.value) == "スーパー管理者はすでに登録されています"
        mock_user_repository.save.assert_not_called()

    def test_duplicate_email(self, mock_user_repository):
        """メールアドレスが重複している場合のテスト"""
        # モックの設定
        mock_user_repository.exists_super_admin.return_value = False
        mock_user_repository.find_by_email.return_value = User(
            id="existing-id",
            _email=Email("admin@example.com"),
            _password=Password.create("ExistingPass123!"),
            name="Existing User",
            role=Role(RoleType.USER),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # ユースケースの実行と検証
        usecase = SuperAdminRegistrationUseCase(user_repository=mock_user_repository)
        request = SuperAdminRegistrationRequest(
            email="admin@example.com",
            password="Admin1234!",
            name="Super Admin"
        )
        
        with pytest.raises(ValueError) as exc_info:
            usecase.execute(request)
        
        assert str(exc_info.value) == "このメールアドレスは既に登録されています"
        mock_user_repository.save.assert_not_called() 