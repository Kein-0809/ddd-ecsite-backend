import pytest
from flask import url_for
from http import HTTPStatus
from app.domain.entities.user import User
from app.domain.value_objects.email import Email


class TestUserRegistration:
    """ユーザー登録のインテグレーションテスト"""

    @pytest.fixture
    def valid_user_data(self):
        """有効なユーザーデータ"""
        return {
            "email": "test@example.com",
            "password": "Test1234!",
            "name": "Test User"
        }

    def test_successful_registration(self, client, valid_user_data):
        """正常なユーザー登録のテスト"""
        response = client.post(
            url_for("user.register"),
            json=valid_user_data
        )

        assert response.status_code == HTTPStatus.CREATED
        data = response.get_json()
        assert "message" in data
        assert "user" in data
        assert data["user"]["email"] == valid_user_data["email"]
        assert data["user"]["name"] == valid_user_data["name"]

    def test_duplicate_email_registration(self, client, valid_user_data, db_session):
        """重複メールアドレスでの登録のテスト"""
        # 1回目の登録
        client.post(url_for("user.register"), json=valid_user_data)

        # 2回目の登録（同じメールアドレス）
        response = client.post(
            url_for("user.register"),
            json=valid_user_data
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.get_json()
        assert "error" in data
        assert "既に登録されています" in data["error"]

    @pytest.mark.parametrize("invalid_data,expected_error", [
        (
            {
                "email": "invalid",
                "password": "Test1234!",
                "name": "Test User"
            },
            "無効なメールアドレス形式です"
        ),
        (
            {
                "email": "test@example.com",
                "password": "weak",
                "name": "Test User"
            },
            "パスワードは8文字以上で"
        ),
        (
            {
                "email": "test@example.com",
                "password": "Test1234!",
                "name": ""
            },
            "名前は必須です"
        ),
    ])
    def test_invalid_registration_data(
        self, client, invalid_data, expected_error
    ):
        """不正なデータでの登録のテスト"""
        response = client.post(
            url_for("user.register"),
            json=invalid_data
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.get_json()
        assert "error" in data
        assert expected_error in data["error"] 