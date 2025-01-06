from enum import Enum
from dataclasses import dataclass

class RoleType(Enum):
    """ユーザーロールの種類"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"

@dataclass(frozen=True)
class Role:
    """ユーザーロールを表す値オブジェクト"""
    role_type: RoleType

    def is_super_admin(self) -> bool:
        """スーパー管理者かどうかを判定"""
        return self.role_type == RoleType.SUPER_ADMIN

    def is_admin(self) -> bool:
        """管理者かどうかを判定"""
        return self.role_type in [RoleType.ADMIN, RoleType.SUPER_ADMIN] 