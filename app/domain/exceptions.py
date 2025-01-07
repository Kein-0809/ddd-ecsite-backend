"""
ドメイン層で使用する例外クラスを定義するモジュール
"""


class DomainException(Exception):
    """ドメイン層の基底例外クラス"""
    pass


class ValidationError(DomainException):
    """バリデーションエラー"""
    pass


class AuthenticationError(DomainException):
    """認証エラー"""
    pass


class AuthorizationError(DomainException):
    """認可エラー"""
    pass


class ResourceNotFoundError(DomainException):
    """リソース未検出エラー"""
    pass


class BusinessRuleError(DomainException):
    """ビジネスルール違反エラー"""
    pass 

class UserAlreadyExistsError(DomainException):
    """ユーザーが既に存在するエラー"""
    pass

class InvalidTokenError(DomainException):
    """無効なトークンエラー"""
    pass

class UnauthorizedError(DomainException):
    """未認証エラー"""
    pass
