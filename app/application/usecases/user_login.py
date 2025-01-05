from dataclasses import dataclass
from ...domain.services.auth_service import AuthService
from ...domain.value_objects.auth_token import AuthToken
from ...domain.entities.user import User

@dataclass
class LoginRequest:
    """ログインリクエスト"""
    email: str
    password: str

@dataclass
class LoginResponse:
    """ログインレスポンス"""
    user: User
    token: AuthToken

class UserLoginUseCase:
    """ユーザーログインユースケース"""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    def execute(self, request: LoginRequest) -> LoginResponse:
        """
        ログインを実行
        
        Args:
            request: ログインリクエスト
            
        Returns:
            LoginResponse: ログイン結果
            
        Raises:
            ValueError: 認証に失敗した場合
        """
        user, token = self.auth_service.authenticate(
            email=request.email,
            password=request.password
        )
        
        return LoginResponse(user=user, token=token)