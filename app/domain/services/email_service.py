from abc import ABC, abstractmethod
from ..entities.user import User

class EmailService(ABC):
    """メールサービスのインターフェース"""

    @abstractmethod
    def send_confirmation_email(self, user: User) -> None:
        """確認メールを送信"""
        pass