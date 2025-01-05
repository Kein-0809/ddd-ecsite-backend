from datetime import datetime
import uuid
from ...domain.entities.user import User
from ...domain.value_objects.email import Email
from ...domain.value_objects.password import Password
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.email_service import EmailService


class UserRegistrationUseCase:
    """ユーザー登録ユースケース"""

    def __init__(
        self, user_repository: UserRepository, email_service: EmailService
    ):
        self.user_repository = user_repository
        self.email_service = email_service

    def execute(self, email: str, password: str, name: str) -> User:
        """
        ユーザー登録を実行

        Args:
            email (str): メールアドレス
            password (str): パスワード
            name (str): ユーザー名

        Returns:
            User: 作成されたユーザー

        Raises:
            ValueError: 入力値が不正な場合
            DuplicateEmailError: メールアドレスが既に登録されている場合
        """
        # 値オブジェクトの作成（バリデーション含む）
        email_vo = Email(email)
        password_vo = Password.create(password)

        # メールアドレスの重複チェック
        if self.user_repository.find_by_email(email):
            raise ValueError("このメールアドレスは既に登録されています")

        # ユーザーの作成
        user = User(
            id=str(uuid.uuid4()),
            email=email_vo,
            password=password_vo,
            name=name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # ユーザーの保存
        saved_user = self.user_repository.save(user)

        # 確認メールの送信
        self.email_service.send_confirmation_email(saved_user)

        return saved_user 