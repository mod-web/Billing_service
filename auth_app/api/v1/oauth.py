from http import HTTPStatus

from flask import Blueprint, request, jsonify

from database.session_decorator import rate_limit
from services.tokens import create_access_and_refresh_tokens

oauth = Blueprint('oauth', __name__)


@oauth.route('/authorize/<string:service_name>', methods=['GET'])
@rate_limit()
def authorize(service_name):
    service = get_service_instance(service_name)
    return service.authorize()


@oauth.route('/redirect/<string:service_name>', methods=['GET'])
def redirect_oauth(service_name):
    code = request.args.get('code')
    service = get_service_instance(service_name)
    user_info = service.get_user_info(code)
    user = service.register(
        user_agent=request.headers.get('user-agent', ''),
        user_info=user_info,
    )
    access_token, refresh_token = create_access_and_refresh_tokens(
        identity=user['id'],
        payload=user,
    )
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user,
    }), HTTPStatus.OK
