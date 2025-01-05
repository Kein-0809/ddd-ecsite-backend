import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """メールアドレスを表す値オブジェクト"""

    value: str

    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError("無効なメールアドレス形式です")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) 