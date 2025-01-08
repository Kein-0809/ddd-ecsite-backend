from flask import Blueprint, jsonify, request, current_app
from http import HTTPStatus
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta
from ...infrastructure.database.models import UserModel
from ... import db
from ...application.usecases.user_registration import UserRegistrationUseCase, UserRegistrationRequest
from ...application.usecases.user_logout import UserLogoutUseCase, LogoutRequest
from ...domain.services.auth_service import AuthService
from ...domain.value_objects.email import Email
from ...domain.exceptions import UserAlreadyExistsError, ValidationError

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """ユーザー登録エンドポイント"""
    try:
        data = request.get_json()
        
        # リクエストデータのバリデーション
        if not data or 'email' not in data or 'password' not in data or 'name' not in data:
            return jsonify({
                'error': '必須フィールドが不足しています'
            }), HTTPStatus.BAD_REQUEST

        # ユースケースの実行
        usecase = UserRegistrationUseCase(
            user_repository=current_app.container.user_repository(),
            email_service=current_app.container.email_service()
        )
        
        user = usecase.execute(
            UserRegistrationRequest(
                email=data['email'],
                password=data['password'],
                name=data['name']
            )
        )

        # トークンの生成
        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

        return jsonify({
            'message': 'ユーザー登録が完了しました',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email.value,
                'name': user.name,
                'role': user.role.role_type.value
            }
        }), HTTPStatus.CREATED
        
    except UserAlreadyExistsError as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.CONFLICT
    except ValidationError as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.BAD_REQUEST
    except Exception as e:
        current_app.logger.error(f"ユーザー登録中にエラーが発生しました: {str(e)}")
        return jsonify({
            'error': 'ユーザー登録に失敗しました'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/login', methods=['POST'])
def login():
    """ログインエンドポイント"""
    try:
        data = request.get_json()
        
        # リクエストデータのバリデーション
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'error': '必須フィールドが不足しています'
            }), HTTPStatus.BAD_REQUEST

        # ユーザーの検索
        user = current_app.container.user_repository().find_by_email(data['email'])
        if not user:
            return jsonify({
                'error': 'メールアドレスまたはパスワードが正しくありません'
            }), HTTPStatus.UNAUTHORIZED
        
        # パスワードの検証
        if not user.verify_password(data['password']):
            return jsonify({
                'error': 'メールアドレスまたはパスワードが正しくありません'
            }), HTTPStatus.UNAUTHORIZED

        if not user.is_active:
            return jsonify({
                'error': 'アカウントが有効化されていません'
            }), HTTPStatus.UNAUTHORIZED

        # トークンの生成
        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

        return jsonify({
            'message': 'ログインに成功しました',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email.value,
                'name': user.name
            }
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"ログイン中にエラーが発生しました: {str(e)}")
        return jsonify({
            'error': 'ログインに失敗しました'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/logout', methods=['POST'])
def logout():
    """ログアウトエンドポイント"""
    try:
        # トークンの取得
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'error': '認証トークンが必要です'
            }), HTTPStatus.UNAUTHORIZED
        
        token = auth_header.split(' ')[1]
        
        # ユースケースの実行
        usecase = UserLogoutUseCase(
            auth_service=current_app.auth_service
        )
        
        usecase.execute(LogoutRequest(token=token))
        
        return jsonify({
            'message': 'ログアウトに成功しました'
        }), HTTPStatus.OK
        
    except ValueError as e:
        return jsonify({'error': str(e)}), HTTPStatus.UNAUTHORIZED
    except Exception as e:
        current_app.logger.error(f"ログアウト中にエラーが発生しました: {str(e)}")
        return jsonify({
            'error': 'ログアウトに失敗しました'
        }), HTTPStatus.INTERNAL_SERVER_ERROR