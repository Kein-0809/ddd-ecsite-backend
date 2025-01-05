import re
from dataclasses import dataclass
from werkzeug.security import generate_password_hash, check_password_hash


@dataclass
class Password:
    """パスワードを表す値オブジェクト"""

    _hashed_password: str = None

    @classmethod
    def create(cls, plain_password: str) -> 'Password':
        """平文のパスワードからインスタンスを生成"""
        if not cls._is_valid_password(plain_password):
            raise ValueError(
                "パスワードは8文字以上で、大文字、小文字、数字、特殊文字を含む必要があります"
            )
        return cls(generate_password_hash(plain_password))

    def verify(self, plain_password: str) -> bool:
        """パスワードを検証"""
        return check_password_hash(self._hashed_password, plain_password)

    @staticmethod
    def _is_valid_password(password: str) -> bool:
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):  # 大文字
            return False
        if not re.search(r'[a-z]', password):  # 小文字
            return False
        if not re.search(r'\d', password):     # 数字
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # 特殊文字
            return False
        return True 