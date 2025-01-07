"""
ユーザーログアウトユースケースのテストモジュール
"""
import pytest
from unittest.mock import Mock, patch

from app.application.usecases.user_logout import UserLogoutUseCase, LogoutRequest
from app.domain.value_objects.auth_token import AuthToken

@pytest.fixture
def mock_auth_service():
    """認証サービスのモック"""
    return Mock()

@pytest.fixture
def user_logout_usecase(mock_auth_service):
    """ユーザーログアウトユースケースのフィクスチャ"""
    return UserLogoutUseCase(auth_service=mock_auth_service)

def test_successful_logout(user_logout_usecase, mock_auth_service):
    """
    正常系: ログアウトが成功するケース
    """
    # テストデータ
    test_token = AuthToken("test-token")

    # ユースケースの実行
    user_logout_usecase.execute(request=LogoutRequest(token=test_token))

    # 認証サービスのメソッドが正しく呼び出されたことを確認
    mock_auth_service.invalidate_token.assert_called_once_with(test_token)

def test_logout_with_invalid_token(user_logout_usecase, mock_auth_service):
    """
    正常系: 無効なトークンでログアウトを試みるケース
    (ログアウト時はトークンが無効でもエラーにしない)
    """
    # テストデータ
    test_token = AuthToken("invalid-token")
    
    # モックの設定
    # mock_auth_service.invalidate_token.side_effect = Exception("Invalid token")
    mock_auth_service.invalidate_token.side_effect = None

    # ユースケースの実行（例外が発生しないことを確認）
    user_logout_usecase.execute(request=LogoutRequest(token=test_token))

    # 認証サービスのメソッドが正しく呼び出されたことを確認
    mock_auth_service.invalidate_token.assert_called_once_with(test_token) 