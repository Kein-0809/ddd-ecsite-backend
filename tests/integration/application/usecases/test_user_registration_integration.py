"""
ユーザー登録ユースケースの統合テスト
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app, db
from app.application.usecases.user_registration import UserRegistrationUseCase, UserRegistrationRequest
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.role import Role, RoleType
from app.domain.exceptions import UserAlreadyExistsError, ValidationError
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.services.email_service import ConsoleEmailService

# テストデータ
TEST_EMAIL = "test_integration@example.com"
TEST_PASSWORD = "Password123!"
TEST_NAME = "Test Integration User"

@pytest.fixture
def app():
    """テスト用のFlaskアプリケーションを作成"""
    # テスト用のFlaskアプリケーションを設定
    app = create_app({
        'TESTING': True,  # テストモードを有効にする
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # メモリ内SQLiteデータベースを使用
        'SQLALCHEMY_TRACK_MODIFICATIONS': False  # SQLAlchemyの変更追跡を無効にする
    })
    return app  # 作成したアプリケーションを返す

@pytest.fixture
def test_client(app):
    """テスト用のクライアントを作成"""
    # Flaskアプリケーションのテストクライアントを作成
    return app.test_client()  # テストクライアントを返す

@pytest.fixture
def init_database(app):
    """テスト用のデータベースを初期化"""
    with app.app_context():  # アプリケーションのコンテキストを作成
        db.create_all()  # データベースのテーブルを作成
        yield db  # テスト中に使用するデータベースオブジェクトを返す
        db.session.remove()  # テスト後にセッションを削除
        db.drop_all()  # テスト後にデータベースのテーブルを削除

@pytest.fixture
def user_repository(init_database):
    """ユーザーリポジトリのインスタンスを作成"""
    # SQLAlchemyを使用してデータベースセッションを持つユーザーリポジトリのインスタンスを作成
    return SQLAlchemyUserRepository(db.session)  # ユーザーリポジトリを返す

@pytest.fixture
def email_service():
    """メールサービスのインスタンスを作成"""
    # コンソールメールサービスのインスタンスを作成
    return ConsoleEmailService()  # メールサービスを返す

@pytest.fixture
def user_registration_usecase(user_repository, email_service):
    """ユーザー登録ユースケースのインスタンスを作成 (Application層)"""
    # ユーザーリポジトリとメールサービスを使用してユーザー登録ユースケースのインスタンスを作成
    return UserRegistrationUseCase(
        user_repository=user_repository,  # ユーザーリポジトリを設定
        email_service=email_service  # メールサービスを設定
    )

def test_successful_user_registration(user_registration_usecase, init_database):
    """
    正常系: ユーザー登録が成功するケース
    """
    # ユースケースの実行
    result = user_registration_usecase.execute(
        UserRegistrationRequest(
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
    assert result.role.role_type == RoleType.USER
    assert result.is_active is True

    # データベースに保存されたことを確認
    saved_user = user_registration_usecase.user_repository.find_by_email(Email(TEST_EMAIL))
    assert saved_user is not None
    assert saved_user.email.value == TEST_EMAIL
    assert saved_user.name == TEST_NAME
    assert saved_user.role.role_type == RoleType.USER

def test_duplicate_email_registration(user_registration_usecase, init_database):
    """
    異常系: 既存のメールアドレスで登録を試みるケース
    """
    # 最初のユーザーを登録
    user_registration_usecase.execute(
        UserRegistrationRequest(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            name=TEST_NAME
        )
    )

    # 同じメールアドレスで2回目の登録を試みる
    with pytest.raises(UserAlreadyExistsError):
        user_registration_usecase.execute(
            UserRegistrationRequest(
                email=TEST_EMAIL,
                password=TEST_PASSWORD,
                name="Another User"
            )
        )

def test_invalid_email_format(user_registration_usecase, init_database):
    """
    異常系: 不正なメールアドレス形式で登録を試みるケース
    """
    with pytest.raises(ValidationError):
        user_registration_usecase.execute(
            UserRegistrationRequest(
                email="invalid-email",
                password=TEST_PASSWORD,
                name=TEST_NAME
            )
        )

def test_invalid_password_format(user_registration_usecase, init_database):
    """
    異常系: パスワード要件を満たさないパスワードで登録を試みるケース
    """
    with pytest.raises(ValidationError):
        user_registration_usecase.execute(
            UserRegistrationRequest(
                email=TEST_EMAIL,
                password="weak",  # 要件を満たさない弱いパスワード
                name=TEST_NAME
            )
        ) 