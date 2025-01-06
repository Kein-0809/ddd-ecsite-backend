from dataclasses import dataclass
from datetime import datetime
from ..value_objects.email import Email
from ..value_objects.password import Password
from ..value_objects.role import Role, RoleType


@dataclass
class User:
    """ユーザーエンティティ"""

    id: str
    name: str
    _email: Email
    _password: Password
    role: Role
    is_active: bool = False
    created_at: datetime = None
    updated_at: datetime = None

    @property
    def email(self) -> Email:
        return self._email

    @property
    def password(self) -> Password:
        return self._password

    def is_super_admin(self) -> bool:
        """スーパー管理者かどうかを判定"""
        return self.role.is_super_admin()

    def is_admin(self) -> bool:
        """管理者かどうかを判定"""
        return self.role.is_admin()

    def activate(self) -> None:
        """ユーザーを有効化"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def update_profile(self, name: str = None, email: Email = None) -> None:
        """プロフィールを更新"""
        if name is not None:
            self.name = name
        if email is not None:
            self._email = email
        self.updated_at = datetime.utcnow() 