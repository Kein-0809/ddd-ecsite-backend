from flask import Blueprint, jsonify, request, current_app
from http import HTTPStatus
from ...application.usecases.user_login import UserLoginUseCase, LoginRequest
from ...infrastructure.services.auth_service_impl import AuthServiceImpl

auth_routes = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_routes.route('/login', methods=['POST'])
def login():
    """ログインエンドポイント"""
    try:
        data = request.get_json()
        
        # ユースケースの実行
        usecase = UserLoginUseCase(
            auth_service=AuthServiceImpl(
                user_repository=request.app.container.user_repository()
            )
        )
        
        response = usecase.execute(
            LoginRequest(
                email=data['email'],
                password=data['password']
            )
        )
        
        return jsonify({
            'message': 'ログインに成功しました',
            'token': response.token.token,
            'user': {
                'id': response.user.id,
                'email': response.user.email.value,
                'name': response.user.name
            }
        }), HTTPStatus.OK
        
    except ValueError as e:
        return jsonify({'error': str(e)}), HTTPStatus.UNAUTHORIZED
    except Exception as e:
        current_app.logger.error(f"ログイン中にエラーが発生しました: {str(e)}")
        return jsonify({
            'error': 'ログインに失敗しました'
        }), HTTPStatus.INTERNAL_SERVER_ERROR