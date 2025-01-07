"""
パスワードの値オブジェクト
"""
from dataclasses import dataclass
import re
from werkzeug.security import generate_password_hash, check_password_hash
from app.domain.exceptions import ValidationError


@dataclass(frozen=True)
class Password:
    """パスワードの値オブジェクト"""
    _hashed_password: str

    @classmethod
    def create(cls, plain_password: str) -> 'Password':
        """平文のパスワードからインスタンスを生成する"""
        if not cls._is_valid_password(plain_password):
            raise ValidationError(
                "パスワードは8文字以上で、大文字、小文字、数字、特殊文字を含む必要があります"
            )
        hashed_password = generate_password_hash(plain_password)
        return cls(_hashed_password=hashed_password)

    def verify(self, plain_password: str) -> bool:
        """パスワードを検証する"""
        return check_password_hash(self._hashed_password, plain_password)

    @staticmethod
    def _is_valid_password(password: str) -> bool:
        """パスワードの要件を検証する"""
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

    def __eq__(self, other: object) -> bool:
        """等価性の比較"""
        if not isinstance(other, Password):
            return NotImplemented
        # パスワードの比較は、ハッシュ値で判断する
        return self._hashed_password == other._hashed_password

    def __hash__(self) -> int:
        """ハッシュ値の計算"""
        return hash(self._hashed_password) 