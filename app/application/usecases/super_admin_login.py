"""
スーパー管理者ログインユースケース
"""
from dataclasses import dataclass
from ...domain.services.auth_service import AuthService
from ...domain.value_objects.auth_token import AuthToken
from ...domain.entities.user import User
from ...domain.value_objects.role import RoleType
from ...domain.exceptions import AuthenticationError, UnauthorizedError

@dataclass
class SuperAdminLoginRequest:
    """スーパー管理者ログインリクエスト"""
    email: str
    password: str

@dataclass
class SuperAdminLoginResponse:
    """スーパー管理者ログインレスポンス"""
    user: User
    token: AuthToken

class SuperAdminLoginUseCase:
    """スーパー管理者ログインユースケース"""
    
    def __init__(self, auth_service: AuthService):
        """
        初期化

        Args:
            auth_service: 認証サービス
        """
        self.auth_service = auth_service
    
    def execute(self, request: SuperAdminLoginRequest) -> SuperAdminLoginResponse:
        """
        スーパー管理者ログインを実行
        
        Args:
            request: ログインリクエスト
            
        Returns:
            SuperAdminLoginResponse: ログイン結果
            
        Raises:
            AuthenticationError: 認証に失敗した場合
            UnauthorizedError: スーパー管理者権限がない場合
        """
        try:
            # 認証を実行
            user, token = self.auth_service.authenticate(
                email=request.email,
                password=request.password
            )
            
            # スーパー管理者権限の確認
            if user.role.role_type != RoleType.SUPER_ADMIN:
                raise UnauthorizedError("スーパー管理者権限がありません")
            
            return SuperAdminLoginResponse(
                user=user,
                token=token
            )
            
        except ValueError as e:
            raise AuthenticationError(str(e)) 