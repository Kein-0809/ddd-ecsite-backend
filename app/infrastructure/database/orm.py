from sqlalchemy.orm import registry, composite
from ...domain.entities.user import User
from ...domain.value_objects.email import Email
from ...domain.value_objects.password import Password
from .models import UserModel

# SQLAlchemyのレジストリを作成
mapper_registry = registry()

def start_mappers():
    """SQLAlchemyマッパーの設定"""
    
    def email_composite_factory(value):
        """Emailコンポジットファクトリ"""
        if value is None:
            return None
        if isinstance(value, Email):
            return value
        return Email(value)

    def password_composite_factory(value):
        """Passwordコンポジットファクトリ"""
        if value is None:
            return None
        if isinstance(value, Password):
            return value
        return Password(value)

    mapper_registry.map_imperatively(
        User,
        UserModel.__table__,
        properties={
            'id': UserModel.__table__.c.id,
            '_email': composite(
                email_composite_factory,
                UserModel.__table__.c.email,
                comparator_factory=lambda *args: UserModel.__table__.c.email.comparator,
            ),
            'name': UserModel.__table__.c.name,
            '_password': composite(
                password_composite_factory,
                UserModel.__table__.c.password_hash,
                comparator_factory=lambda *args: UserModel.__table__.c.password_hash.comparator,
            ),
            'is_active': UserModel.__table__.c.is_active,
            'is_admin': UserModel.__table__.c.is_admin,
            'created_at': UserModel.__table__.c.created_at,
            'updated_at': UserModel.__table__.c.updated_at,
        }
    ) 