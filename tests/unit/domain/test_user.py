import pytest
from datetime import datetime
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password


@pytest.fixture
def valid_user():
    """有効なユーザーエンティティを作成"""
    return User(
        id="test-id",
        email=Email("test@example.com"),
        name="Test User",
        password=Password.create("Test1234!"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestUser:
    """ユーザーエンティティのテスト"""

    def test_create_user(self, valid_user):
        """ユーザーエンティティが正しく作成される"""
        assert valid_user.id == "test-id"
        assert valid_user.email.value == "test@example.com"
        assert valid_user.name == "Test User"
        assert valid_user.is_active is False
        assert valid_user.is_admin is False

    def test_activate_user(self, valid_user):
        """ユーザーを有効化できる"""
        valid_user.activate()
        assert valid_user.is_active is True

    def test_update_profile(self, valid_user):
        """プロフィールを更新できる"""
        new_email = Email("new@example.com")
        new_name = "New Name"
        
        valid_user.update_profile(name=new_name, email=new_email)
        
        assert valid_user.email.value == "new@example.com"
        assert valid_user.name == "New Name" 