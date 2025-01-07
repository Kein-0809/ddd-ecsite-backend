import pytest
from app.domain.value_objects.role import Role, RoleType


class TestRole:
    """ロールのテストクラス"""

    def test_create_super_admin_role(self):
        """スーパー管理者ロールの作成テスト"""
        role = Role(RoleType.SUPER_ADMIN)
        assert role.role_type == RoleType.SUPER_ADMIN
        assert role.role_type.value == "super_admin"
        assert role.is_super_admin() is True
        assert role.is_admin() is True

    def test_create_admin_role(self):
        """管理者ロールの作成テスト"""
        role = Role(RoleType.ADMIN)
        assert role.role_type == RoleType.ADMIN
        assert role.role_type.value == "admin"
        assert role.is_super_admin() is False
        assert role.is_admin() is True

    def test_create_user_role(self):
        """一般ユーザーロールの作成テスト"""
        role = Role(RoleType.USER)
        assert role.role_type == RoleType.USER
        assert role.role_type.value == "user"
        assert role.is_super_admin() is False
        assert role.is_admin() is False

    def test_role_equality(self):
        """ロールの等価性テスト"""
        role1 = Role(RoleType.ADMIN)
        role2 = Role(RoleType.ADMIN)
        role3 = Role(RoleType.USER)

        assert role1 == role2
        assert role1 != role3
        assert hash(role1) == hash(role2)
        assert hash(role1) != hash(role3) 