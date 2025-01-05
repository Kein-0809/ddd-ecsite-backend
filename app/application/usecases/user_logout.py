from dataclasses import dataclass
from ...domain.services.auth_service import AuthService

@dataclass
class LogoutRequest:
    """ログアウトリクエスト"""
    token: str

class UserLogoutUseCase:
    """ユーザーログアウトユースケース"""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    def execute(self, request: LogoutRequest) -> None:
        """
        ログアウトを実行
        
        Args:
            request: ログアウトリクエスト
            
        Raises:
            ValueError: トークンが無効な場合
        """
        self.auth_service.invalidate_token(request.token) 