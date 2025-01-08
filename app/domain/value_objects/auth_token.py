"""
認証トークンの値オブジェクト
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
import jwt
from app.domain.exceptions import ValidationError


@dataclass(frozen=True)
class AuthToken:
    """認証トークンの値オブジェクト"""
    value: str

    def __str__(self) -> str:
        """トークンの文字列表現を返す"""
        return self.value

    @classmethod
    def create(cls, user_id: str, secret_key: str, expiration: datetime = None) -> 'AuthToken':
        """トークンを生成する"""
        if expiration is None:
            expiration = datetime.utcnow() + timedelta(days=1)

        payload = {
            'user_id': user_id,
            'exp': expiration
        }

        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return cls(token)

    def decode(self, secret_key: str) -> str:
        """トークンをデコードしてユーザーIDを取得する"""
        try:
            payload = jwt.decode(self.value, secret_key, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            raise ValidationError("トークンの有効期限が切れています")
        except jwt.InvalidTokenError:
            raise ValidationError("無効なトークンです")