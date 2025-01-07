"""
アプリケーションのルートパッケージ
"""

from flask import Flask
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from .domain.services.auth_service import AuthService
from .infrastructure.database import db

# グローバルなインスタンスを作成
migrate = Migrate()
csrf = CSRFProtect()

def create_app(test_config=None):
    """アプリケーションファクトリ"""
    app = Flask(__name__)

    # デフォルト設定
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///app.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is not None:
        # テスト用の設定で上書き
        app.config.update(test_config)

    # 拡張機能の初期化
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # 認証サービスの初期化
    app.auth_service = AuthService(user_repository=db.session)

    with app.app_context():
        # テストモードの場合はルートの登録をスキップ
        if not app.config.get('TESTING', False):
            # Blueprintの登録
            from .api.routes import user_routes, auth_routes
            app.register_blueprint(user_routes.user_routes)
            app.register_blueprint(auth_routes.auth_routes)

        # データベースの初期化
        db.create_all()

    return app