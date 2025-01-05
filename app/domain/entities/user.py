from dataclasses import dataclass
from datetime import datetime
from ..value_objects.email import Email
from ..value_objects.password import Password


@dataclass
class User:
    """ユーザーエンティティ"""

    id: str
    name: str
    _email: Email
    _password: Password
    is_active: bool = False
    is_admin: bool = False
    created_at: datetime = None
    updated_at: datetime = None

    @property
    def email(self) -> Email:
        return self._email

    @property
    def password(self) -> Password:
        return self._password

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