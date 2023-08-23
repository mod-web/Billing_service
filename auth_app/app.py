import click
from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

from api.v1.auth import auth
from api.v1.oauth import oauth
from api.v1.roles import roles
from api.v1.users import users
from config import POSTGRES_CONN_STR, JWT_SECRET_KEY, JWT_ALGORITHM, JAEGER_TRACER_ENABLE
from flask_swagger_ui import get_swaggerui_blueprint

from services.user import UserService
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_CONN_STR

Swagger(app, template_file="swagger/openapi.yaml")
SQLAlchemy(app)

app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ALGORITHM'] = JWT_ALGORITHM
jwt = JWTManager(app)

BASE_SWAGGER_URL = '/apidocs/'
API_URL = '/swagger/openapi.yaml'
swagger_blueprint = get_swaggerui_blueprint(BASE_SWAGGER_URL, API_URL)


@click.command(name='create-superuser')
@click.argument('login')
@click.argument('password')
@click.argument('last_name')
@click.argument('first_name')
def create_superuser(
        login,
        password,
        last_name,
        first_name
):
    UserService().create_superuser(password, login, first_name, last_name)


app.register_blueprint(auth, url_prefix="/api/v1/auth")
app.register_blueprint(roles, url_prefix="/api/v1/roles")
app.register_blueprint(users, url_prefix="/api/v1/users")
app.register_blueprint(oauth, url_prefix="/api/v1/oauth")
app.register_blueprint(swagger_blueprint)
app.cli.add_command(create_superuser)


@app.route('/')
def get_status():
    return {'status': 'ok'}


if __name__ == '__main__':
    app.run()
    FlaskInstrumentor().instrument_app(app)
