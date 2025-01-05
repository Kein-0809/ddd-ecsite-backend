from dataclasses import dataclass
from datetime import datetime, timedelta
import jwt
from typing import Optional

@dataclass(frozen=True)
class AuthToken:
    """認証トークンを表す値オブジェクト"""
    
    token: str
    
    @classmethod
    def create(cls, user_id: str, secret_key: str, expires_in: int = 3600) -> 'AuthToken':
        """トークンを生成"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return cls(token=token)
    
    @staticmethod
    def decode(token: str, secret_key: str) -> Optional[dict]:
        """トークンをデコード"""
        try:
            return jwt.decode(token, secret_key, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return None