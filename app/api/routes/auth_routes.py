from flask import Blueprint, jsonify, request, current_app
from http import HTTPStatus
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta
from ...infrastructure.database.models import UserModel
from ... import db

auth_routes = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_routes.route('/login', methods=['POST'])
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
        user = db.session.query(UserModel).filter_by(email=data['email']).first()
        
        # 認証チェック
        if not user or not check_password_hash(user.password_hash, data['password']):
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
                'email': user.email,
                'name': user.name
            }
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"ログイン中にエラーが発生しました: {str(e)}")
        return jsonify({
            'error': 'ログインに失敗しました'
        }), HTTPStatus.INTERNAL_SERVER_ERROR