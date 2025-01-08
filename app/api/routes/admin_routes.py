"""
管理者関連のルートハン�ラ
"""
from flask import Blueprint, jsonify, request, current_app
from http import HTTPStatus
from ...application.usecases.super_admin_registration import (
    SuperAdminRegistrationUseCase,
    SuperAdminRegistrationRequest
)
from ...application.usecases.super_admin_login import (
    SuperAdminLoginUseCase,
    SuperAdminLoginRequest
)
from ...domain.exceptions import (
    UserAlreadyExistsError,
    ValidationError,
    AuthenticationError,
    UnauthorizedError
)

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@bp.route('/super-admin/register', methods=['POST'])
def register_super_admin():
    """スーパー管理者登録エンドポイント"""
    try:
        data = request.get_json()
        
        # リクエストデータのバリデーション
        if not data or 'email' not in data or 'password' not in data or 'name' not in data:
            return jsonify({
                'error': '必須フィールドが不足しています'
            }), HTTPStatus.BAD_REQUEST

        # ユースケースの実行
        usecase = SuperAdminRegistrationUseCase(
            user_repository=current_app.container.user_repository(),
            email_service=current_app.container.email_service()
        )
        
        user = usecase.execute(
            SuperAdminRegistrationRequest(
                email=data['email'],
                password=data['password'],
                name=data['name']
            )
        )
        
        return jsonify({
            'message': 'スーパー管理者を登録しました',
            'user': {
                'id': user.id,
                'email': str(user.email),
                'name': user.name,
                'role': user.role.role_type.value,
                'is_active': user.is_active
            }
        }), HTTPStatus.CREATED
        
    except UserAlreadyExistsError as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.BAD_REQUEST
    except ValidationError as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.BAD_REQUEST
    except Exception as e:
        current_app.logger.error(f"スーパー管理者登録中にエラーが発生しました: {str(e)}")
        return jsonify({
            'error': '予期せぬエラーが発生しました'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/admin/register', methods=['POST'])
def register_admin():
    """管理者登録エンドポイント"""
    try:
        # 認証チェック
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '認証が必要です'}), HTTPStatus.UNAUTHORIZED
            
        token = auth_header.split(' ')[1]
        
        # スーパー管理者の認証
        current_user = current_app.auth_service.verify_token(token)
        
        if not current_user.is_super_admin():
            return jsonify({'error': '権限がありません'}), HTTPStatus.FORBIDDEN
        
        # 管理者登録
        data = request.get_json()
        usecase = AdminRegistrationUseCase(
            user_repository=current_app.container.user_repository()
        )
        
        user = usecase.execute(AdminRegistrationRequest(
            email=data['email'],
            password=data['password'],
            name=data['name']
        ))
        
        return jsonify({
            'message': '管理者を登録しました',
            'user': {
                'id': user.id,
                'email': user.email.value,
                'name': user.name,
                'role': user.role.role_type.value,
                'is_active': user.is_active
            }
        }), HTTPStatus.CREATED
        
    except ValueError as e:
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        current_app.logger.error(f"管理者登録中にエラーが発生しました: {str(e)}")
        return jsonify({'error': '予期せぬエラーが発生しました'}), HTTPStatus.INTERNAL_SERVER_ERROR 