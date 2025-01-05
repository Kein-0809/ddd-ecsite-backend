import pytest
from datetime import datetime
from app.application.usecases.user_login import UserLoginUseCase, LoginRequest
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.services.auth_service import AuthService
from app.domain.value_objects.auth_token import AuthToken


@pytest.fixture
def mock_auth_service(mocker):
    """認証サービスのモック"""
    return mocker.Mock(spec=AuthService)


@pytest.fixture
def valid_user():
    """有効なユーザーエンティティ"""
    return User(
        id="test-id",
        email=Email("test@example.com"),
        name="Test User",
        password=Password.create("Test1234!"),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def auth_token():
    """認証トークン"""
    return AuthToken.create("test-id", "test-secret-key")


class TestUserLoginUseCase:
    """ユーザーログインユースケースのテスト"""

    def test_successful_login(self, mock_auth_service, valid_user, auth_token):
        """正常なログインのテスト"""
        # モックの設定
        mock_auth_service.authenticate.return_value = (valid_user, auth_token)

        # ユースケースの実行
        usecase = UserLoginUseCase(auth_service=mock_auth_service)
        request = LoginRequest(
            email="test@example.com",
            password="Test1234!"
        )
        response = usecase.execute(request)

        # 検証
        assert response.user == valid_user
        assert response.token == auth_token
        mock_auth_service.authenticate.assert_called_once_with(
            email="test@example.com",
            password="Test1234!"
        )

    def test_invalid_credentials(self, mock_auth_service):
        """無効な認証情報でのログイン失敗テスト"""
        # モックの設定
        mock_auth_service.authenticate.side_effect = ValueError(
            "メールアドレスまたはパスワードが正しくありません"
        )

        # ユースケースの実行と検証
        usecase = UserLoginUseCase(auth_service=mock_auth_service)
        request = LoginRequest(
            email="wrong@example.com",
            password="WrongPass123!"
        )

        with pytest.raises(ValueError) as exc_info:
            usecase.execute(request)
        
        assert str(exc_info.value) == "メールアドレスまたはパスワードが正しくありません"

    def test_inactive_user(self, mock_auth_service):
        """非アクティブユーザーのログイン失敗テスト"""
        # モックの設定
        mock_auth_service.authenticate.side_effect = ValueError(
            "アカウントが有効化されていません"
        )

        # ユースケースの実行と検証
        usecase = UserLoginUseCase(auth_service=mock_auth_service)
        request = LoginRequest(
            email="inactive@example.com",
            password="Test1234!"
        )

        with pytest.raises(ValueError) as exc_info:
            usecase.execute(request)
        
        assert str(exc_info.value) == "アカウントが有効化されていません" 