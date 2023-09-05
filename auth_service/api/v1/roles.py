from http import HTTPStatus

from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required

from services.role import role_service
from services.tokens import admin_access, validate_access_token

roles = Blueprint("roles", __name__)


@roles.errorhandler(404)
def handle_not_found(error):
    return make_response(jsonify({'error': 'Not found'}), HTTPStatus.NOT_FOUND)


@roles.errorhandler(409)
def handle_conflict(error):
    return make_response(jsonify({'error': 'Role already exists'}), HTTPStatus.NOT_FOUND)


@roles.route("/", methods=["GET"])
@jwt_required()
@admin_access()
@validate_access_token()
def roles_list():
    roles = role_service.get_all_roles()
    return roles, HTTPStatus.OK


@roles.route("/create", methods=["POST"])
@jwt_required()
@admin_access()
@validate_access_token()
def create_role():
    role_service.create_role(request.json.get('role'))
    return jsonify({"msg": "Created new role"}), HTTPStatus.CREATED


@roles.route("/<role_id>", methods=["PATCH"])
@jwt_required()
@admin_access()
@validate_access_token()
def update_role(role_id):
    new_role_name = request.json.get('role')
    role_service.update_role(role_id, new_role_name)
    return jsonify({"msg": "Updated role"}), HTTPStatus.CREATED


@roles.route("/<role_id>", methods=["DELETE"])
@jwt_required()
@admin_access()
@validate_access_token()
def delete_role(role_id):
    role_service.delete_role(role_id)
    return jsonify({"msg": "Deleted role"}), HTTPStatus.OK
