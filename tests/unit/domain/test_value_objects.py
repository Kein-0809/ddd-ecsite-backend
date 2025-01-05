import pytest
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password


class TestEmail:
    """Emailバリューオブジェクトのテスト"""

    def test_valid_email(self):
        """正常な電子メールアドレスでインスタンス化できる"""
        email = Email("test@example.com")
        assert email.value == "test@example.com"

    @pytest.mark.parametrize("invalid_email", [
        "",  # 空文字
        "invalid",  # @なし
        "@example.com",  # ローカルパートなし
        "test@",  # ドメインなし
        "test@example",  # TLDなし
    ])
    def test_invalid_email(self, invalid_email):
        """不正な電子メールアドレスでエラーが発生する"""
        with pytest.raises(ValueError):
            Email(invalid_email)


class TestPassword:
    """Passwordバリューオブジェクトのテスト"""

    def test_valid_password(self):
        """正常なパスワードでインスタンス化できる"""
        password = Password.create("Test1234!")
        assert isinstance(password, Password)
        assert password._hashed_password is not None

    def test_password_verification(self):
        """パスワード検証が正しく機能する"""
        password = Password.create("Test1234!")
        assert password.verify("Test1234!") is True
        assert password.verify("wrongpassword") is False

    @pytest.mark.parametrize("invalid_password", [
        "short",  # 8文字未満
        "lowercase123!",  # 大文字なし
        "UPPERCASE123!",  # 小文字なし
        "TestPassword!",  # 数字なし
        "TestPassword1",  # 特殊文字なし
    ])
    def test_invalid_password(self, invalid_password):
        """不正なパスワードでエラーが発生する"""
        with pytest.raises(ValueError):
            Password.create(invalid_password) 