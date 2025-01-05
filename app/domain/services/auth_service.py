from typing import Optional, Set
from flask import current_app
from ...domain.entities.user import User
from ...domain.value_objects.auth_token import AuthToken
from ...domain.repositories.user_repository import UserRepository

class AuthService():
    """認証サービスの実装"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self._invalidated_tokens: Set[str] = set()  # 無効化されたトークンを保持
    
    def authenticate(self, email: str, password: str) -> tuple[User, AuthToken]:
        """ユーザーを認証し、トークンを生成"""
        user = self.user_repository.find_by_email(email)
        if user is None or not user.password.verify(password):
            raise ValueError("メールアドレスまたはパスワードが正しくありません")
        
        if not user.is_active:
            raise ValueError("アカウントが有効化されていません")
            
        token = AuthToken.create(
            user_id=user.id,
            secret_key=current_app.config['SECRET_KEY']
        )
        return user, token
    
    def verify_token(self, token: str) -> User:
        """トークンを検証してユーザーを取得"""
        payload = AuthToken.decode(token, current_app.config['SECRET_KEY'])
        if payload is None:
            raise ValueError("無効なトークンです")
            
        user = self.user_repository.find_by_id(payload['user_id'])
        if user is None:
            raise ValueError("ユーザーが見つかりません")
            
        return user
    
    def invalidate_token(self, token: str) -> None:
        """トークンを無効化"""
        if not token:
            raise ValueError("トークンが指定されていません")
            
        # トークンの検証
        payload = AuthToken.decode(token, current_app.config['SECRET_KEY'])
        if payload is None:
            raise ValueError("無効なトークンです")
            
        # トークンを無効化リストに追加
        self._invalidated_tokens.add(token)
    
    def is_token_valid(self, token: str) -> bool:
        """トークンが有効かどうかを確認"""
        return token not in self._invalidated_tokens