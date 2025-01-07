"""
スーパー管理者登録ユースケース
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
from ...domain.exceptions import UserAlreadyExistsError, ValidationError

@dataclass
class SuperAdminRegistrationRequest:
    """スーパー管理者登録リクエスト"""
    email: str
    password: str
    name: str

class SuperAdminRegistrationUseCase:
    """スーパー管理者登録ユースケース"""

    def __init__(self, user_repository: UserRepository, email_service: EmailService):
        """
        初期化

        Args:
            user_repository: ユーザーリポジトリ
            email_service: メールサービス
        """
        self.user_repository = user_repository
        self.email_service = email_service

    def execute(self, request: SuperAdminRegistrationRequest) -> User:
        """
        スーパー管理者を登録

        Args:
            request: 登録リクエスト

        Returns:
            User: 作成されたスーパー管理者

        Raises:
            UserAlreadyExistsError: スーパー管理者が既に存在する場合
            ValidationError: 入力値が不正な場合
        """
        # スーパー管理者の存在チェック
        if self.user_repository.exists_super_admin():
            raise UserAlreadyExistsError("スーパー管理者は既に登録されています")

        # メールアドレスの重複チェック
        if self.user_repository.find_by_email(Email(request.email)):
            raise UserAlreadyExistsError("このメールアドレスは既に登録されています")

        # スーパー管理者の作成
        user = User(
            id=str(uuid.uuid4()),
            _email=Email(request.email),
            _password=Password.create(request.password),
            name=request.name,
            role=Role(RoleType.SUPER_ADMIN),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # スーパー管理者の保存
        saved_user = self.user_repository.save(user)

        # 確認メールの送信
        self.email_service.send_confirmation_email(saved_user)

        return saved_user 