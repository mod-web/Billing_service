import requests

from tests.conftest import HOST, TEST_LOGIN, TEST_PASSWORD, TEST_LAST_NAME, TEST_FIRST_NAME


def test_sign_up(delete_user_after_test):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = f'{HOST}/api/v1/auth/signup'
    data = {'login': TEST_LOGIN, 'password': TEST_PASSWORD,
            'first_name': TEST_FIRST_NAME, 'last_name': TEST_LAST_NAME}
    response = requests.post(url=url,
                             json=data,
                             headers=headers
                             )
    assert response.status_code == 201


def test_login(create_and_delete_user):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    url = f'{HOST}/api/v1/auth/login'
    data = {'login': TEST_LOGIN, 'password': TEST_PASSWORD}
    response = requests.post(url=url,
                             json=data,
                             headers=headers
                             )
    assert response.status_code == 200


def test_logout(get_tokens):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens["access_token"]}',
    }
    url = f'{HOST}/api/v1/auth/logout'
    response = requests.delete(
        url=url,
        headers=headers
    )
    assert response.status_code == 200


def test_refresh(get_tokens):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {get_tokens["refresh_token"]}',
    }
    url = f'{HOST}/api/v1/auth/refresh'
    response = requests.post(
        url=url,
        headers=headers
    )
    assert response.status_code == 200
