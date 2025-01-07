"""
メールサービスの実装
"""
from ...domain.services.email_service import EmailService
from ...domain.entities.user import User

class ConsoleEmailService(EmailService):
    """
    テスト用のメールサービス実装
    メールの代わりにコンソールに出力する
    """
    
    def send_confirmation_email(self, user: User) -> None:
        """
        確認メールの送信（コンソールに出力）
        
        Args:
            user: 確認メールを送信するユーザー
        """
        print(f"""
        ===== 確認メール =====
        To: {user.email.value}
        Subject: アカウント登録確認
        
        {user.name} 様
        
        アカウントの登録ありがとうございます。
        以下のリンクをクリックして、アカウントを有効化してください。
        
        http://example.com/activate/{user.id}
        
        ==================
        """) 