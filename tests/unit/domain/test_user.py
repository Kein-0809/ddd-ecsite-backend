import pytest
from datetime import datetime
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role, RoleType
from app.domain.exceptions import ValidationError


class TestUser:
    """ユーザーのテストクラス"""

    def test_create_user_with_valid_data(self):
        """有効なデータでのユーザー作成テスト"""
        user = User(
            id="test-id",
            _email=Email("test@example.com"),
            _password=Password.create("Password123!"),
            name="Test User",
            role=Role(RoleType.USER),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        assert user.id == "test-id"
        assert user.email.value == "test@example.com"
        assert user.name == "Test User"
        assert user.role.role_type == RoleType.USER
        assert user.is_active is True
        assert user.verify_password("Password123!")

    def test_create_user_with_invalid_email(self):
        """無効なメールアドレスでのユーザー作成テスト"""
        with pytest.raises(ValidationError) as exc_info:
            User(
                id="test-id",
                _email=Email("invalid-email"),
                _password=Password.create("Password123!"),
                name="Test User",
                role=Role(RoleType.USER),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        assert "無効なメールアドレスです" in str(exc_info.value)

    def test_create_user_with_invalid_password(self):
        """無効なパスワードでのユーザー作成テスト"""
        with pytest.raises(ValidationError) as exc_info:
            User(
                id="test-id",
                _email=Email("test@example.com"),
                _password=Password.create("weak"),
                name="Test User",
                role=Role(RoleType.USER),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        assert "パスワードは8文字以上で、大文字、小文字、数字、特殊文字を含む必要があります" in str(exc_info.value)

    def test_verify_password(self):
        """パスワード検証テスト"""
        user = User(
            id="test-id",
            _email=Email("test@example.com"),
            _password=Password.create("Password123!"),
            name="Test User",
            role=Role(RoleType.USER),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        assert user.verify_password("Password123!") is True
        assert user.verify_password("WrongPassword123!") is False

    def test_update_profile(self):
        """プロフィール更新テスト"""
        user = User(
            id="test-id",
            _email=Email("test@example.com"),
            _password=Password.create("Password123!"),
            name="Test User",
            role=Role(RoleType.USER),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        new_email = Email("new@example.com")
        new_name = "New Name"
        
        user.update_profile(name=new_name, email=new_email)
        assert user.name == new_name
        assert user.email == new_email

    def test_activate_user(self):
        """ユーザーアクティベーションテスト"""
        user = User(
            id="test-id",
            _email=Email("test@example.com"),
            _password=Password.create("Password123!"),
            name="Test User",
            role=Role(RoleType.USER),
            is_active=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert user.is_active is False
        user.activate()
        assert user.is_active is True

    def test_user_equality(self):
        """ユーザーの等価性テスト"""
        user1 = User(
            id="test-id",
            _email=Email("test@example.com"),
            _password=Password.create("Password123!"),
            name="Test User",
            role=Role(RoleType.USER),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        user2 = User(
            id="test-id",
            _email=Email("test@example.com"),
            _password=Password.create("Password123!"),
            name="Test User",
            role=Role(RoleType.USER),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        user3 = User(
            id="other-id",
            _email=Email("other@example.com"),
            _password=Password.create("Password123!"),
            name="Other User",
            role=Role(RoleType.USER),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert user1 == user2
        assert user1 != user3
        assert hash(user1) == hash(user2)
        assert hash(user1) != hash(user3) 