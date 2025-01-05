from typing import Optional
from sqlalchemy.orm import Session
from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.email import Email
from ...domain.value_objects.password import Password
from ..database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemyを使用したユーザーリポジトリの実装"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, user: User) -> User:
        """ユーザーを保存"""
        user_model = UserModel(
            id=user.id,
            email=user.email.value,
            name=user.name,
            password_hash=user.password._hashed_password,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.session.add(user_model)
        self.session.commit()
        return user

    def find_by_email(self, email: str) -> Optional[User]:
        """メールアドレスでユーザーを検索"""
        user_model = self.session.query(UserModel).filter_by(email=email).first()
        if not user_model:
            return None
        return self._to_entity(user_model)

    def _to_entity(self, model: UserModel) -> User:
        """データベースモデルをドメインエンティティに変換"""
        return User(
            id=model.id,
            email=Email(model.email),
            name=model.name,
            password=Password(model.password_hash),
            is_active=model.is_active,
            is_admin=model.is_admin,
            created_at=model.created_at,
            updated_at=model.updated_at,
        ) 