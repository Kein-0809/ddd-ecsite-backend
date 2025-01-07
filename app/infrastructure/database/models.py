"""
SQLAlchemyのデータベースモデル
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from ...domain.value_objects.role import RoleType
from . import db

class UserModel(db.Model):
    """ユーザーモデル"""
    
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(RoleType), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)