"""
SQLAlchemyを使用したユーザーリポジトリの実装
"""
from typing import Optional
from sqlalchemy.orm import Session

from ...domain.repositories.user_repository import UserRepository
from ...domain.entities.user import User
from ...domain.value_objects.email import Email
from ...domain.value_objects.password import Password
from ...domain.value_objects.role import Role, RoleType
from ..database.models import UserModel

class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemyを使用したユーザーリポジトリの実装"""
    
    def __init__(self, session: Session):
        """
        初期化
        
        Args:
            session: SQLAlchemyのセッション
        """
        self.session = session
    
    def save(self, user: User) -> User:
        """
        ユーザーを保存
        
        Args:
            user: 保存するユーザー
            
        Returns:
            User: 保存されたユーザー
        """
        # 既存のユーザーを検索
        existing_user = self.session.query(UserModel).filter_by(id=user.id).first()

        if existing_user:
            # 既存のユーザーを更新
            existing_user.email = str(user.email)
            existing_user.password_hash = user._password._hashed_password
            existing_user.name = user.name
            existing_user.role = user.role.role_type
            existing_user.is_active = user.is_active
            existing_user.updated_at = user.updated_at
        else:
            # 新規ユーザーを作成
            user_model = UserModel(
                id=user.id,
                email=str(user.email),
                password_hash=user._password._hashed_password,
                name=user.name,
                role=user.role.role_type,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            self.session.add(user_model)

        self.session.commit()
        return self._to_entity(existing_user if existing_user else user_model)
    
    def find_by_email(self, email: Email) -> Optional[User]:
        """
        メールアドレスでユーザーを検索
        
        Args:
            email: 検索するメールアドレス
            
        Returns:
            Optional[User]: 見つかったユーザー、見つからない場合はNone
        """
        user_model = self.session.query(UserModel).filter_by(email=str(email)).first()
        if not user_model:
            return None
        return self._to_entity(user_model)
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        IDでユーザーを検索
        
        Args:
            user_id: 検索するユーザーID
            
        Returns:
            Optional[User]: 見つかったユーザー、見つからない場合はNone
        """
        user_model = self.session.query(UserModel).filter_by(id=user_id).first()
        if not user_model:
            return None
        return self._to_entity(user_model)
    
    def exists_super_admin(self) -> bool:
        """
        スーパー管理者が存在するかどうかを確認
        
        Returns:
            bool: スーパー管理者が存在する場合はTrue
        """
        return self.session.query(UserModel).filter_by(
            role=RoleType.SUPER_ADMIN
        ).first() is not None
    
    def _to_entity(self, model: UserModel) -> User:
        """
        データベースモデルをドメインエンティティに変換
        
        Args:
            model: データベースモデル
            
        Returns:
            User: ドメインエンティティ
        """
        return User(
            id=model.id,
            _email=Email(model.email),
            _password=Password(model.password_hash),
            name=model.name,
            role=Role(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        ) 