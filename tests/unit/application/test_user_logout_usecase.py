import pytest
from app.application.usecases.user_logout import UserLogoutUseCase, LogoutRequest
from app.domain.services.auth_service import AuthService

@pytest.fixture
def mock_auth_service(mocker):
    """認証サービスのモック"""
    return mocker.Mock(spec=AuthService)

class TestUserLogoutUseCase:
    """ユーザーログアウトユースケースのテスト"""

    def test_successful_logout(self, mock_auth_service):
        """正常なログアウトのテスト"""
        # ユースケースの実行
        usecase = UserLogoutUseCase(auth_service=mock_auth_service)
        request = LogoutRequest(token="valid-token")
        usecase.execute(request)

        # 検証
        mock_auth_service.invalidate_token.assert_called_once_with("valid-token")

    def test_invalid_token(self, mock_auth_service):
        """無効なトークンでのログアウト失敗テスト"""
        # モックの設定
        mock_auth_service.invalidate_token.side_effect = ValueError("無効なトークンです")

        # ユースケースの実行と検証
        usecase = UserLogoutUseCase(auth_service=mock_auth_service)
        request = LogoutRequest(token="invalid-token")

        with pytest.raises(ValueError) as exc_info:
            usecase.execute(request)
        
        assert str(exc_info.value) == "無効なトークンです" 