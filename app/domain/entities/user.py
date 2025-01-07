"""
ユーザーエンティティ
"""
from dataclasses import dataclass
from datetime import datetime
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role


@dataclass
class User:
    """ユーザーエンティティ"""
    id: str
    name: str
    _email: Email
    _password: Password
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @property
    def email(self) -> Email:
        """メールアドレスを取得する"""
        return self._email

    def verify_password(self, plain_password: str) -> bool:
        """パスワードを検証する"""
        return self._password.verify(plain_password)

    def update_profile(self, name: str = None, email: Email = None) -> None:
        """プロフィールを更新する"""
        if name is not None:
            self.name = name
        if email is not None:
            self._email = email
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """アカウントを有効化する"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def is_super_admin(self) -> bool:
        """スーパー管理者かどうかを判定する"""
        return self.role.is_super_admin()

    def is_admin(self) -> bool:
        """管理者かどうかを判定する"""
        return self.role.is_admin()

    def __eq__(self, other: object) -> bool:
        """等価性の比較"""
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """ハッシュ値の計算"""
        return hash(self.id) 