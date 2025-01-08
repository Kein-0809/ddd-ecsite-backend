"""
依存性注入のためのコンテナ
"""
from flask import current_app
from .infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from .infrastructure.services.email_service import ConsoleEmailService

class Container:
    """依存性注入のためのコンテナ"""

    def __init__(self, db_session):
        """
        初期化

        Args:
            db_session: データベースセッション
        """
        self._db_session = db_session

    def user_repository(self):
        """ユーザーリポジトリを取得"""
        return SQLAlchemyUserRepository(self._db_session)

    def email_service(self):
        """メールサービスを取得"""
        return ConsoleEmailService() 