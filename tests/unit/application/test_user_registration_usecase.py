import pytest
from unittest.mock import Mock, patch
from app.application.usecases.user_registration import UserRegistrationUseCase
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password


class TestUserRegistrationUseCase:
    """ユーザー登録ユースケースのテスト"""

    @pytest.fixture
    def mock_repository(self):
        """モックリポジトリを作成"""
        return Mock()

    @pytest.fixture
    def mock_email_service(self):
        """モックメールサービスを作成"""
        return Mock()

    @pytest.fixture
    def usecase(self, mock_repository, mock_email_service):
        """ユースケースインスタンスを作成"""
        return UserRegistrationUseCase(
            # UserRegistrationUseCaseにあるuser_repositoryとemail_serviceをモックに置き換える
            # モックはUserRepositoryとEmailServiceのインターフェースを満たしている必要がある
            user_repository=mock_repository,
            email_service=mock_email_service
        )

    def test_successful_registration(self, usecase, mock_repository, mock_email_service):
        """正常なユーザー登録のテスト"""
        # モックの設定
        mock_repository.find_by_email.return_value = None
        mock_repository.save.return_value = Mock(spec=User)

        # ユースケースの実行
        user = usecase.execute(
            email="test@example.com",
            password="Test1234!",
            name="Test User"
        )

        # 検証
        assert isinstance(user, User)
        mock_repository.find_by_email.assert_called_once_with("test@example.com")
        mock_repository.save.assert_called_once()
        mock_email_service.send_confirmation_email.assert_called_once()

    def test_duplicate_email(self, usecase, mock_repository):
        """重複メールアドレスの場合のテスト"""
        # モックの設定
        mock_repository.find_by_email.return_value = Mock(spec=User)

        # 検証
        with pytest.raises(ValueError, match="このメールアドレスは既に登録されています"):
            usecase.execute(
                email="test@example.com",
                password="Test1234!",
                name="Test User"
            )

    @pytest.mark.parametrize("invalid_input,expected_error", [
        (
            {"email": "invalid", "password": "Test1234!", "name": "Test User"},
            "無効なメールアドレス形式です"
        ),
        (
            {"email": "test@example.com", "password": "weak", "name": "Test User"},
            "パスワードは8文字以上で、大文字、小文字、数字、特殊文字を含む必要があります"
        ),
    ])
    def test_invalid_input(self, usecase, invalid_input, expected_error):
        """不正な入力値の場合のテスト"""
        with pytest.raises(ValueError, match=expected_error):
            usecase.execute(**invalid_input) 