import pytest
import jwt
from datetime import datetime, timedelta
from app.domain.value_objects.auth_token import AuthToken


class TestAuthToken:
    """認証トークンの値オブジェクトのテスト"""

    def test_create_token(self):
        """トークンの生成テスト"""
        # トークンの生成
        user_id = "test-user-id"
        secret_key = "test-secret-key"
        token = AuthToken.create(user_id, secret_key)

        # トークンの検証
        assert isinstance(token, AuthToken)
        assert isinstance(token.token, str)

        # トークンのデコード
        decoded = jwt.decode(token.token, secret_key, algorithms=['HS256'])
        assert decoded['user_id'] == user_id
        assert 'exp' in decoded

    def test_decode_valid_token(self):
        """有効なトークンのデコードテスト"""
        user_id = "test-user-id"
        secret_key = "test-secret-key"
        token = AuthToken.create(user_id, secret_key)

        # デコード
        payload = AuthToken.decode(token.token, secret_key)
        assert payload is not None
        assert payload['user_id'] == user_id

    def test_decode_invalid_token(self):
        """無効なトークンのデコードテスト"""
        # 不正なトークン
        invalid_token = "invalid.token.string"
        payload = AuthToken.decode(invalid_token, "test-secret-key")
        assert payload is None

    def test_token_expiration(self):
        """トークンの有効期限テスト"""
        user_id = "test-user-id"
        secret_key = "test-secret-key"
        expires_in = 1  # 1秒後に有効期限切れ

        token = AuthToken.create(user_id, secret_key, expires_in)
        
        # 有効期限内
        payload = AuthToken.decode(token.token, secret_key)
        assert payload is not None
        assert payload['user_id'] == user_id

        # 有効期限切れを待つ
        import time
        time.sleep(2)

        # 有効期限切れ後
        payload = AuthToken.decode(token.token, secret_key)
        assert payload is None 