from dataclasses import dataclass
from datetime import datetime
import uuid
from ...domain.entities.user import User
from ...domain.value_objects.email import Email
from ...domain.value_objects.password import Password
from ...domain.value_objects.role import Role, RoleType
from ...domain.repositories.user_repository import UserRepository

@dataclass
class SuperAdminRegistrationRequest:
    """スーパー管理者登録リクエスト"""
    email: str
    password: str
    name: str

class SuperAdminRegistrationUseCase:
    """スーパー管理者登録ユースケース"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(self, request: SuperAdminRegistrationRequest) -> User:
        """
        スーパー管理者を登録
        
        Args:
            request: 登録リクエスト
            
        Returns:
            User: 作成されたスーパー管理者
            
        Raises:
            ValueError: 
                - 入力値が不正な場合
                - すでにスーパー管理者が存在する場合
        """
        # スーパー管理者の存在チェック
        if self.user_repository.exists_super_admin():
            raise ValueError("スーパー管理者はすでに登録されています")

        # メールアドレスの重複チェック
        if self.user_repository.find_by_email(request.email):
            raise ValueError("このメールアドレスは既に登録されています")

        # 値オブジェクトの作成
        email = Email(request.email)
        password = Password.create(request.password)
        role = Role(RoleType.SUPER_ADMIN)
        
        # スーパー管理者の作成
        now = datetime.utcnow()
        super_admin = User(
            id=str(uuid.uuid4()),
            _email=email,
            _password=password,
            name=request.name,
            role=role,
            is_active=True,  # スーパー管理者は作成時から有効
            created_at=now,
            updated_at=now
        )
        
        # 保存
        return self.user_repository.save(super_admin) 