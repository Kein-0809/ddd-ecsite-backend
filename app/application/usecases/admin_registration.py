"""
管理者登録ユースケース
"""
from dataclasses import dataclass
from datetime import datetime
import uuid

from ...domain.entities.user import User
from ...domain.value_objects.email import Email
from ...domain.value_objects.password import Password
from ...domain.value_objects.role import Role, RoleType
from ...domain.repositories.user_repository import UserRepository
from ...domain.exceptions import UserAlreadyExistsError, UnauthorizedError

@dataclass
class AdminRegistrationRequest:
    """管理者登録リクエスト"""
    email: str
    password: str
    name: str

class AdminRegistrationUseCase:
    """管理者登録ユースケース"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(self, request: AdminRegistrationRequest) -> User:
        """
        管理者を登録
        
        Args:
            request: 登録リクエスト
            
        Returns:
            User: 作成された管理者
            
        Raises:
            UnauthorizedError: スーパー管理者による承認が得られない場合
            UserAlreadyExistsError: メールアドレスが既に使用されている場合
        """
        # スーパー管理者の検証
        super_admin = self.user_repository.find_by_email(Email("super.admin@example.com"))
        if not super_admin or super_admin.role.role_type != RoleType.SUPER_ADMIN:
            raise UnauthorizedError("スーパー管理者による承認が必要です")

        # メールアドレスの重複チェック
        if self.user_repository.find_by_email(Email(request.email)):
            raise UserAlreadyExistsError("このメールアドレスは既に登録されています")

        # 管理者の作成
        admin = User(
            id=str(uuid.uuid4()),
            _email=Email(request.email),
            _password=Password.create(request.password),
            name=request.name,
            role=Role(RoleType.ADMIN),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 保存
        return self.user_repository.save(admin) 