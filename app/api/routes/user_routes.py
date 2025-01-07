from flask import Blueprint, jsonify, request, current_app
from http import HTTPStatus
from ...application.usecases.user_registration import UserRegistrationUseCase

bp = Blueprint("user", __name__, url_prefix="/api/users")


@bp.route("/register", methods=["POST"])
def register():
    """ユーザー登録エンドポイント"""
    try:
        data = request.get_json()
        
        # ユースケースの実行
        usecase = UserRegistrationUseCase(
            user_repository=current_app.container.user_repository(),
            email_service=current_app.container.email_service(),
        )
        
        user = usecase.execute(
            email=data["email"],
            password=data["password"],
            name=data["name"],
        )

        return (
            jsonify({
                "message": "ユーザー登録が完了しました。確認メールをご確認ください。",
                "user": {
                    "id": user.id,
                    "email": user.email.value,
                    "name": user.name,
                }
            }),
            HTTPStatus.CREATED,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        current_app.logger.error(f"ユーザー登録中にエラーが発生しました: {str(e)}")
        return (
            jsonify({"error": "ユーザー登録に失敗しました"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        ) 