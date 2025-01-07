import pytest
from datetime import datetime, timedelta
from app.domain.value_objects.auth_token import AuthToken
from app.domain.exceptions import ValidationError


class TestAuthToken:
    """認証トークンのテストクラス"""

    def test_create_token(self, test_user, secret_key):
        """トークン生成のテスト"""
        token = AuthToken.create(test_user.id, secret_key)
        assert isinstance(token, AuthToken)
        assert token.value is not None
        assert len(token.value) > 0

    def test_decode_valid_token(self, test_user, secret_key):
        """有効なトークンのデコードテスト"""
        token = AuthToken.create(test_user.id, secret_key)
        user_id = token.decode(secret_key)
        assert user_id == test_user.id

    def test_decode_invalid_token(self, secret_key):
        """無効なトークンのデコードテスト"""
        invalid_token = AuthToken("invalid.token.string")
        with pytest.raises(ValidationError) as exc_info:
            invalid_token.decode(secret_key)
        assert "無効なトークンです" in str(exc_info.value)

    def test_token_expiration(self, test_user, secret_key):
        """トークンの有効期限テスト"""
        # 有効期限切れのトークンを生成
        expired_token = AuthToken.create(
            test_user.id,
            secret_key,
            expiration=datetime.utcnow() - timedelta(hours=1)
        )

        with pytest.raises(ValidationError) as exc_info:
            expired_token.decode(secret_key)
        assert "トークンの有効期限が切れています" in str(exc_info.value) 