import pytest
from app.domain.value_objects.role import Role, RoleType


class TestRole:
    """ロール値オブジェクトのテスト"""

    def test_super_admin_role(self):
        """スーパー管理者ロールのテスト"""
        role = Role(RoleType.SUPER_ADMIN)
        assert role.is_super_admin() is True
        assert role.is_admin() is True

    def test_admin_role(self):
        """管理者ロールのテスト"""
        role = Role(RoleType.ADMIN)
        assert role.is_super_admin() is False
        assert role.is_admin() is True

    def test_user_role(self):
        """一般ユーザーロールのテスト"""
        role = Role(RoleType.USER)
        assert role.is_super_admin() is False
        assert role.is_admin() is False 