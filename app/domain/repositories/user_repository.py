from abc import ABC, abstractmethod
from typing import Optional
from ..entities.user import User
from ..value_objects.role import RoleType

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

    @abstractmethod
    def exists_super_admin(self) -> bool:
        """スーパー管理者が存在するかどうかを確認"""
        pass