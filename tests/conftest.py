"""
テストの共通設定とフィクスチャを定義するモジュール
"""
import os
import sys
import pytest
from datetime import datetime

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role, RoleType


@pytest.fixture
def test_user():
    """テスト用ユーザーのフィクスチャ"""
    return User(
        id="test-id",
        _email=Email("test@example.com"),
        _password=Password.create("Password123!"),
        name="Test User",
        role=Role(RoleType.USER),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def test_admin():
    """テスト用管理者のフィクスチャ"""
    return User(
        id="admin-id",
        _email=Email("admin@example.com"),
        _password=Password.create("Password123!"),
        name="Test Admin",
        role=Role(RoleType.ADMIN),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def test_super_admin():
    """テスト用スーパー管理者のフィクスチャ"""
    return User(
        id="super-admin-id",
        _email=Email("super.admin@example.com"),
        _password=Password.create("Password123!"),
        name="Test Super Admin",
        role=Role(RoleType.SUPER_ADMIN),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def secret_key():
    """テスト用シークレットキーのフィクスチャ"""
    return "test-secret-key" 