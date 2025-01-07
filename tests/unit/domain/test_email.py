import pytest
from app.domain.value_objects.email import Email
from app.domain.exceptions import ValidationError


class TestEmail:
    """メールアドレスのテストクラス"""

    def test_create_valid_email(self):
        """有効なメールアドレスの作成テスト"""
        email = Email("test@example.com")
        assert email.value == "test@example.com"

    def test_create_invalid_email(self):
        """無効なメールアドレスの作成テスト"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test@.com",
            "test@example.",
            "test@example..com",
            "test@example.c",
            "test@example.com.",
            ".test@example.com",
        ]

        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                Email(invalid_email)
            assert "無効なメールアドレスです" in str(exc_info.value)

    def test_email_equality(self):
        """メールアドレスの等価性テスト"""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        email3 = Email("other@example.com")

        assert email1 == email2
        assert email1 != email3
        assert hash(email1) == hash(email2)
        assert hash(email1) != hash(email3)

    def test_email_string_representation(self):
        """メールアドレスの文字列表現テスト"""
        email = Email("test@example.com")
        assert str(email) == "test@example.com" 