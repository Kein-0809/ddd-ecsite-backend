"""
メールアドレスの値オブジェクト
"""
from dataclasses import dataclass
import re
from app.domain.exceptions import ValidationError


@dataclass(frozen=True)
class Email:
    """メールアドレスの値オブジェクト"""
    value: str

    def __post_init__(self):
        """初期化後の検証"""
        if not self._is_valid_email(self.value):
            raise ValidationError("無効なメールアドレスです")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """メールアドレスの形式を検証する"""
        # より厳密なメールアドレスの検証パターン
        pattern = (
            r'^[a-zA-Z0-9._%+-]+'  # ローカル部
            r'@'                    # @記号
            r'[a-zA-Z0-9.-]+'      # ドメイン部
            r'\.'                   # ドット
            r'[a-zA-Z]{2,}$'       # トップレベルドメイン
        )
        if not re.match(pattern, email):
            return False
        # 追加のバリデーション
        if '..' in email:  # 連続したドットをチェック
            return False
        if email.startswith('.') or email.endswith('.'):  # 先頭または末尾のドットをチェック
            return False
        parts = email.split('@')
        if len(parts) != 2:  # @記号の数をチェック
            return False
        domain = parts[1]
        if domain.startswith('.') or domain.endswith('.'):  # ドメイン部の先頭または末尾のドットをチェック
            return False
        return True

    def __str__(self) -> str:
        """文字列表現を返す"""
        return self.value 