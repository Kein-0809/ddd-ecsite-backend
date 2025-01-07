"""
認証サービス
"""
import jwt
from flask import current_app
from datetime import datetime, timedelta
from typing import Optional, Set, Tuple

from ..entities.user import User
from ..value_objects.email import Email
from ..value_objects.auth_token import AuthToken
from ..repositories.user_repository import UserRepository
from ..exceptions import AuthenticationError, ValidationError

class AuthService:
    """認証サービス"""

    def __init__(self, user_repository: UserRepository):
        """
        初期化
        
        Args:
            user_repository: ユーザーリポジトリ
        """
        self.user_repository = user_repository
        self._invalidated_tokens: Set[str] = set()  # 無効化されたトークンを保持

    def authenticate(self, email: str, password: str) -> tuple[User, AuthToken]:
        """
        ユーザーを認証し、トークンを生成
        
        Args:
            email: メールアドレス
            password: パスワード
            
        Returns:
            tuple[User, AuthToken]: 認証されたユーザーとトークン
            
        Raises:
            AuthenticationError: 認証に失敗した場合
        """
        user = self.user_repository.find_by_email(Email(email))
        if user is None or not user._password.verify(password):
            raise AuthenticationError("メールアドレスまたはパスワードが間違っています")

        if not user.is_active:
            raise AuthenticationError("アカウントが無効化されています")

        # トークンの生成
        token = self._generate_token(user)
        return user, token

    def _generate_token(self, user: User) -> AuthToken:
        """
        JWTトークンを生成
        
        Args:
            user: ユーザー
            
        Returns:
            AuthToken: 生成されたトークン
        """
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return AuthToken(token)

    def invalidate_token(self, token: AuthToken) -> None:
        """
        トークンを無効化
        
        Args:
            token: 無効化するトークン
        """
        try:
            # トークンをデコードして有効性を確認
            AuthToken.decode(token, current_app.config['SECRET_KEY'])
            # 有効なトークンを無効化リストに追加
            self._invalidated_tokens.add(token.value)
        except ValidationError:
            # トークンが無効な場合は何もしない
            pass

    def is_token_valid(self, token: AuthToken) -> bool:
        """
        トークンが有効かどうかを確認
        
        Args:
            token: 確認するトークン
            
        Returns:
            bool: トークンが有効な場合はTrue
        """
        try:
            # トークンをデコードして有効性を確認
            AuthToken.decode(token, current_app.config['SECRET_KEY'])
            # 無効化リストに含まれていないことを確認
            return token.value not in self._invalidated_tokens
        except ValidationError:
            return False