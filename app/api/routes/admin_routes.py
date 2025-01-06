from flask import Blueprint, jsonify, request, current_app
from http import HTTPStatus
from ...application.usecases.super_admin_registration import (
    SuperAdminRegistrationUseCase,
    SuperAdminRegistrationRequest
)

admin_routes = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_routes.route('/super-admin/register', methods=['POST'])
def register_super_admin():
    """スーパー管理者登録エンドポイント"""
    try:
        data = request.get_json()
        
        # リクエストデータのバリデーション
        if not data or not all(k in data for k in ['email', 'password', 'name']):
            return jsonify({
                'error': '必須フィールドが不足しています'
            }), HTTPStatus.BAD_REQUEST

        # ユースケースの実行
        usecase = SuperAdminRegistrationUseCase(
            user_repository=current_app.user_repository
        )
        
        user = usecase.execute(
            SuperAdminRegistrationRequest(
                email=data['email'],
                password=data['password'],
                name=data['name']
            )
        )
        
        return jsonify({
            'message': 'スーパー管理者の登録が完了しました',
            'user': {
                'id': user.id,
                'email': user.email.value,
                'name': user.name,
                'role': user.role.role_type.value
            }
        }), HTTPStatus.CREATED
        
    except ValueError as e:
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        current_app.logger.error(f"スーパー管理者登録中にエラーが発生しました: {str(e)}")
        return jsonify({
            'error': 'スーパー管理者の登録に失敗しました'
        }), HTTPStatus.INTERNAL_SERVER_ERROR 