"""
スーパー管理者登録ユースケースの統合テスト
"""
import pytest
from datetime import datetime

from app import create_app, db
from app.application.usecases.super_admin_registration import SuperAdminRegistrationUseCase, SuperAdminRegistrationRequest
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role, RoleType
from app.domain.exceptions import ValidationError, UserAlreadyExistsError
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.services.email_service import ConsoleEmailService

# テストデータ
TEST_EMAIL = "super.admin@example.com"
TEST_PASSWORD = "SuperAdmin123!"
TEST_NAME = "Test Super Admin"

@pytest.fixture
def app():
    """テスト用のFlaskアプリケーションを作成"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key'
    })
    return app

@pytest.fixture
def test_client(app):
    """テスト用のクライアントを作成"""
    return app.test_client()

@pytest.fixture(autouse=True)
def init_database(app):
    """テスト用のデータベースを初期化"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def user_repository(init_database):
    """ユーザーリポジトリのインスタンスを作成"""
    return SQLAlchemyUserRepository(db.session)

@pytest.fixture
def email_service():
    """メールサービスのインスタンスを作成"""
    return ConsoleEmailService()

@pytest.fixture
def super_admin_registration_usecase(user_repository, email_service):
    """スーパー管理者登録ユースケースのインスタンスを作成"""
    return SuperAdminRegistrationUseCase(
        user_repository=user_repository,
        email_service=email_service
    )

def test_successful_super_admin_registration(super_admin_registration_usecase):
    """
    正常系: スーパー管理者登録が成功するケース
    """
    # ユースケースの実行
    result = super_admin_registration_usecase.execute(
        request=SuperAdminRegistrationRequest(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            name=TEST_NAME
        )
    )

    # 検証
    assert result is not None
    assert isinstance(result, User)
    assert result.email.value == TEST_EMAIL
    assert result.name == TEST_NAME
    assert result.role.role_type == RoleType.SUPER_ADMIN
    assert result.is_active is True

    # データベースに保存されたことを確認
    saved_user = super_admin_registration_usecase.user_repository.find_by_email(Email(TEST_EMAIL))
    assert saved_user is not None
    assert saved_user.email.value == TEST_EMAIL
    assert saved_user.name == TEST_NAME
    assert saved_user.role.role_type == RoleType.SUPER_ADMIN

def test_duplicate_super_admin_registration(super_admin_registration_usecase):
    """
    異常系: 既にスーパー管理者が存在する場合の登録試行
    """
    # 最初のスーパー管理者を登録
    super_admin_registration_usecase.execute(
        request=SuperAdminRegistrationRequest(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            name=TEST_NAME
        )
    )

    # 2人目のスーパー管理者の登録を試みる
    with pytest.raises(UserAlreadyExistsError):
        super_admin_registration_usecase.execute(
            request=SuperAdminRegistrationRequest(
                email="another.super.admin@example.com",
                password=TEST_PASSWORD,
                name="Another Super Admin"
            )
        )

def test_invalid_email_format(super_admin_registration_usecase):
    """
    異常系: 不正なメールアドレス形式で登録を試みるケース
    """
    with pytest.raises(ValidationError):
        super_admin_registration_usecase.execute(
            request=SuperAdminRegistrationRequest(
                email="invalid-email",
                password=TEST_PASSWORD,
                name=TEST_NAME
            )
        )

def test_invalid_password_format(super_admin_registration_usecase):
    """
    異常系: パスワード要件を満たさないパスワードで登録を試みるケース
    """
    with pytest.raises(ValidationError):
        super_admin_registration_usecase.execute(
            request=SuperAdminRegistrationRequest(
                email=TEST_EMAIL,
                password="weak",  # 要件を満たさない弱いパスワード
                name=TEST_NAME
            )
        ) 