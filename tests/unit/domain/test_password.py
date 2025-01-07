import pytest
from app.domain.value_objects.password import Password
from app.domain.exceptions import ValidationError


class TestPassword:
    """パスワードのテストクラス"""

    def test_create_valid_password(self):
        """有効なパスワードの作成テスト"""
        password = Password.create("Password123!")
        assert password.verify("Password123!")

    def test_create_invalid_password(self):
        """無効なパスワードの作成テスト"""
        invalid_passwords = [
            "short",  # 短すぎる
            "password",  # 小文字のみ
            "PASSWORD",  # 大文字のみ
            "12345678",  # 数字のみ
            "!@#$%^&*",  # 特殊文字のみ
            "Password",  # 大文字と小文字のみ
            "Password1",  # 特殊文字なし
            "Password!",  # 数字なし
            "12345678!",  # 文字なし
        ]

        for invalid_password in invalid_passwords:
            with pytest.raises(ValidationError) as exc_info:
                Password.create(invalid_password)
            assert "パスワードは8文字以上で、大文字、小文字、数字、特殊文字を含む必要があります" in str(exc_info.value)

    def test_password_verification(self):
        """パスワード検証テスト"""
        password = Password.create("Password123!")
        assert password.verify("Password123!") is True
        assert password.verify("WrongPassword123!") is False

    def test_password_comparison(self):
        """パスワード比較テスト"""
        password1 = Password.create("Password123!")
        password2 = Password.create("Password123!")
        password3 = Password.create("DifferentPass123!")

        # 同じパスワードでも異なるハッシュ値になるため、verify()メソッドで比較する
        assert password1.verify("Password123!")
        assert password2.verify("Password123!")
        assert not password3.verify("Password123!") 