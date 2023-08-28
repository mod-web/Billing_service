import pytest
import requests
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from database.db import engine
from database.db_models import User, Roles, UsersRoles

HOST = 'http://auth_service:5000'
TEST_USER_ID = '81dae9f3-4251-429d-bd27-1f75bde74ae1'
TEST_LOGIN = 'test_login'
TEST_PASSWORD = 'test_password'
TEST_FIRST_NAME = 'test_first_name'
TEST_LAST_NAME = 'test_last_name'
TEST_ROLE_NAME = 'test_role'
TEST_ROLE_ID = '81dae9f3-4251-429d-bd27-1f75bde74ae4'


@pytest.fixture()
def delete_user_after_test():
    with Session(engine) as session:
        yield
        session.query(User).filter_by(login=TEST_LOGIN).delete()
        session.commit()


@pytest.fixture()
def create_and_delete_user():
    with Session(engine) as session:
        new_user = User(
            id=TEST_USER_ID,
            login=TEST_LOGIN,
            password=generate_password_hash(TEST_PASSWORD),
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )
        session.add(new_user)
        session.commit()
        yield session
        session.query(User).filter_by(id=TEST_USER_ID).delete()
        session.commit()


@pytest.fixture()
def get_tokens():
    with Session(engine) as session:
        new_user = User(
            id=TEST_USER_ID,
            login=TEST_LOGIN,
            password=generate_password_hash(TEST_PASSWORD),
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
        )
        session.add(new_user)
        session.commit()
        headers = {"Content-Type": "application/json; charset=utf-8"}
        login_url = f'{HOST}/api/v1/auth/login'
        data = {'login': TEST_LOGIN, 'password': TEST_PASSWORD}
        login = requests.post(url=login_url,
                              json=data,
                              headers=headers
                              )
        yield login.json()
        session.query(User).filter_by(id=TEST_USER_ID).delete()
        session.commit()


@pytest.fixture()
def get_tokens_for_admin():
    with Session(engine) as session:
        new_user = User(
            id=TEST_USER_ID,
            login=TEST_LOGIN,
            password=generate_password_hash(TEST_PASSWORD),
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            is_admin=True,
        )
        session.add(new_user)
        session.commit()
        headers = {"Content-Type": "application/json; charset=utf-8"}
        login_url = f'{HOST}/api/v1/auth/login'
        data = {'login': TEST_LOGIN, 'password': TEST_PASSWORD}
        login = requests.post(url=login_url,
                              json=data,
                              headers=headers
                              )
        yield login.json()
        session.query(User).filter_by(id=TEST_USER_ID).delete()
        session.query(Roles).filter_by(role=TEST_ROLE_NAME).delete()
        session.commit()


@pytest.fixture()
def create_role():
    with Session(engine) as session:
        new_role = Roles(
            id=TEST_ROLE_ID,
            role=TEST_ROLE_NAME,
        )
        session.add(new_role)
        session.commit()
        yield
        session.query(Roles).filter_by(id=TEST_ROLE_ID).delete()
        session.query(UsersRoles).filter_by(role_id=TEST_ROLE_ID).delete()
        session.commit()


@pytest.fixture()
def create_user_role():
    with Session(engine) as session:
        new_user_role = UsersRoles(
            user_id=TEST_USER_ID,
            role_id=TEST_ROLE_ID,
        )
        session.add(new_user_role)
        session.commit()
        yield
        session.query(UsersRoles).filter_by(role_id=TEST_ROLE_ID).delete()
        session.commit()
