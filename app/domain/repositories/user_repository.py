from abc import ABC, abstractmethod
from typing import Optional
from ..entities.user import User

class UserRepository(ABC):
    """ユーザーリポジトリのインターフェース"""

    @abstractmethod
    def save(self, user: User) -> User:
        """ユーザーを保存"""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """メールアドレスでユーザーを検索"""
        pass