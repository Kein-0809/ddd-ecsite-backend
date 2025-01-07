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
            ValueError: 
                - トークンが指定されていない場合
                - トークンが無効な場合
        """
        # ログアウト時はトークンが無効でもエラーにしない
        
        # トークンの存在チェック
        if not request.token:
            raise ValueError("トークンが指定されていません")
            
        # トークンの無効化
        self.auth_service.invalidate_token(request.token) 