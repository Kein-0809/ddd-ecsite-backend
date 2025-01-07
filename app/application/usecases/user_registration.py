"""
ユーザー登録ユースケース
"""
from dataclasses import dataclass
from datetime import datetime
import uuid

from ...domain.entities.user import User
from ...domain.value_objects.email import Email
from ...domain.value_objects.password import Password
from ...domain.value_objects.role import Role, RoleType
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.email_service import EmailService
from ...domain.exceptions import UserAlreadyExistsError

@dataclass
class UserRegistrationRequest:
    """ユーザー登録リクエスト"""
    email: str
    password: str
    name: str

class UserRegistrationUseCase:
    """ユーザー登録ユースケース"""

    def __init__(self, user_repository: UserRepository, email_service: EmailService):
        """
        初期化

        Args:
            user_repository: ユーザーリポジトリ
            email_service: メールサービス
        """
        # インフラ層のレポジトリ
        self.user_repository = user_repository
        # インフラ層のサービス
        self.email_service = email_service

    def execute(self, request: UserRegistrationRequest) -> User:
        """
        ユーザーを登録

        Args:
            request: 登録リクエスト

        Returns:
            User: 作成されたユーザー

        Raises:
            UserAlreadyExistsError: メールアドレスが既に登録されている場合
        """
        # メールアドレスの重複チェック
        if self.user_repository.find_by_email(Email(request.email)):
            raise UserAlreadyExistsError("このメールアドレスは既に登録されています")

        # ユーザーの作成 (本来はFactoryの役割?)
        user = User(
            id=str(uuid.uuid4()),
            _email=Email(request.email),
            _password=Password.create(request.password),
            name=request.name,
            role=Role(RoleType.USER),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # ユーザーの保存
        saved_user = self.user_repository.save(user)

        # 確認メールの送信
        self.email_service.send_confirmation_email(saved_user)

        return saved_user 