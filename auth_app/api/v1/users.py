from http import HTTPStatus

from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt

from services.role import role_service
from services.tokens import admin_access, validate_access_token
from services.user import user_service

users = Blueprint("users", __name__)


@users.errorhandler(404)
def handle_not_found(error):
    return make_response(jsonify({'error': 'Not found'}), HTTPStatus.NOT_FOUND)


@users.errorhandler(409)
def handle_conflict(error):
    return make_response(jsonify({'error': 'User already has this role'}), HTTPStatus.NOT_FOUND)


@users.errorhandler(401)
def handle_invalid_creds_request(error):
    return make_response(jsonify({'error': 'Invalid credentials'}), HTTPStatus.NOT_FOUND)


@users.route("/apply-role", methods=["POST"])
@admin_access()
@jwt_required()
@validate_access_token()
def apply_role_to_user():
    role_service.apply_user_role(
        user_id=request.json.get('user_id'),
        role_id=request.json.get('role_id'),
    )

    return jsonify({'msg': 'role created'}), HTTPStatus.OK


@users.route("/delete-role", methods=["DELETE"])
@admin_access()
@jwt_required()
@validate_access_token()
def delete_role_from_user():
    role_service.delete_user_role(
        user_id=request.json.get('user_id'),
        role_id=request.json.get('role_id'),
    )

    return jsonify({'msg': 'role deleted'}), HTTPStatus.OK


@users.route("/login-history", methods=["GET"])
@jwt_required()
@validate_access_token()
def get_login_history():
    page_size = request.args.get('page_size', default=10, type=int)
    page = request.args.get('page', default=1, type=int)
    token = get_jwt()
    user_id = token.get('id')
    return jsonify(
        {
            'page': page,
            'page_size': page_size,
            'data': [user_service.get_login_history(page=page, page_size=page_size, user_id=user_id)],
        }
    ), HTTPStatus.OK


@users.route("/change-password", methods=["POST"])
@jwt_required()
@validate_access_token()
def change_password():
    token = get_jwt()
    user_service.change_password(
        user_id=token.get('id'),
        old_password=request.json.get('old_password'),
        new_password=request.json.get('new_password'),
    )
    return jsonify({'msg': 'password updated'}), HTTPStatus.OK


@users.route("/change-login", methods=["POST"])
@jwt_required()
@validate_access_token()
def change_login():
    token = get_jwt()
    user_service.change_login(
        user_id=token.get('id'),
        new_login=request.json.get('new_login'),
        password=request.json.get('password'),
    )
    return jsonify({'msg': 'login updated'}), HTTPStatus.OK
