from flask_jwt_extended import get_jwt, jwt_required
from http import HTTPStatus

from flask import Blueprint, request, jsonify, make_response

from services.tokens import create_access_and_refresh_tokens, RedisTokenStorage, validate_access_token
from services.user import user_service

auth = Blueprint("auth", __name__)


@auth.errorhandler(404)
def handle_not_found(error):
    return make_response(jsonify({'error': 'Not found'}), HTTPStatus.NOT_FOUND)


@auth.errorhandler(400)
def handle_bad_request(error):
    return make_response(jsonify({'error': 'User already exists'}), HTTPStatus.NOT_FOUND)


@auth.errorhandler(401)
def handle_invalid_creds_request(error):
    return make_response(jsonify({'error': 'Invalid credentials'}), HTTPStatus.NOT_FOUND)


@auth.route("/signup", methods=["POST"])
def create_user():
    new_user = user_service.register_user(
        login=request.json.get('login'),
        password=request.json.get('password'),
        last_name=request.json.get('last_name'),
        first_name=request.json.get('first_name'),
    )

    new_user['roles'] = user_service.get_roles_names_for_user(new_user['id'])
    access_token, refresh_token = create_access_and_refresh_tokens(
        identity=new_user['id'],
        payload=new_user,
    )
    response = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': new_user,
    }
    return jsonify(response), HTTPStatus.CREATED


@auth.route("/login", methods=["POST"])
def login_user():
    user = user_service.login_user(
        login=request.json.get('login'),
        password=request.json.get('password', None),
        user_agent=request.headers.get("user-agent", ""),
    )
    user['roles'] = user_service.get_roles_names_for_user(user['id'])
    access_token, refresh_token = create_access_and_refresh_tokens(
        identity=user['id'],
        payload=user,
    )
    response = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user,
    }
    return jsonify(response), HTTPStatus.OK


@auth.route("/logout", methods=["DELETE"])
@jwt_required()
@validate_access_token()
def logout():
    token = get_jwt()
    redis_storage = RedisTokenStorage()
    redis_storage.add_token_to_blacklist(token)
    return jsonify({'msg': 'token successfully revoked'}), HTTPStatus.OK


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_tokens():
    token = get_jwt()
    user_id = token.get('id')
    redis_storage = RedisTokenStorage()
    if redis_storage.check_token_in_blacklist(token) is None:
        user = user_service.get_user_by_id(user_id)
        user['roles'] = user_service.get_roles_names_for_user(user['id'])
        redis_storage.add_token_to_blacklist(token)
        access_token, refresh_token = create_access_and_refresh_tokens(
            identity=user_id,
            payload=user,
        )
        response = {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
        return jsonify(response), HTTPStatus.OK
    return jsonify({'msg': 'invalid token'}), HTTPStatus.UNAUTHORIZED
